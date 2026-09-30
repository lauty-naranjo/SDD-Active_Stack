"""Cobertura 2.2 restante (verificación): token 404/410 y confirmar
siempre permitida aun dentro de ventana (<24h)."""

from __future__ import annotations

import sqlite3
from datetime import datetime

import pytest

from c06.db import conectar, crear_schema
from c06 import servicio

INICIO = "2026-10-15T10:00:00-03:00"
FIN = "2026-10-15T10:30:00-03:00"


def _insertar(con: sqlite3.Connection, token: str,
              expira: str | None) -> None:
    con.execute(
        """INSERT INTO turnos (id, profesional_id, sillon_id, prestacion_id,
            paciente_nombre, paciente_telefono, inicio, fin, estado, origen,
            token_publico, token_expira_en)
           VALUES ('t-tok', 'prof-demo-1', 'sillon-demo-1',
            'prest-limpieza-30', 'Lucía Demo', '+549110000007', ?, ?,
            'reservado', 'online', ?, ?)""", (INICIO, FIN, token, expira))
    con.commit()


@pytest.fixture()
def db() -> sqlite3.Connection:
    con = conectar()
    crear_schema(con)
    yield con
    con.close()


def test_token_inexistente_404(db: sqlite3.Connection) -> None:
    ahora = datetime.fromisoformat("2026-10-13T10:00:00-03:00")
    assert servicio.cancelar_por_token(db, "tok-no-existe", ahora)[0] == 404
    assert servicio.confirmar_por_token(db, "tok-no-existe", ahora)[0] == 404


def test_token_expirado_410(db: sqlite3.Connection) -> None:
    _insertar(db, "tok-exp", "2026-10-13T10:00:00-03:00")
    ahora = datetime.fromisoformat("2026-10-14T09:00:00-03:00")
    assert servicio.cancelar_por_token(db, "tok-exp", ahora)[0] == 410
    assert servicio.confirmar_por_token(db, "tok-exp", ahora)[0] == 410


def test_confirmar_dentro_de_ventana_acepta(db: sqlite3.Connection) -> None:
    _insertar(db, "tok-cf", "2026-10-16T10:00:00-03:00")
    ahora = datetime.fromisoformat("2026-10-14T12:00:00-03:00")  # 22h < 24h
    status, body = servicio.confirmar_por_token(db, "tok-cf", ahora)
    assert status == 200
    assert body["estado"] == "confirmado"
