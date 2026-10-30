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

Resultado esperado: **29 passed, 1 failed** (estado al 29/10/2026).

> ⚠️ **Falla conocida y preexistente**: `tests/test_e2e_pagina.py::test_confirmar_sin_login` siembra el turno
> con fecha fija `2026-10-15T10:00:00-03:00` y no fija el reloj del servidor, así que hoy el turno ya está
> en el pasado y el endpoint responde `410` en vez de `200`. El código de C-06 no cambió: es un test atado a
> la fecha real. Queda registrado como defecto a corregir, no se toca en este TP.
> Detalle por escenario en el reporte de verificación del change archivado.

## MCP: Context7

Usamos el servidor MCP **Context7** (Upstash) para traer documentación actualizada de librerías al contexto
del agente. Es una integración, **no** una skill: no se registra en `.atl/skill-registry.md`.

| Ítem | Dato |
|---|---|
| Endpoint | `https://mcp.context7.com/mcp` (remoto, transporte HTTP) |
| Herramientas | `resolve-library-id`, `query-docs` |
| Credenciales | Ninguna obligatoria. Funciona anónimo con límite de peticiones bajo |
| Variables de entorno | `CONTEXT7_API_KEY` (opcional, gratuita, solo para subir el límite) |
| Costo | Gratuito |

### Configuración

La configuración del cliente opencode vive en `opencode.json`. Puede ser la global
(`C:\Users\<usuario>\.config\opencode\opencode.json`) o una del proyecto (`.opencode/opencode.json`).
El fragmento listo para copiar está en [`docs/skills-mcp/mcp.json.example`](docs/skills-mcp/mcp.json.example):

```json
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": true
    }
  }
}
```

Con API key (opcional), el header lo define **Context7**, no opencode:

```json
{ "headers": { "Authorization": "Bearer {env:CONTEXT7_API_KEY}" } }
```

> Ojo con este detalle: la documentación de opencode muestra `headers: { "CONTEXT7_API_KEY": "..." }`,
> mientras que la de Context7 pide `Authorization: Bearer <key>`. Son incompatibles entre sí; seguimos la
> del servidor. Sin key no hace falta ningún header.

### Comprobar la conexión

```bash
opencode mcp list
```

Salida esperada (recortada):

```
•  ✓ context7 connected
   https://mcp.context7.com/mcp
```

Después, una llamada real: pedirle al agente que resuelva una librería y consulte su documentación. La
evidencia de nuestra ejecución está en
[`docs/skills-mcp/evidencias/03-mcp-context7.md`](docs/skills-mcp/evidencias/03-mcp-context7.md).

### Solución de problemas

| Síntoma | Causa / solución |
|---|---|
| `opencode mcp list` no muestra el servidor | El bloque `mcp` no está en el `opencode.json` que está leyendo el cliente, o `enabled` está en `false`. Verificar también la precedencia de config (proyecto > global) |
| El servidor aparece pero las herramientas no responden | Correr `opencode mcp debug context7`, que prueba conectividad HTTP y muestra el estado de autenticación |
| Error `429 Too Many Requests` | Límite anónimo alcanzado: registrar una API key gratuita y exportar `CONTEXT7_API_KEY` |
| `401 Unauthorized` al usar key | Header mal armado: Context7 espera `Authorization: Bearer <key>` |

### Límites de uso

Solo lectura de documentación pública. No modifica el repo ni la base de datos. No se le pasan datos de
pacientes ni credenciales. La API key, si se usa, va en `.env` (R2).

## Documentación del TP «skill propia + MCP»

| Documento | Contenido |
|---|---|
| [`ENTREGA.md`](ENTREGA.md) | Integrantes, enlaces, commit de entrega y checklist del enunciado |
| [`docs/skills-mcp/investigacion.md`](docs/skills-mcp/investigacion.md) | Ficha de investigación (≤2 páginas) |
| [`docs/skills-mcp/aplicacion.md`](docs/skills-mcp/aplicacion.md) | Informe de aplicación: resultados, archivos modificados, revisión crítica y limitaciones |
| [`docs/skills-mcp/evidencias/`](docs/skills-mcp/evidencias/) | Evidencias 01–04 (skill creadora, descubrimiento, MCP y revisión antes/después) |

## Estructura

```
├── docs/discovery/        informe-discovery.md + informe-discovery.pdf (mercado A-D + fuentes)
├── docs/skills-mcp/       ficha de investigación, informe de aplicación, evidencias y config de ejemplo del MCP
├── knowledge-base/        10 archivos canónicos + README (fuente de verdad del dominio)
├── openspec/specs/        specs vigentes (ej. gestion-turnos)
├── openspec/changes/      changes activos / archive/<fecha>-<change>/ (proposal, design, tasks, specs)
├── .opencode/skills/      skills del proyecto (openspec-* + revisor-escenarios-turnos)
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
