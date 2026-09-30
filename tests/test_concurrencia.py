"""Task 3.3: concurrencia — una gana, un solo evento, sin doble reserva.

- Doble reprogramación simultánea de dos turnos al MISMO destino libre:
  una gana 200, la otra 409; el destino queda ocupado por un solo turno.
- Doble cancelar simultáneo del mismo turno: un 200 + un 409, un único
  HuecoLiberado.
DB en archivo (hilos con conexiones propias) + barrera de largada."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import threading
from datetime import datetime

import pytest

from c06.db import conectar, crear_schema
from c06 import servicio

AHORA = datetime.fromisoformat("2026-10-18T10:00:00-03:00")
DEST = "2026-10-21T10:00:00-03:00"


def _insertar(con: sqlite3.Connection, id_: str, token: str, inicio: str,
              fin: str) -> None:
    con.execute(
        """INSERT INTO turnos (id, profesional_id, sillon_id, prestacion_id,
            paciente_nombre, paciente_telefono, inicio, fin, estado, origen,
            token_publico, token_expira_en)
           VALUES (?, 'prof-demo-1', 'sillon-demo-1', 'prest-limpieza-30',
            'Paciente Demo', '+549110000003', ?, ?, 'reservado', 'online',
            ?, '2026-10-22T10:00:00-03:00')""",
        (id_, inicio, fin, token))
    con.commit()


@pytest.fixture()
def db_path() -> str:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = conectar(path)
    crear_schema(con)
    yield path
    con.close()
    os.unlink(path)


def _carreras(fn, n: int = 2) -> list:
    barrera = threading.Barrier(n)
    resultados: list = [None] * n

    def _correr(i: int) -> None:
        barrera.wait()
        resultados[i] = fn(i)

    hilos = [threading.Thread(target=_correr, args=(i,)) for i in range(n)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    return resultados


def test_doble_reprogramacion_mismo_destino_una_gana(db_path: str) -> None:
    base = conectar(db_path)
    crear_schema(base)
    _insertar(base, "t-conc-a", "tok-conc-a",
              "2026-10-20T10:00:00-03:00", "2026-10-20T10:30:00-03:00")
    _insertar(base, "t-conc-b", "tok-conc-b",
              "2026-10-20T11:00:00-03:00", "2026-10-20T11:30:00-03:00")
    base.close()

    def _op(i: int) -> tuple[int, dict]:
        con = conectar(db_path)
        crear_schema(con)
        token = "tok-conc-a" if i == 0 else "tok-conc-b"
        try:
            return servicio.reprogramar_por_token(con, token, DEST, AHORA)
        finally:
            con.close()

    resultados = _carreras(_op)
    assert sorted(s[0] for s in resultados) == [200, 409]
    check = conectar(db_path)
    en_dest = check.execute("SELECT id FROM turnos WHERE inicio=? AND"
                            " estado IN ('reservado','confirmado')",
                            (DEST,)).fetchall()
    assert len(en_dest) == 1
    n = check.execute("SELECT COUNT(*) c FROM eventos_outbox WHERE"
                      " tipo='TurnoReprogramado'").fetchone()["c"]
    assert n == 1
    check.close()


def test_doble_cancelar_un_solo_evento(db_path: str) -> None:
    base = conectar(db_path)
    crear_schema(base)
    _insertar(base, "t-conc-c", "tok-conc-c",
              "2026-10-20T10:00:00-03:00", "2026-10-20T10:30:00-03:00")
    base.close()

    def _op(i: int) -> tuple[int, dict]:
        del i
        con = conectar(db_path)
        crear_schema(con)
        try:
            return servicio.cancelar_por_token(con, "tok-conc-c", AHORA)
        finally:
            con.close()

    resultados = _carreras(_op)
    assert sorted(s[0] for s in resultados) == [200, 409]
    check = conectar(db_path)
    n = check.execute("SELECT COUNT(*) c FROM eventos_outbox WHERE"
                      " tipo='HuecoLiberado' AND turno_id='t-conc-c'"
                      ).fetchone()["c"]
    assert n == 1
    check.close()
