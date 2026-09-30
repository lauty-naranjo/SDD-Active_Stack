"""Task 1.2 (RED primero): transición inválida rechazada a nivel DB (R3).

Fixture ficticio (R1): 'María Demo', teléfono ficticio. Sin secretos (R2).
Valores esperados = literales del spec (R5), no recálculo del código."""

from __future__ import annotations

import sqlite3

import pytest

from c06.db import conectar, crear_schema

TURNO_FICTICIO = {
    "id": "t-001",
    "profesional_id": "prof-demo-1",
    "sillon_id": "sillon-demo-1",
    "prestacion_id": "prest-limpieza-30",
    "paciente_nombre": "María Demo",
    "paciente_telefono": "+549110000001",
    "inicio": "2026-10-15T10:00:00-03:00",
    "fin": "2026-10-15T10:30:00-03:00",
    "origen": "online",
    "token_publico": "tok-demo-001",
    "token_expira_en": "2026-10-14T10:00:00-03:00",
}


def _insertar(con: sqlite3.Connection, estado: str, id_: str = "t-001",
              token: str = "tok-demo-001") -> None:
    d = dict(TURNO_FICTICIO, estado=estado, id=id_, token_publico=token)
    con.execute(
        """INSERT INTO turnos (id, profesional_id, sillon_id, prestacion_id,
            paciente_nombre, paciente_telefono, inicio, fin, estado, origen,
            token_publico, token_expira_en)
           VALUES (:id, :profesional_id, :sillon_id, :prestacion_id,
            :paciente_nombre, :paciente_telefono, :inicio, :fin, :estado,
            :origen, :token_publico, :token_expira_en)""", d)
    con.commit()


@pytest.fixture()
def db() -> sqlite3.Connection:
    con = conectar()
    crear_schema(con)
    yield con
    con.close()


def test_db_rechaza_cancelado_a_confirmado(db: sqlite3.Connection) -> None:
    """cancelado → confirmado: UPDATE directo debe fallar en DB (R3)."""
    _insertar(db, "cancelado")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE turnos SET estado='confirmado' WHERE id='t-001'")
        db.commit()
    fila = db.execute("SELECT estado FROM turnos WHERE id='t-001'").fetchone()
    assert fila["estado"] == "cancelado"


def test_db_rechaza_atendido_a_cancelado(db: sqlite3.Connection) -> None:
    """atendido → cancelado: UPDATE directo debe fallar en DB (R3)."""
    _insertar(db, "atendido")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE turnos SET estado='cancelado' WHERE id='t-001'")
        db.commit()
    fila = db.execute("SELECT estado FROM turnos WHERE id='t-001'").fetchone()
    assert fila["estado"] == "atendido"


def test_db_permite_reservado_a_confirmado(db: sqlite3.Connection) -> None:
    """Control: reservado → confirmado es válida y pasa."""
    _insertar(db, "reservado")
    db.execute("UPDATE turnos SET estado='confirmado' WHERE id='t-001'")
    db.commit()
    fila = db.execute("SELECT estado FROM turnos WHERE id='t-001'").fetchone()
    assert fila["estado"] == "confirmado"
