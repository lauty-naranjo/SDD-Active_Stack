"""C-06 ventana 24h (D2): reloj servidor + comparación en UTC.

Acepta ⟺ inicio - ahora >= 24h exactas. Igualdad acepta; < 24h rechaza.
`inicio`/`ahora` son aware (literales del spec con -03:00); la resta es
absoluta, sin redondeo a días calendario.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

VENTANA = timedelta(hours=24)


def ventana_ok(inicio: datetime, ahora: datetime) -> bool:
    """True si falta >= 24h (borde exacto 24h00 acepta)."""
    return (inicio - ahora) >= VENTANA


def ahora_servidor() -> datetime:
    """Reloj del servidor (UTC). Nunca hora del cliente (D2)."""
    return datetime.now(timezone.utc)
