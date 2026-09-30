# turnos - odontologia — Sistema de turnos odontológicos

Proyecto académico (Metodología I). Reserva online 24/7 + agenda multi-profesional/sillón
sin solapamientos + ventana 24h + seña Mercado Pago + factura ARCA + sync Google Calendar.
Ver alcance y reglas en `knowledge-base/` y el plan en `CHANGES.md`.

## Requisitos

- Python 3.11+ (desarrollo y CI con 3.13)
- `pip`

## Instalación

```bash
python -m pip install -r requirements.txt
```

Sin dependencias de runtime: solo stdlib (`sqlite3`, `http.server`) + `pytest` para tests.
Sin secretos: copiar `.env.example` a `.env` solo cuando un change lo pida; nunca
commitear valores reales (R2).

## Correr los tests

```bash
python -m pytest tests/ -q
```

Resultado esperado: **30 passed** (change C-06, 14 escenarios del spec cubiertos).
Detalle por escenario en el reporte de verificación del change archivado.

## Estructura

```
├── docs/discovery/        informe-discovery.md + informe-discovery.pdf (mercado A-D + fuentes)
├── knowledge-base/        10 archivos canónicos + README (fuente de verdad del dominio)
├── openspec/specs/        specs vigentes (ej. gestion-turnos)
├── openspec/changes/      changes activos / archive/<fecha>-<change>/ (proposal, design, tasks, specs)
├── src/c06/               implementación C-06 (ventana 24h)
├── tests/                 1 test por comportamiento del spec (TDD, fixtures ficticios)
├── CHANGES.md             roadmap: 12 changes, dependencias, camino crítico
├── AGENTS.md / CLAUDE.md  instrucciones + reglas duras R1-R7
└── .env.example           placeholders (sin valores reales)
```

## Flujo de trabajo (resumen)

Propuesta (`/opsx-propose`) → implementación (`/opsx-apply`) → verificación
(`/opsx-verify`, tests en verde obligatorio) → archive (`/opsx-archive`).
Historial de commits del repo muestra el proceso por etapas.
