"""C-06 gestion-ventana-24h — stub de interfaz (task 1.1).

Fija los supuestos de C-03/C-04/C-05 como interfaz mínima, greenfield:
- Turno { id, profesional_id, sillon_id, prestacion_id, paciente (ficticio),
  inicio, fin, estado, origen, token_publico UNIQUE, token_expira_en }
- Anti-solapamiento C-04: delegado en servicio.reprogramar (rango semiabierto '[)');
  este módulo solo crea la tabla turnos + índice (estado) + tabla bloqueos.
- Transiciones de estado (task 1.3): CHECK + trigger; el stub 1.1 NO los trae
  (el test 1.2 debe fallar en rojo contra este stub).

Decisiones de supuestos registradas en design.md (Contexto + OQ-1..OQ-3)."""

from __future__ import annotations

import sqlite3

SCHEMA_STUB = """
CREATE TABLE IF NOT EXISTS turnos (
  id TEXT PRIMARY KEY,
  profesional_id TEXT NOT NULL,
  sillon_id TEXT NOT NULL,
  prestacion_id TEXT NOT NULL,
  paciente_nombre TEXT NOT NULL,
  paciente_telefono TEXT NOT NULL,
  inicio TEXT NOT NULL,
  fin TEXT NOT NULL,
  estado TEXT NOT NULL,
  origen TEXT NOT NULL,
  token_publico TEXT UNIQUE NOT NULL,
  token_expira_en TEXT,
  CHECK (estado IN ('pendiente_sena', 'reservado', 'confirmado',
                    'cancelado', 'ausente', 'atendido'))
);
CREATE INDEX IF NOT EXISTS idx_turnos_estado ON turnos(estado);
CREATE TABLE IF NOT EXISTS bloqueos (
  id TEXT PRIMARY KEY,
  profesional_id TEXT,
  sillon_id TEXT,
  inicio TEXT NOT NULL,
  fin TEXT NOT NULL,
  motivo TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS eventos_outbox (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo TEXT NOT NULL,
  turno_id TEXT NOT NULL,
  operacion TEXT NOT NULL,
  payload TEXT NOT NULL,
  creado_en TEXT NOT NULL,
  UNIQUE (turno_id, operacion)
);
"""


def conectar(db_path: str = ":memory:") -> sqlite3.Connection:
    con = sqlite3.connect(db_path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def crear_schema(con: sqlite3.Connection) -> None:
    con.executescript(SCHEMA_STUB)
    con.executescript(DDL_TRANSICIONES)
    con.commit()


# Task 1.3 (D4, R3): máquina de estados impuesta en DB. Válidas:
# pendiente_sena→reservado (C-05/C-07, referenciada), reservado→confirmado,
# reservado→cancelado, confirmado→cancelado|atendido|ausente.
# Cualquier otra transición aborta con IntegrityError (RAISE(ABORT)).
DDL_TRANSICIONES = """
CREATE TRIGGER IF NOT EXISTS trg_turno_transicion
BEFORE UPDATE OF estado ON turnos
FOR EACH ROW WHEN (OLD.estado <> NEW.estado)
BEGIN
  SELECT CASE
    WHEN OLD.estado = 'pendiente_sena' AND NEW.estado = 'reservado' THEN NULL
    WHEN OLD.estado = 'reservado'
         AND NEW.estado IN ('confirmado', 'cancelado') THEN NULL
    WHEN OLD.estado = 'confirmado'
         AND NEW.estado IN ('cancelado', 'atendido', 'ausente') THEN NULL
    ELSE RAISE(ABORT, 'transicion de estado invalida')
  END;
END;
"""
