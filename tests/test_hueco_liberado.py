"""Task 2.3 (RED primero): cancelación válida emite un único HuecoLiberado
con payload completo y libera [inicio, fin) (D1, seam C-09).

Literales del spec: inicio 2026-10-20T10:00-03:00, fin 2026-10-20T10:30-03:00.
El helper hueco_ocupado() aún no existe → rojo esperado."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

import pytest

from c06.db import conectar, crear_schema
from c06 import servicio

INICIO = "2026-10-20T10:00:00-03:00"
FIN = "2026-10-20T10:30:00-03:00"
AHORA = datetime.fromisoformat("2026-10-18T10:00:00-03:00")  # 48h antes


def _insertar(con: sqlite3.Connection) -> None:
    con.execute(
        """INSERT INTO turnos (id, profesional_id, sillon_id, prestacion_id,
            paciente_nombre, paciente_telefono, inicio, fin, estado, origen,
            token_publico, token_expira_en)
           VALUES ('t-hueco-1', 'prof-demo-1', 'sillon-demo-1',
            'prest-limpieza-30', 'Juan Pérez Demo', '+549110000002',
            ?, ?, 'reservado', 'online',
            'tok-demo-hueco', '2026-10-21T10:00:00-03:00')""", (INICIO, FIN))
    con.commit()


@pytest.fixture()
def db() -> sqlite3.Connection:
    con = conectar()
    crear_schema(con)
    yield con
    con.close()


def test_cancelacion_emite_unico_hueco_liberado(db: sqlite3.Connection) -> None:
    _insertar(db)
    status, _ = servicio.cancelar_por_token(db, "tok-demo-hueco", AHORA)
    assert status == 200
    filas = db.execute(
        "SELECT tipo, payload FROM eventos_outbox WHERE tipo='HuecoLiberado'"
    ).fetchall()
    assert len(filas) == 1
    payload = json.loads(filas[0]["payload"])
    assert payload["turno_id"] == "t-hueco-1"
    assert payload["profesional_id"] == "prof-demo-1"
    assert payload["sillon_id"] == "sillon-demo-1"
    assert payload["inicio"] == "2026-10-20T10:00:00-03:00"
    assert payload["fin"] == "2026-10-20T10:30:00-03:00"


def test_reintento_no_duplica_evento(db: sqlite3.Connection) -> None:
    _insertar(db)
    assert servicio.cancelar_por_token(db, "tok-demo-hueco", AHORA)[0] == 200
    status, _ = servicio.cancelar_por_token(db, "tok-demo-hueco", AHORA)
    assert status == 409
    n = db.execute("SELECT COUNT(*) c FROM eventos_outbox WHERE"
                   " tipo='HuecoLiberado'").fetchone()["c"]
    assert n == 1


def test_hueco_queda_disponible(db: sqlite3.Connection) -> None:
    _insertar(db)
    assert servicio.hueco_ocupado(db, "prof-demo-1", "sillon-demo-1",
                                  INICIO, FIN) is True
    assert servicio.cancelar_por_token(db, "tok-demo-hueco", AHORA)[0] == 200
    assert servicio.hueco_ocupado(db, "prof-demo-1", "sillon-demo-1",
                                  INICIO, FIN) is False
