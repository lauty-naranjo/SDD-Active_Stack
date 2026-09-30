"""Task 3.1 (RED primero): reprogramación atómica (D3).

- Feliz: mismo id, fin re-derivado, estado reservado, HuecoLiberado(origen).
- Adyacencia: destino [10:00,10:30) con vecino [10:30,11:00) → ACEPTA.
- Destino con intersección real → 409 + sugerencia espera, origen intacto,
  sin eventos.
Literales del spec. `reprogramar_por_token` aún no existe → rojo esperado."""

from __future__ import annotations

import sqlite3
from datetime import datetime

import pytest

from c06.db import conectar, crear_schema
from c06 import servicio

ORIG_INICIO = "2026-10-20T10:00:00-03:00"
ORIG_FIN = "2026-10-20T10:30:00-03:00"
DEST_INICIO = "2026-10-21T10:00:00-03:00"
DEST_FIN = "2026-10-21T10:30:00-03:00"
AHORA = datetime.fromisoformat("2026-10-18T10:00:00-03:00")


def _insertar(con: sqlite3.Connection, id_: str, token: str, inicio: str,
              fin: str, estado: str = "reservado") -> None:
    con.execute(
        """INSERT INTO turnos (id, profesional_id, sillon_id, prestacion_id,
            paciente_nombre, paciente_telefono, inicio, fin, estado, origen,
            token_publico, token_expira_en)
           VALUES (?, 'prof-demo-1', 'sillon-demo-1', 'prest-limpieza-30',
            'María Demo', '+549110000001', ?, ?, ?, 'online',
            ?, '2026-10-22T10:00:00-03:00')""",
        (id_, inicio, fin, estado, token))
    con.commit()


@pytest.fixture()
def db() -> sqlite3.Connection:
    con = conectar()
    crear_schema(con)
    yield con
    con.close()


def test_reprogramacion_feliz(db: sqlite3.Connection) -> None:
    _insertar(db, "t-repro-1", "tok-repro-1", ORIG_INICIO, ORIG_FIN)
    status, body = servicio.reprogramar_por_token(db, "tok-repro-1",
                                                  DEST_INICIO, AHORA)
    assert status == 200
    fila = db.execute("SELECT id, inicio, fin, estado FROM turnos"
                      " WHERE id='t-repro-1'").fetchone()
    assert (fila["id"], fila["inicio"], fila["fin"], fila["estado"]) == \
        ("t-repro-1", DEST_INICIO, DEST_FIN, "reservado")
    assert body["estado"] == "reservado"
    n = db.execute("SELECT COUNT(*) c FROM eventos_outbox WHERE"
                   " tipo='HuecoLiberado'").fetchone()["c"]
    assert n == 1


def test_adyacencia_fin_igual_inicio_acepta(db: sqlite3.Connection) -> None:
    _insertar(db, "t-vecino", "tok-vecino",
              "2026-10-21T10:30:00-03:00", "2026-10-21T11:00:00-03:00")
    _insertar(db, "t-repro-2", "tok-repro-2", ORIG_INICIO, ORIG_FIN)
    status, _ = servicio.reprogramar_por_token(db, "tok-repro-2",
                                               DEST_INICIO, AHORA)
    assert status == 200
    fila = db.execute("SELECT inicio, fin FROM turnos WHERE id='t-repro-2'"
                      ).fetchone()
    assert (fila["inicio"], fila["fin"]) == (DEST_INICIO, DEST_FIN)


def test_destino_ocupado_rechaza_sin_mutar(db: sqlite3.Connection) -> None:
    _insertar(db, "t-ocupante", "tok-ocupante",
              "2026-10-21T10:15:00-03:00", "2026-10-21T10:45:00-03:00")
    _insertar(db, "t-repro-3", "tok-repro-3", ORIG_INICIO, ORIG_FIN)
    status, body = servicio.reprogramar_por_token(db, "tok-repro-3",
                                                  DEST_INICIO, AHORA)
    assert status == 409
    assert "espera" in body["error"].lower()
    fila = db.execute("SELECT inicio, fin, estado FROM turnos"
                      " WHERE id='t-repro-3'").fetchone()
    assert (fila["inicio"], fila["fin"], fila["estado"]) == \
        (ORIG_INICIO, ORIG_FIN, "reservado")
    n = db.execute("SELECT COUNT(*) c FROM eventos_outbox").fetchone()["c"]
    assert n == 0
