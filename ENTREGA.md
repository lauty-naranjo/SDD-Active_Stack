# ENTREGA — TP «Integrar una skill propia y un MCP al proyecto odontológico»

**Materia**: Metodología I · Tecnicatura Universitaria en Programación
**TP anterior**: «Del Discovery al primer Change» (mismo repositorio y roadmap)

## Integrantes

| Integrante | Contribución |
|---|---|
| Lautaro Naranjo | Investigación y ficha, configuración del MCP Context7, integración de la skill a la fundación y preparación del change C-08 |
| Martín Escudero | Diseño de la skill propia, revisión crítica con la skill, correcciones de la spec y del diseño, evidencias |

## Enlaces

| Dato | Valor |
|---|---|
| Repositorio | https://github.com/lauty-naranjo/SDD-Active_Stack |
| Commit de entrega | `360f5a3` — «docs(c-08): prepara whatsapp-manual-confirmacion con la spec revisada»; el estado entregado es el tip de `main` |
| Ficha de investigación | [`docs/skills-mcp/investigacion.md`](docs/skills-mcp/investigacion.md) |
| Informe de aplicación | [`docs/skills-mcp/aplicacion.md`](docs/skills-mcp/aplicacion.md) |
| Evidencias | [`docs/skills-mcp/evidencias/`](docs/skills-mcp/evidencias/) |

## Contenido de este zip

```
ENTREGA.md
investigacion.md          (ficha, ≤2 páginas)
aplicacion.md             (informe, ≤2 páginas)
evidencias/
 01-skill-creator-invocacion.md
 02-descubrimiento-skill.md
 03-mcp-context7.md
 04-revision-critica.md
mcp.json.example          (configuración del MCP sin secretos)
```

El repositorio contiene además la skill versionada (`.opencode/skills/revisor-escenarios-turnos/`), el
registro (`.atl/skill-registry.md`), las instrucciones del agente (`AGENTS.md` y `CLAUDE.md`) y los artefactos
completos del change preparado (`openspec/changes/c-08-whatsapp-manual-confirmacion/`).

## Cómo reproducir

```bash
# 1) Skill creadora (si no está instalada)
npx skills add https://github.com/anthropics/skills --skill skill-creator

# 2) MCP Context7: agregar el bloque de docs/skills-mcp/mcp.json.example
#    en ~/.config/opencode/opencode.json o en .opencode/opencode.json
opencode mcp list          # debe mostrar: context7 connected

# 3) Integridad del change preparado
openspec validate c-08-whatsapp-manual-confirmacion --strict

# 4) Suite del proyecto
python -m pytest -q        # 29 verdes · 1 rojo preexistente (test_confirmar_sin_login, C-06)
```

## Estado de la entrega

| Requisito del enunciado | Estado |
|---|---|
| Skill propia creada con una skill creadora y adaptada al dominio | ✅ `revisor-escenarios-turnos` + evidencia 01 |
| Skill guardada en la carpeta de skills del agente | ✅ `.opencode/skills/revisor-escenarios-turnos/` |
| Fuente de la skill creadora versionada (instalada fuera del repo) | ✅ `docs/skills-mcp/vendor/skill-creator/` |
| Registro en `.atl/skill-registry.md` (nombre, propósito, ubicación, uso) | ✅ |
| `AGENTS.md` y `CLAUDE.md` actualizados y coherentes | ✅ (idénticos) |
| Comprobación en sesión nueva de que el agente encuentra y usa la skill | ✅ evidencia 02 |
| MCP conectado y al menos una herramienta real ejecutada | ✅ Context7 + evidencia 03 |
| MCP documentado (requisitos, config, env, verificación, troubleshooting) en README | ✅ `README.md` §MCP |
| Configuración de ejemplo sin secretos | ✅ `docs/skills-mcp/mcp.json.example` |
| MCP documentado como integración y no como skill | ✅ |
| Change pendiente preparado con SDD (proposal, design, spec, tasks) | ✅ C-08 |
| ≥3 escenarios verificables (esperado, error de negocio, borde) | ✅ 19 escenarios |
| Tareas con la forma de verificación de cada escenario | ✅ 36 tareas |
| Reglas revisadas contra la KB, sin decisiones de dominio inventadas | ✅ evidencia 04 |
| Change NO marcado como implementado/verificado/archivado | ✅ `CHANGES.md` → «preparado» |
| Ficha de investigación ≤2 páginas | ✅ |
| Informe de aplicación ≤2 páginas | ✅ |
| Evidencia de uso de la skill y del MCP | ✅ evidencias 01–04 |
| Al menos una omisión/error detectado con antes y después | ✅ 15 hallazgos, 3 antes/después |
| Historial de commits | ✅ commits del TP2 en `main` (skill, MCP + ficha, change C-08 y entrega). **Nota**: el historial completo figura a nombre de un solo integrante (`lauty-naranjo`), incluidos los commits previos del TP1 |
| Video ≤5 min | ➡️ Se entrega por separado, fuera del repositorio (Lautaro Naranjo y Martín Escudero) |
| Datos ficticios y sin secretos | ✅ (`Juan Pérez Demo`, `tur-demo-001`, sin credenciales) |
