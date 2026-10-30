# Informe de aplicación — skill propia + MCP

**Proyecto**: turnos - odontologia · **Integrantes**: Lautaro Naranjo, Martín Escudero
**Materia**: Metodología I · **Fecha**: 29/10/2026
**Ficha de investigación**: [`investigacion.md`](investigacion.md) · **Evidencias**: [`evidencias/`](evidencias/)

---

## 1. Resultados

**Skill propia integrada.** `revisor-escenarios-turnos` se generó con `skill-creator`, se adaptó al dominio
(alcance de **sólo lectura**: reporta, no reescribe la spec; fixtures ficticios por R1) y se validó con
`scripts/quick_validate.py` → `Skill is valid!`. Vive versionada en
`.opencode/skills/revisor-escenarios-turnos/SKILL.md`, quedó registrada en `.atl/skill-registry.md` (nombre,
propósito, ubicación y situaciones de uso) y referenciada en `AGENTS.md` y `CLAUDE.md` (cuándo usarla, qué
necesita y cómo revisar la salida). El descubrimiento se verificó en una **sesión nueva** con `opencode run`,
sin nombrarle la skill al agente.

**MCP operativo.** Context7 quedó conectado (`opencode mcp list` → `context7 connected`) y se ejecutaron
herramientas reales: `resolve-library-id` + `query-docs` sobre SQLite (conflictos y transacciones) y sobre
`urllib.parse`. Los fragmentos obtenidos alimentaron las decisiones D1 y D3 del `design.md`; está documentado
como integración en `README.md` y en las instrucciones del agente, no como skill.

**Change C-08 preparado.** `openspec/changes/c-08-whatsapp-manual-confirmacion/` con `proposal.md`,
`design.md`, `specs/gestion-turnos/spec.md` (5 requirements, **19 escenarios**) y `tasks.md`
(**36 tareas** con su forma de verificación). `openspec validate c-08-whatsapp-manual-confirmacion --strict`
→ `is valid`. No se implementó, verificó ni archivó.

## 2. Evidencias

| Evidencia | Qué acredita |
|---|---|
| [`01-skill-creator-invocacion.md`](evidencias/01-skill-creator-invocacion.md) | Invocación de la skill creadora, pautas aplicadas, validación y salida cruda del validador |
| [`02-descubrimiento-skill.md`](evidencias/02-descubrimiento-skill.md) | Sesión nueva: el agente encuentra y usa la skill por las referencias del proyecto; incluye el fallo de descubrimiento en caliente y su resolución |
| [`03-mcp-context7.md`](evidencias/03-mcp-context7.md) | Conexión del MCP, solicitudes reales (`resolve-library-id`, `query-docs`) y qué aportó cada fragmento al `design.md` |
| [`04-revision-critica.md`](evidencias/04-revision-critica.md) | Informe de la skill, 15 hallazgos y los antes/después con cita |

## 3. Archivos modificados y motivo

| Archivo | Modificación y motivo |
|---|---|
| `.opencode/skills/revisor-escenarios-turnos/SKILL.md` | **Nuevo**: la skill propia, versionada dentro del repo |
| `.atl/skill-registry.md` | Se registró la skill (nombre, propósito, ubicación, uso) y se corrigieron rutas a un usuario inexistente y 6 skills que no estaban instaladas |
| `AGENTS.md` / `CLAUDE.md` | Se agregó la sección de la skill propia y la del MCP (propósito, capacidades, momento de uso, límites); ambos archivos quedaron idénticos |
| `README.md` | Se agregó «MCP: Context7» con requisitos, configuración, comprobación de conexión, troubleshooting y el detalle del header de autenticación |
| `docs/skills-mcp/investigacion.md` | Ficha de la Parte 1 (≤2 páginas) |
| `docs/skills-mcp/mcp.json.example` | Configuración de ejemplo sin secretos |
| `docs/skills-mcp/vendor/skill-creator/` | Copia versionada de la skill creadora (instalada fuera del repo) |
| `docs/skills-mcp/evidencias/01…04` | Registros de uso y revisión crítica |
| `openspec/changes/c-08-…/spec.md` | 11 → 19 escenarios (auth del panel, borde exacto de 24 h, tipo inválido, estados faltantes, zona horaria) |
| `openspec/changes/c-08-…/design.md` | D3 (`ON CONFLICT DO NOTHING`), D4 (la ruta por `id` la expone C-08) y D5 (auth y zona horaria del panel) |
| `openspec/changes/c-08-…/tasks.md` | 27 → 36 tareas, cada una con su forma de verificación |
| `openspec/changes/c-08-…/proposal.md`, `README.md` | Artefactos del change preparado |
| `CHANGES.md` | C-08 pasa a **preparado** (no implementado ni archivado) y se completó su «Leer antes» |

No se regeneró la fundación ni se marcaron etapas que no se ejecutaron: los cambios son incrementales y se
documentan acá.

## 4. Revisión crítica

La skill devolvió **15 hallazgos** (2 `BLOQUEANTE`, 11 `MAYOR`, 2 `MENOR`). Se corrigieron 13, uno quedó como
riesgo declarado (H-08, la unicidad impide contar reintentos) y uno se difirió a pregunta abierta (H-14, el
literal del aviso). El detalle con citas y los antes/después están en `04-revision-critica.md`; los tres casos
más demostrativos:

1. **Panel interno sin autenticación** (BLOQUEANTE). El endpoint devolvía nombre, teléfono y link `wa.me` sin
   sesión. La KB (`03_actores_y_roles.md`) exige auth para todo el panel y el propio `design.md` asumía `401`,
   pero la spec no lo reflejaba: se agregó el requisito y dos escenarios (401/403 y «no filtra datos»).
2. **Endpoint fantasma** (`POST /turnos/:id/confirmar` «existente»). No existe en C-06 (sólo por `token`): se
   corrigió la spec y la tarea ahora incluye exponer la ruta en `src/c08/app.py` reutilizando
   `servicio.confirmar_por_id`.
3. **`INSERT OR IGNORE` que absorbía `CHECK`/FK**. Releyendo la cita de SQLite que trajo el MCP, el
   `rowcount == 0` confundía «tipo inválido» con «duplicado» y hacía imposible el `422` prometido. Se cambió a
   `ON CONFLICT (turno_id, tipo) DO NOTHING` y se agregó el escenario correspondiente.

También se registran dos defectos propios del agente: falta de `pyyaml` para el validador de `skill-creator`
(instalado y repetido) y la skill no visible en la misma sesión en que se creó (se verificó en sesión nueva,
porque el runtime lista las skills al iniciar).

## 5. Limitaciones

- **El change no está implementado**: `src/c08/` no existe, así que ningún escenario se ejecutó; la
  verificación está planificada en `tasks.md` (TDD rojo-primero).
- `wa.me` no se probó en un dispositivo real: el encoding se contrastó contra la semántica documentada de
  `urllib.parse.quote` y contra el literal del escenario.
- `BEGIN IMMEDIATE` / `busy_timeout` no se validaron empíricamente (tareas 4.5–4.6).
- El test `tests/test_e2e_pagina.py::test_confirmar_sin_login` sigue en rojo (**defecto preexistente** de
  C-06; hoy la suite da 29 verdes y 1 rojo). No se corrige en este TP y no se oculta.
- `CHANGES.md` mantiene C-01…C-05 pendientes aunque C-06 esté archivado: deuda registrada, no resuelta.
- Playwright MCP se comparó pero no se instaló; el video de demostración queda fuera de este informe.
