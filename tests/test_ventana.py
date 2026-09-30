"""Task 2.1 (RED primero): ventana 24h con literales del spec (R4/R5).

inicio = 2026-10-15T10:00:00-03:00 en todos los casos:
- ahora = 2026-10-14T09:59 → 24h01 ≥ 24h → ACEPTA
- ahora = 2026-10-14T10:01 → 23h59 < 24h → RECHAZA 409 + contacto, sin mutar
- ahora = 2026-10-14T10:00 → exactamente 24h00 → ACEPTA
- reprogramar con ahora = 2026-10-14T12:00 (22h) → RECHAZA, origen intacto
Fixture ficticio (R1). Sin secretos (R2)."""

from __future__ import annotations

import sqlite3
from datetime import datetime

import pytest

from c06.db import conectar, crear_schema
from c06 import servicio

INICIO = "2026-10-15T10:00:00-03:00"
FIN = "2026-10-15T10:30:00-03:00"


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _insertar_reservado(con: sqlite3.Connection, token: str = "tok-demo-001",
                        id_: str = "t-001") -> None:
    con.execute(
        """INSERT INTO turnos (id, profesional_id, sillon_id, prestacion_id,
            paciente_nombre, paciente_telefono, inicio, fin, estado, origen,
            token_publico, token_expira_en)
           VALUES (?, 'prof-demo-1', 'sillon-demo-1', 'prest-limpieza-30',
            'María Demo', '+549110000001', ?, ?, 'reservado', 'online',
            ?, '2026-10-16T10:00:00-03:00')""", (id_, INICIO, FIN, token))
    con.commit()


def _estado(con: sqlite3.Connection, id_: str = "t-001") -> str:
    return con.execute("SELECT estado FROM turnos WHERE id = ?",
                       (id_,)).fetchone()["estado"]


@pytest.fixture()
def db() -> sqlite3.Connection:
    con = conectar()
    crear_schema(con)
    yield con
    con.close()


def test_cancelar_24h01_acepta(db: sqlite3.Connection) -> None:
    _insertar_reservado(db)
    status, body = servicio.cancelar_por_token(db, "tok-demo-001",
                                               _dt("2026-10-14T09:59:00-03:00"))
    assert status == 200
    assert body["estado"] == "cancelado"
    assert _estado(db) == "cancelado"


def test_cancelar_23h59_rechaza_con_contacto(db: sqlite3.Connection) -> None:
    _insertar_reservado(db)
    status, body = servicio.cancelar_por_token(db, "tok-demo-001",
                                               _dt("2026-10-14T10:01:00-03:00"))
    assert status == 409
    assert "24 horas" in body["error"]
    assert "contacto" in body
    assert _estado(db) == "reservado"
    n = db.execute("SELECT COUNT(*) c FROM eventos_outbox").fetchone()["c"]
    assert n == 0


def test_cancelar_24h00_exactas_acepta(db: sqlite3.Connection) -> None:
    _insertar_reservado(db)
    status, _ = servicio.cancelar_por_token(db, "tok-demo-001",
                                            _dt("2026-10-14T10:00:00-03:00"))
    assert status == 200
    assert _estado(db) == "cancelado"


def test_reprogramar_dentro_de_ventana_rechaza(db: sqlite3.Connection) -> None:
    _insertar_reservado(db)
    status, body = servicio.reprogramar_por_token(
        db, "tok-demo-001", "2026-10-21T10:00:00-03:00",
        _dt("2026-10-14T12:00:00-03:00"))
    assert status == 409
    fila = db.execute("SELECT inicio, fin, estado FROM turnos WHERE id='t-001'"
                      ).fetchone()
    assert (fila["inicio"], fila["fin"], fila["estado"]) == \
        (INICIO, FIN, "reservado")
