# Ficha de investigación — skill propia + servidor MCP

**Proyecto**: turnos - odontologia · **Integrantes**: Lautaro Naranjo, Martín Escudero
**Materia**: Metodología I — «Integrar una skill propia y un MCP al proyecto odontológico» · **Fecha**: 29/10/2026

---

## 1. Necesidad detectada y change elegido

Elegimos **C-08 `whatsapp-manual-confirmacion`**: es el único change pendiente de `CHANGES.md` que depende
solo de **C-06 `gestion-ventana-24h`**, el único implementado y archivado. Se puede preparar sin
funcionalidades inexistentes porque la tabla `turnos` ya existe en `src/c06/db.py` con `estado`,
`paciente_telefono` y la máquina de estados.

- **Tarea repetible a mejorar (skill)**: revisar a mano cada spec antes de implementarla, cruzando los
  escenarios contra las reglas `RN-XX` de la KB. Fallamos en tres cosas: reglas sin escenario, escenarios no
  verificables y valores que el agente completa «porque suenan razonables» aunque la KB los deje abiertos.
  Prueba concreta: la suite da **29 verdes y 1 rojo** (`test_confirmar_sin_login`), porque el escenario
  siembra una fecha fija sin congelar el reloj.
- **Necesidad de información (MCP)**: el stack es Python stdlib (`sqlite3`, `http.server`) y no hay
  documentación local. Para el `design.md` hay que confirmar `sqlite3` (transacciones, `busy_timeout`) y
  `urllib.parse.quote` (deep link `wa.me` con tildes, `ñ` y `+54 9`).

Ambas apuntan al **mismo** change: la skill audita los escenarios de C-08 y el MCP respalda el `design.md`.

---

## 2. Skill creadora y diseño de la skill propia

| Campo | Dato |
|---|---|
| **Nombre** | `skill-creator` |
| **Fuente oficial** | Repositorio `anthropics/skills`, carpeta `skills/skill-creator` (licencia Apache-2.0) |
| **Compatibilidad** | Estándar Agent Skills (`SKILL.md` + frontmatter `name`/`description`), el mismo que usa opencode; verificado cargándola con la herramienta `skill` del agente |
| Dónde quedó | `C:\Users\ramir\.config\opencode\skills\skill-creator\` (global, **fuera del repo**) |
| Comprobación | Se carga con `skill({name})` y el `SKILL.md` pasó `scripts/quick_validate.py` → `Skill is valid!` |
| Reproducibilidad | Copia versionada en `docs/skills-mcp/vendor/skill-creator/`; comando en §4 |

**Diseño de `revisor-escenarios-turnos`**

| Aspecto | Definición |
|---|---|
| Propósito | Auditar una delta spec de OpenSpec contra las reglas `RN-XX` de la KB antes de implementarla |
| Activación | En `propose`/`verify` de un change de turnos, o ante «revisá los escenarios», «¿falta algún caso borde?», «¿esta spec es verificable?» |
| Entradas | Ruta del change, capability, RN del scope (sale de «Leer antes» de `CHANGES.md`) y archivos de `knowledge-base/` |
| Procedimiento | (1) extraer Requirements/Scenarios; (2) extraer RN del scope; (3) matriz RN × escenario (feliz/error/borde/concurrencia) y marcar huecos; (4) validar DADO-CUANDO-ENTONCES con valores literales, resultado observable y no-mutación en errores; (5) detectar decisiones de dominio inventadas contra `10_preguntas_abiertas.md`; (6) revisar bordes temporales y de concurrencia |
| Salida | Matriz de cobertura, hallazgos `BLOQUEANTE`/`MAYOR`/`MENOR` con cita `archivo:línea`, preguntas abiertas y sección «no verificado» |
| Criterio de revisión | Sin hallazgo sin cita a RN/KB; sin valor numérico sin respaldo; ≥3 escenarios por requirement crítico; todo error de negocio indica código HTTP, mensaje y que no muta estado |
| Ubicación | `.opencode/skills/revisor-escenarios-turnos/SKILL.md`, versionada (el directorio coincide con el `name`) |

---

## 3. Comparación de MCP y elección

| Criterio | Context7 (Upstash) | Playwright MCP (Microsoft) |
|---|---|---|
| Propósito | Documentación actualizada de librerías en el contexto | Automatización de navegador con snapshots |
| Capacidades | `resolve-library-id`, `query-docs` | 70+ herramientas: navegar, click, formularios, red, storage, PDF |
| Compatibilidad | Remoto, cliente MCP estándar; opencode lo documenta como ejemplo | Local vía `npx`; opencode entre los clientes soportados |
| Instalación | Ninguna: se registra la URL `https://mcp.context7.com/mcp` | `npx @playwright/mcp@latest`; Node 18+ y descarga del navegador |
| Permisos | Solo lectura de documentación pública | Control de un navegador: puede navegar y escribir en sitios |
| Credenciales / costo / licencia | Anónimo con límite bajo; key gratuita opcional; MIT | Sin credenciales; gratuito; Apache-2.0 |

**Elección: Context7.** C-08 no tiene UI todavía (la página pública y la agenda son C-05 y C-06), así que
Playwright no tendría nada real que operar. Context7 responde lo que el `design.md` necesita: transacciones
de `sqlite3` para que el log no se duplique y `urllib.parse.quote` para el deep link. **Límites**: solo
lectura de documentación pública; no modifica repo ni base; no recibe datos de pacientes; la API key, si se
usa, va en `.env` y nunca al repo ni al video (R2).

---

## 4. Instalación y comprobación

```bash
# Skill creadora (reproducible en otra máquina)
npx skills add https://github.com/anthropics/skills --skill skill-creator
```
Comprobación: figura en la lista de skills del agente y responde al invocarla.

```json
{ "mcp": { "context7": { "type": "remote", "url": "https://mcp.context7.com/mcp", "enabled": true } } }
```
Va en `C:\Users\ramir\.config\opencode\opencode.json` (global) o en `.opencode/opencode.json`; ejemplo sin
secretos en `docs/skills-mcp/mcp.json.example`. Comprobación: `opencode mcp list` muestra
`context7 connected` y `resolve-library-id` + `query-docs` devuelven documentación (evidencia 03).

---

## 5. Archivos de la fundación a actualizar

| Archivo | Cambio |
|---|---|
| `.opencode/skills/revisor-escenarios-turnos/SKILL.md` | **Nuevo**: la skill propia |
| `.atl/skill-registry.md` | Registrar propósito, ubicación y uso; corregir rutas y skills inexistentes |
| `AGENTS.md` / `CLAUDE.md` | Sección de la skill y del MCP (propósito, capacidades, uso, límites) |
| `README.md` | Requisitos, configuración reproducible y troubleshooting del MCP |
| `CHANGES.md` | C-08 referenciado como **preparado** (no implementado ni archivado) |

---

## 6. Fuentes (consultadas el 29/10/2026)

| Fuente | URL |
|---|---|
| `skill-creator` (oficial) | github.com/anthropics/skills/tree/main/skills/skill-creator |
| Especificación Agent Skills | github.com/anthropics/skills/tree/main/spec |
| Context7 (repo y endpoint) | github.com/upstash/context7 · context7.com/docs/resources/all-clients |
| Playwright MCP | playwright.dev/docs/getting-started-mcp · github.com/microsoft/playwright-mcp |
| opencode — MCP y Skills | opencode.ai/docs/mcp-servers/ · opencode.ai/docs/skills/ |

---

## 7. Pendientes y no verificado

- `skill-creator` ya estaba instalada: documentamos el comando y la comprobación, pero no ejecutamos una
  instalación limpia.
- `CHANGES.md` mantiene C-01…C-05 pendientes aunque C-06 esté archivado (el stack real no tiene ADR-01): deuda
  registrada.
- Playwright MCP se comparó, no se instaló; el test en rojo de C-06 no se corrige acá (defecto preexistente).
