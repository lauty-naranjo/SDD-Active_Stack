"""Task 4.3 (RED primero): cambios publicados como seam hacia GCal (C-11).

- Sin ninguna credencial GCal en el entorno, confirmar/cancelar/reprogramar
  responden 200 y publican TurnoConfirmado/TurnoCancelado/TurnoReprogramado
  con payload completo (incl. estado resultante).
Rojo esperado: TurnoConfirmado aún no incluye 'estado' en el payload."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

import pytest

from c06.db import conectar, crear_schema
from c06 import servicio

AHORA = datetime.fromisoformat("2026-10-18T10:00:00-03:00")


def _insertar(con: sqlite3.Connection, id_: str, token: str) -> None:
    con.execute(
        """INSERT INTO turnos (id, profesional_id, sillon_id, prestacion_id,
            paciente_nombre, paciente_telefono, inicio, fin, estado, origen,
            token_publico, token_expira_en)
           VALUES (?, 'prof-demo-1', 'sillon-demo-1', 'prest-limpieza-30',
            'Pedro Demo', '+549110000006',
            '2026-10-20T10:00:00-03:00', '2026-10-20T10:30:00-03:00',
            'reservado', 'online', ?, '2026-10-22T10:00:00-03:00')""",
        (id_, token))
    con.commit()


def _sin_gcal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GCAL_CLIENT_ID", raising=False)
    monkeypatch.delenv("GCAL_CLIENT_SECRET", raising=False)
    assert "GCAL_CLIENT_ID" not in dir(__import__("os").environ)


def _payload(con: sqlite3.Connection, tipo: str) -> dict:
    fila = con.execute("SELECT payload FROM eventos_outbox WHERE tipo=?",
                       (tipo,)).fetchone()
    assert fila is not None, f"falta evento {tipo}"
    return json.loads(fila["payload"])


@pytest.fixture()
def db() -> sqlite3.Connection:
    con = conectar()
    crear_schema(con)
    yield con
    con.close()


def test_confirmar_publica_evento_sin_gcal(db: sqlite3.Connection,
                                           monkeypatch) -> None:
    _sin_gcal(monkeypatch)
    _insertar(db, "t-gcal-1", "tok-gcal-1")
    assert servicio.confirmar_por_token(db, "tok-gcal-1", AHORA)[0] == 200
    payload = _payload(db, "TurnoConfirmado")
    assert payload["turno_id"] == "t-gcal-1"
    assert payload["profesional_id"] == "prof-demo-1"
    assert payload["sillon_id"] == "sillon-demo-1"
    assert payload["inicio"] == "2026-10-20T10:00:00-03:00"
    assert payload["fin"] == "2026-10-20T10:30:00-03:00"
    assert payload["estado"] == "confirmado"


def test_cancelar_publica_evento_sin_gcal(db: sqlite3.Connection,
                                          monkeypatch) -> None:
    _sin_gcal(monkeypatch)
    _insertar(db, "t-gcal-2", "tok-gcal-2")
    assert servicio.cancelar_por_token(db, "tok-gcal-2", AHORA)[0] == 200
    payload = _payload(db, "TurnoCancelado")
    assert (payload["turno_id"], payload["estado"]) == \
        ("t-gcal-2", "cancelado")


def test_reprogramar_publica_evento_sin_gcal(db: sqlite3.Connection,
                                             monkeypatch) -> None:
    _sin_gcal(monkeypatch)
    _insertar(db, "t-gcal-3", "tok-gcal-3")
    status, _ = servicio.reprogramar_por_token(db, "tok-gcal-3",
                                               "2026-10-21T10:00:00-03:00",
                                               AHORA)
    assert status == 200
    payload = _payload(db, "TurnoReprogramado")
    assert payload["origen_inicio"] == "2026-10-20T10:00:00-03:00"
    assert payload["inicio"] == "2026-10-21T10:00:00-03:00"
    assert payload["estado"] == "reservado"
