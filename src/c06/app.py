"""C-06 página pública /turnos/:token (D5, 4.2).

Mínima y server-rendered (stdlib http.server, sin SPA ni sesiones):
- GET /turnos/:token → estado + profesional + fecha/hora + acciones.
- POST /turnos/:token/confirmar | /cancelar | /reprogramar (mismos errores
  de ventana que la API; 404/410/409/422 del servicio).
- Token inválido → 404 sin exponer datos de otros turnos.
- Reloj inyectable (fijar_ahora) para E2E de bordes; en producción es el
  reloj del servidor (D2). Sin GCal: siempre 200 en cambios válidos (4.3).
"""

from __future__ import annotations

import sqlite3
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from typing import Callable

from c06 import servicio
from c06.db import conectar, crear_schema
from c06.ventana import ahora_servidor


def _html(titulo: str, cuerpo: str) -> bytes:
    return (f"<!doctype html><html lang='es'><head><meta charset='utf-8'>"
            f"<title>{titulo}</title></head><body>{cuerpo}</body></html>"
            ).encode()


class App:
    def __init__(self, db_path: str = ":memory:") -> None:
        self.con: sqlite3.Connection = conectar(db_path)
        crear_schema(self.con)
        self._ahora_fijo: datetime | None = None
        app = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args: object) -> None:
                pass

            def do_GET(self) -> None:
                token = app._ruta_token(self.path)
                if token is None:
                    self._responder(404, _html("No encontrado",
                                               "<p>turno no encontrado</p>"))
                    return
                fila = self._con().execute(
                    "SELECT * FROM turnos WHERE token_publico = ?",
                    (token,)).fetchone()
                if fila is None:
                    self._responder(404, _html("No encontrado",
                                               "<p>turno no encontrado</p>"))
                    return
                cuerpo = (
                    f"<h1>Mi turno</h1><p>estado: {fila['estado']}</p>"
                    f"<p>profesional: {fila['profesional_id']}</p>"
                    f"<p>inicio: {fila['inicio']}</p>"
                    f"<p>fin: {fila['fin']}</p>"
                    f"<form method='post' action='/turnos/{token}/confirmar'>"
                    "<button>Confirmar</button></form>"
                    f"<form method='post' action='/turnos/{token}/cancelar'>"
                    "<button>Cancelar</button></form>"
                    f"<form method='post' action='/turnos/{token}/reprogramar'>"
                    "<input name='nuevo_inicio'>"
                    "<button>Reprogramar</button></form>")
                self._responder(200, _html("Mi turno", cuerpo))

            def do_POST(self) -> None:
                token, accion = app._ruta_accion(self.path)
                if token is None or accion is None:
                    self._responder(404, _html("No encontrado",
                                               "<p>turno no encontrado</p>"))
                    return
                ahora = app.ahora()
                if accion == "confirmar":
                    status, body = servicio.confirmar_por_token(
                        app.con, token, ahora)
                elif accion == "cancelar":
                    status, body = servicio.cancelar_por_token(
                        app.con, token, ahora)
                elif accion == "reprogramar":
                    largo = int(self.headers.get("Content-Length", 0))
                    params = urllib.parse.parse_qs(
                        self.rfile.read(largo).decode())
                    nuevo = (params.get("nuevo_inicio", [""])[0]).strip()
                    if not nuevo:
                        status, body = 422, {"error": "falta nuevo_inicio"}
                    else:
                        status, body = servicio.reprogramar_por_token(
                            app.con, token, nuevo, ahora)
                else:
                    self._responder(404, _html("No encontrado",
                                               "<p>turno no encontrado</p>"))
                    return
                detalle = (f"<p>estado: {body.get('estado', '')}</p>"
                           if status == 200
                           else f"<p>{body.get('error', '')}</p>"
                                f"<p>contacto: {body.get('contacto', '')}</p>"
                                f"<p><a href='/turnos/{token}'>Volver</a></p>")
                self._responder(status, _html("Resultado", detalle))

            def _con(self) -> sqlite3.Connection:
                return app.con

            def _responder(self, status: int, contenido: bytes) -> None:
                self.send_response(status)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(contenido)))
                self.end_headers()
                self.wfile.write(contenido)

        self.handler = Handler

    def ahora(self) -> datetime:
        return self._ahora_fijo or ahora_servidor()

    def fijar_ahora(self, iso: str | None) -> None:
        """Reloj fijo para E2E (None = reloj servidor)."""
        self._ahora_fijo = datetime.fromisoformat(iso) if iso else None

    def seed_demo(self) -> None:
        self.con.execute(
            """INSERT OR IGNORE INTO turnos (id, profesional_id, sillon_id,
                prestacion_id, paciente_nombre, paciente_telefono, inicio,
                fin, estado, origen, token_publico, token_expira_en)
               VALUES ('t-demo-e2e', 'prof-demo-1', 'sillon-demo-1',
                'prest-limpieza-30', 'María Demo', '+549110000005',
                '2026-10-15T10:00:00-03:00', '2026-10-15T10:30:00-03:00',
                'reservado', 'online', 'tok-demo-e2e',
                '2026-10-16T10:00:00-03:00')""")
        self.con.commit()

    @staticmethod
    def _ruta_token(path: str) -> str | None:
        partes = path.split("?", 1)[0].rstrip("/").split("/")
        if len(partes) == 3 and partes[1] == "turnos" and partes[2]:
            return urllib.parse.unquote(partes[2])
        return None

    @staticmethod
    def _ruta_accion(path: str) -> tuple[str | None, str | None]:
        partes = path.split("?", 1)[0].rstrip("/").split("/")
        if len(partes) == 4 and partes[1] == "turnos" and partes[2]:
            if partes[3] in ("confirmar", "cancelar", "reprogramar"):
                return urllib.parse.unquote(partes[2]), partes[3]
        return None, None


def crear_app(db_path: str = ":memory:") -> App:
    return App(db_path)


Reloj = Callable[[], datetime]
