"""Task 4.1 (RED primero): endpoints staff con RBAC.

- Rol sin permiso (paciente) → 403 en confirmar/cancelar/reprogramar/
  marcar-atendido/marcar-ausente por id.
- Staff respeta la misma ventana RN-TUR-01 (cancelar <24h → 409).
- ausente ≠ cancelado: marcar-ausente deja 'ausente', distinguible de
  'cancelado' (RN-REP-02); marcar-atendido/ausente solo staff.
Funciones *_por_id aún no existen → rojo esperado."""

from __future__ import annotations

import sqlite3
from datetime import datetime

import pytest

from c06.db import conectar, crear_schema
from c06 import servicio

AHORA_LEJOS = datetime.fromisoformat("2026-10-13T10:00:00-03:00")
AHORA_CERCA = datetime.fromisoformat("2026-10-14T12:00:00-03:00")


def _insertar(con: sqlite3.Connection, id_: str = "t-staff-1",
              estado: str = "reservado") -> None:
    con.execute(
        """INSERT INTO turnos (id, profesional_id, sillon_id, prestacion_id,
            paciente_nombre, paciente_telefono, inicio, fin, estado, origen,
            token_publico, token_expira_en)
           VALUES (?, 'prof-demo-1', 'sillon-demo-1', 'prest-limpieza-30',
            'Ana Demo', '+549110000004',
            '2026-10-15T10:00:00-03:00', '2026-10-15T10:30:00-03:00', ?,
            'mostrador', ?, '2026-10-16T10:00:00-03:00')""",
        (id_, estado, f"tok-{id_}"))
    con.commit()


@pytest.fixture()
def db() -> sqlite3.Connection:
    con = conectar()
    crear_schema(con)
    yield con
    con.close()


def test_staff_sin_permiso_403(db: sqlite3.Connection) -> None:
    _insertar(db)
    assert servicio.confirmar_por_id(db, "t-staff-1", "paciente",
                                     AHORA_LEJOS)[0] == 403
    assert servicio.cancelar_por_id(db, "t-staff-1", "paciente",
                                    AHORA_LEJOS)[0] == 403
    assert servicio.reprogramar_por_id(
        db, "t-staff-1", "paciente",
        "2026-10-21T10:00:00-03:00", AHORA_LEJOS)[0] == 403
    assert servicio.marcar_ausente_por_id(db, "t-staff-1", "paciente",
                                          AHORA_LEJOS)[0] == 403


def test_staff_respeta_ventana(db: sqlite3.Connection) -> None:
    _insertar(db)
    status, body = servicio.cancelar_por_id(db, "t-staff-1", "recepcionista",
                                            AHORA_CERCA)
    assert status == 409
    assert "contacto" in body
    fila = db.execute("SELECT estado FROM turnos WHERE id='t-staff-1'"
                      ).fetchone()
    assert fila["estado"] == "reservado"


def test_ausente_distinto_de_cancelado(db: sqlite3.Connection) -> None:
    _insertar(db, "t-aus", "confirmado")
    _insertar(db, "t-can", "reservado")
    assert servicio.marcar_ausente_por_id(db, "t-aus", "dueño",
                                          AHORA_LEJOS)[0] == 200
    assert servicio.cancelar_por_id(db, "t-can", "recepcionista",
                                    AHORA_LEJOS)[0] == 200
    estados = dict(db.execute("SELECT id, estado FROM turnos WHERE id IN"
                              " ('t-aus','t-can')").fetchall())
    assert estados == {"t-aus": "ausente", "t-can": "cancelado"}


def test_marcar_atendido_solo_staff(db: sqlite3.Connection) -> None:
    _insertar(db, "t-ate", "confirmado")
    assert servicio.marcar_atendido_por_id(db, "t-ate", "paciente",
                                           AHORA_LEJOS)[0] == 403
    assert servicio.marcar_atendido_por_id(db, "t-ate", "recepcionista",
                                           AHORA_LEJOS)[0] == 200
    fila = db.execute("SELECT estado FROM turnos WHERE id='t-ate'").fetchone()
    assert fila["estado"] == "atendido"
