"""Task 4.2 (RED primero): página pública /turnos/:token sin login + E2E.

- GET muestra estado/profesional/fecha-hora sin pedir credenciales.
- POST confirmar/cancelar/reprogramar sin sesión, mismos errores de ventana.
- Bordes E2E: 23h59 → 409 con contacto; 24h01 → 200.
- Token inválido → 404 sin filtrar datos de otros turnos.
`c06.app` aún no existe → rojo esperado. Sin cookies/sesión en ningún caso."""

from __future__ import annotations

import threading
import urllib.parse
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

INICIO = "2026-10-15T10:00:00-03:00"
FIN = "2026-10-15T10:30:00-03:00"


@pytest.fixture()
def servidor():
    from c06.app import crear_app
    app = crear_app(":memory:")
    app.seed_demo()
    srv = HTTPServer(("127.0.0.1", 0), app.handler)
    hilo = threading.Thread(target=srv.serve_forever, daemon=True)
    hilo.start()
    yield app, f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


def _get(base: str, path: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(base + path) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _post(base: str, path: str,
          data: dict | None = None) -> tuple[int, str]:
    body = urllib.parse.urlencode(data or {}).encode()
    req = urllib.request.Request(base + path, data=body, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def test_pagina_muestra_turno_sin_login(servidor) -> None:
    _, base = servidor
    status, html = _get(base, "/turnos/tok-demo-e2e")
    assert status == 200
    assert "reservado" in html
    assert "prof-demo-1" in html
    assert "2026-10-15T10:00" in html
    assert "Cookie" not in html and "login" not in html.lower()


def test_confirmar_sin_login(servidor) -> None:
    _, base = servidor
    status, _ = _post(base, "/turnos/tok-demo-e2e/confirmar")
    assert status == 200
    _, html = _get(base, "/turnos/tok-demo-e2e")
    assert "confirmado" in html


def test_borde_23h59_rechaza(servidor) -> None:
    app, base = servidor
    app.fijar_ahora("2026-10-14T10:01:00-03:00")
    status, body = _post(base, "/turnos/tok-demo-e2e/cancelar")
    assert status == 409
    assert "24 horas" in body and "contacto" in body.lower()
    _, html = _get(base, "/turnos/tok-demo-e2e")
    assert "reservado" in html


def test_borde_24h01_acepta(servidor) -> None:
    app, base = servidor
    app.fijar_ahora("2026-10-14T09:59:00-03:00")
    status, _ = _post(base, "/turnos/tok-demo-e2e/cancelar")
    assert status == 200
    _, html = _get(base, "/turnos/tok-demo-e2e")
    assert "cancelado" in html


def test_token_invalido_no_filtra(servidor) -> None:
    _, base = servidor
    assert _get(base, "/turnos/tok-inexistente-999")[0] == 404
    assert _post(base, "/turnos/tok-inexistente-999/cancelar")[0] == 404
    _, html = _get(base, "/turnos/tok-inexistente-999")
    assert "María Demo" not in html
    assert "prof-demo-1" not in html
