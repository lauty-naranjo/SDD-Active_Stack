"""C-06 servicio: confirmar/cancelar por token (D2, D5).

- Reloj servidor inyectado (`ahora`); 404 token inexistente, 410 expirado.
- Cancelar exige ventana >= 24h; rechazo 409 + mensaje + contacto (OQ-2/OQ-3:
  409 y APP_CONTACTO provisorios). Confirmar siempre permitida.
- Transición inválida → 409. El trigger DB (task 1.3) es la red de seguridad;
  el servicio usa UPDATE condicional (race-safe, task 3.3).
- Cancelación válida emite HuecoLiberado (D1, seam C-09).
- Cambios aceptados emiten TurnoConfirmado/TurnoCancelado (seam C-11, 4.3).
- Sin credenciales GCal: el flujo sigue 200 (este módulo no toca GCal).
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Any

from c06.ventana import ahora_servidor, ventana_ok

CONTACTO = os.environ.get("APP_CONTACTO", "+54 11 0000 0000 (consultorio demo)")
MENSAJE_VENTANA = (
    "Ya estás dentro de las 24 horas previas al turno y no es posible "
    "cancelar ni reprogramar por este medio. Comunicate con el consultorio:"
)

ESTADOS_CANCELABLES = ("reservado", "confirmado")
ESTADOS_VIGENTES = ("pendiente_sena", "reservado", "confirmado")


def hueco_ocupado(con: sqlite3.Connection, profesional_id: str,
                  sillon_id: str, inicio: str, fin: str,
                  excluir_turno: str | None = None) -> bool:
    """True si algún turno vigente del mismo profesional o sillón intersecta
    [inicio, fin) con semántica semiabierta (fin == inicio vecino NO solapa,
    RN-AGEN-01). Los cancelados/ausentes/atendidos no ocupan."""
    sql = """SELECT 1 FROM turnos
             WHERE estado IN ('pendiente_sena','reservado','confirmado')
               AND (profesional_id = ? OR sillon_id = ?)
               AND inicio < ? AND ? < fin"""
    args: list[Any] = [profesional_id, sillon_id, fin, inicio]
    if excluir_turno is not None:
        sql += " AND id <> ?"
        args.append(excluir_turno)
    return con.execute(sql, args).fetchone() is not None


def _fila_por_token(con: sqlite3.Connection, token: str) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM turnos WHERE token_publico = ?",
                       (token,)).fetchone()


def _expirado(fila: sqlite3.Row, ahora: datetime) -> bool:
    exp = fila["token_expira_en"]
    if exp is None:
        return False
    return ahora > datetime.fromisoformat(exp)


def _emitir(con: sqlite3.Connection, tipo: str, fila: sqlite3.Row,
            ahora: datetime, extra: dict[str, Any] | None = None) -> None:
    payload = {"turno_id": fila["id"],
               "profesional_id": fila["profesional_id"],
               "sillon_id": fila["sillon_id"],
               "inicio": fila["inicio"], "fin": fila["fin"],
               "liberado_en": ahora.isoformat(),
               **(extra or {})}
    con.execute(
        """INSERT OR IGNORE INTO eventos_outbox
           (tipo, turno_id, operacion, payload, creado_en)
           VALUES (?, ?, ?, ?, ?)""",
        (tipo, fila["id"], tipo, json.dumps(payload), ahora.isoformat()))


def _confirmar_fila(con: sqlite3.Connection, fila: sqlite3.Row,
                    ahora: datetime) -> tuple[int, dict]:
    cur = con.execute(
        "UPDATE turnos SET estado='confirmado' WHERE id=? AND estado='reservado'",
        (fila["id"],))
    con.commit()
    if cur.rowcount == 0:
        return 409, {"error": "transicion invalida"}
    _emitir(con, "TurnoConfirmado", fila, ahora, {"estado": "confirmado"})
    con.commit()
    return 200, {"id": fila["id"], "estado": "confirmado"}


def confirmar_por_token(con: sqlite3.Connection, token: str,
                        ahora: datetime | None = None) -> tuple[int, dict]:
    """Confirmar: siempre permitida (sin ventana). reservado → confirmado."""
    ahora = ahora or ahora_servidor()
    fila = _fila_por_token(con, token)
    if fila is None:
        return 404, {"error": "turno no encontrado"}
    if _expirado(fila, ahora):
        return 410, {"error": "enlace expirado"}
    return _confirmar_fila(con, fila, ahora)


def _bloqueo_colisiona(con: sqlite3.Connection, profesional_id: str,
                       sillon_id: str, inicio: str, fin: str) -> bool:
    sql = """SELECT 1 FROM bloqueos
             WHERE (profesional_id IS NULL OR profesional_id = ?)
               AND (sillon_id IS NULL OR sillon_id = ?)
               AND inicio < ? AND ? < fin"""
    return con.execute(sql, (profesional_id, sillon_id, fin,
                             inicio)).fetchone() is not None


def _reprogramar_fila(con: sqlite3.Connection, fila: sqlite3.Row,
                      nuevo_inicio_raw: str,
                      ahora: datetime) -> tuple[int, dict]:
    if fila["estado"] not in ("reservado", "confirmado"):
        return 409, {"error": "transicion invalida"}
    try:
        nuevo_inicio = datetime.fromisoformat(nuevo_inicio_raw)
    except ValueError:
        return 422, {"error": "nuevo_inicio con formato ISO8601 inválido"}
    if nuevo_inicio.tzinfo is None:
        return 422, {"error": "nuevo_inicio debe incluir zona horaria"}
    if nuevo_inicio <= ahora:
        return 422, {"error": "nuevo_inicio debe ser futuro"}
    origen_inicio = datetime.fromisoformat(fila["inicio"])
    if not ventana_ok(origen_inicio, ahora):
        return 409, {"error": MENSAJE_VENTANA, "contacto": CONTACTO}
    duracion = (datetime.fromisoformat(fila["fin"]) - origen_inicio)
    nuevo_fin_dt = (nuevo_inicio + duracion)
    nuevo_fin_raw = nuevo_fin_dt.isoformat()
    con.execute("BEGIN IMMEDIATE")
    try:
        if hueco_ocupado(con, fila["profesional_id"], fila["sillon_id"],
                         nuevo_inicio_raw, nuevo_fin_raw,
                         excluir_turno=fila["id"]):
            con.rollback()
            return 409, {"error": "Ese horario ya está ocupado. "
                                  "Podés anotarte en la lista de espera."}
        if _bloqueo_colisiona(con, fila["profesional_id"], fila["sillon_id"],
                              nuevo_inicio_raw, nuevo_fin_raw):
            con.rollback()
            return 409, {"error": "Ese horario no está disponible. "
                                  "Podés anotarte en la lista de espera."}
        cur = con.execute(
            "UPDATE turnos SET inicio=?, fin=?, estado='reservado'"
            " WHERE id=? AND estado IN ('reservado','confirmado')",
            (nuevo_inicio_raw, nuevo_fin_raw, fila["id"]))
        if cur.rowcount == 0:
            con.rollback()
            return 409, {"error": "transicion invalida"}
        _emitir(con, "HuecoLiberado", fila, ahora)
        fila_nueva = con.execute("SELECT * FROM turnos WHERE id=?",
                                 (fila["id"],)).fetchone()
        _emitir(con, "TurnoReprogramado", fila_nueva, ahora,
                {"origen_inicio": fila["inicio"], "estado": "reservado"})
        con.commit()
    except Exception:
        try:
            con.rollback()
        except Exception:
            pass
        raise
    return 200, {"id": fila["id"], "inicio": nuevo_inicio_raw,
                 "fin": nuevo_fin_raw, "estado": "reservado"}


def reprogramar_por_token(con: sqlite3.Connection, token: str,
                          nuevo_inicio_raw: str,
                          ahora: datetime | None = None
                          ) -> tuple[int, dict]:
    """Reprogramar atómica (D3): ventana sobre origen, anti-solapamiento C-04
    con rango semiabierto '[)', ROLLBACK + 409 si destino ocupado.

    fin re-derivado en servidor (RN-TUR-03): misma duración del turno origen.
    Transacción corta con BEGIN IMMEDIATE (equivale a SELECT ... FOR UPDATE
    en Postgres; ver D4)."""
    ahora = ahora or ahora_servidor()
    fila = _fila_por_token(con, token)
    if fila is None:
        return 404, {"error": "turno no encontrado"}
    if _expirado(fila, ahora):
        return 410, {"error": "enlace expirado"}
    return _reprogramar_fila(con, fila, nuevo_inicio_raw, ahora)


def _cancelar_fila(con: sqlite3.Connection, fila: sqlite3.Row,
                   ahora: datetime) -> tuple[int, dict]:
    if fila["estado"] not in ESTADOS_CANCELABLES:
        return 409, {"error": "transicion invalida"}
    inicio = datetime.fromisoformat(fila["inicio"])
    if not ventana_ok(inicio, ahora):
        return 409, {"error": MENSAJE_VENTANA, "contacto": CONTACTO}
    cur = con.execute(
        "UPDATE turnos SET estado='cancelado' WHERE id=? AND estado IN"
        " ('reservado','confirmado')", (fila["id"],))
    if cur.rowcount == 0:
        con.rollback()
        return 409, {"error": "transicion invalida"}
    _emitir(con, "HuecoLiberado", fila, ahora)
    _emitir(con, "TurnoCancelado", fila, ahora,
            {"estado": "cancelado"})
    con.commit()
    return 200, {"id": fila["id"], "estado": "cancelado"}


def cancelar_por_token(con: sqlite3.Connection, token: str,
                       ahora: datetime | None = None) -> tuple[int, dict]:
    """Cancelar: exige ventana >= 24h (RN-TUR-01). Libera [inicio, fin)."""
    ahora = ahora or ahora_servidor()
    fila = _fila_por_token(con, token)
    if fila is None:
        return 404, {"error": "turno no encontrado"}
    if _expirado(fila, ahora):
        return 410, {"error": "enlace expirado"}
    return _cancelar_fila(con, fila, ahora)


# --- API staff (D5): rol recepcionista/dueño; misma ventana RN-TUR-01 ---
ROLES_STAFF = ("recepcionista", "dueño")


def _autorizado(rol: str | None) -> bool:
    return rol in ROLES_STAFF


def _fila_por_id(con: sqlite3.Connection, turno_id: str) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM turnos WHERE id = ?",
                       (turno_id,)).fetchone()


def confirmar_por_id(con: sqlite3.Connection, turno_id: str,
                     rol: str | None,
                     ahora: datetime | None = None) -> tuple[int, dict]:
    ahora = ahora or ahora_servidor()
    if not _autorizado(rol):
        return 403, {"error": "requiere rol recepcionista o dueño"}
    fila = _fila_por_id(con, turno_id)
    if fila is None:
        return 404, {"error": "turno no encontrado"}
    return _confirmar_fila(con, fila, ahora)


def cancelar_por_id(con: sqlite3.Connection, turno_id: str,
                    rol: str | None,
                    ahora: datetime | None = None) -> tuple[int, dict]:
    ahora = ahora or ahora_servidor()
    if not _autorizado(rol):
        return 403, {"error": "requiere rol recepcionista o dueño"}
    fila = _fila_por_id(con, turno_id)
    if fila is None:
        return 404, {"error": "turno no encontrado"}
    return _cancelar_fila(con, fila, ahora)


def reprogramar_por_id(con: sqlite3.Connection, turno_id: str,
                       rol: str | None, nuevo_inicio_raw: str,
                       ahora: datetime | None = None) -> tuple[int, dict]:
    ahora = ahora or ahora_servidor()
    if not _autorizado(rol):
        return 403, {"error": "requiere rol recepcionista o dueño"}
    fila = _fila_por_id(con, turno_id)
    if fila is None:
        return 404, {"error": "turno no encontrado"}
    return _reprogramar_fila(con, fila, nuevo_inicio_raw, ahora)


def _marcar_fila(con: sqlite3.Connection, fila: sqlite3.Row,
                 destino: str, ahora: datetime,
                 evento: str) -> tuple[int, dict]:
    cur = con.execute(
        "UPDATE turnos SET estado=? WHERE id=? AND estado='confirmado'",
        (destino, fila["id"]))
    con.commit()
    if cur.rowcount == 0:
        return 409, {"error": "transicion invalida"}
    fila_nueva = con.execute("SELECT * FROM turnos WHERE id=?",
                             (fila["id"],)).fetchone()
    _emitir(con, evento, fila_nueva, ahora, {"estado": destino})
    con.commit()
    return 200, {"id": fila["id"], "estado": destino}


def marcar_atendido_por_id(con: sqlite3.Connection, turno_id: str,
                           rol: str | None,
                           ahora: datetime | None = None) -> tuple[int, dict]:
    """Solo staff, desde confirmado. Sin ventana (turno ya ocurrido)."""
    ahora = ahora or ahora_servidor()
    if not _autorizado(rol):
        return 403, {"error": "requiere rol recepcionista o dueño"}
    fila = _fila_por_id(con, turno_id)
    if fila is None:
        return 404, {"error": "turno no encontrado"}
    return _marcar_fila(con, fila, "atendido", ahora, "TurnoAtendido")


def marcar_ausente_por_id(con: sqlite3.Connection, turno_id: str,
                          rol: str | None,
                          ahora: datetime | None = None) -> tuple[int, dict]:
    """Solo staff, desde confirmado. ausente ≠ cancelado (RN-REP-02)."""
    ahora = ahora or ahora_servidor()
    if not _autorizado(rol):
        return 403, {"error": "requiere rol recepcionista o dueño"}
    fila = _fila_por_id(con, turno_id)
    if fila is None:
        return 404, {"error": "turno no encontrado"}
    return _marcar_fila(con, fila, "ausente", ahora, "TurnoAusente")
