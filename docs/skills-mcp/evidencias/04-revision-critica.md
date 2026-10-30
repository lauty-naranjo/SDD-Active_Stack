# Evidencia 04 — Revisión crítica: antes y después

**Fecha**: 29/10/2026 · **Change auditado**: C-08 `whatsapp-manual-confirmacion`
**Skill propia**: `revisor-escenarios-turnos` (invocada con la herramienta `skill`)
**MCP**: Context7 (evidencia de las consultas en `03-mcp-context7.md`)

---

## 1. Solicitud realizada a la skill

> «Ejecutá `revisor-escenarios-turnos` sobre `openspec/changes/c-08-whatsapp-manual-confirmacion/`,
> capability `gestion-turnos`, RN del scope `RN-CONF-01/02/03` y `RN-TUR-01/04`. Devolvé la tabla de
> cobertura RN × escenario, los hallazgos con severidad y cita `archivo:línea`, las preguntas abiertas y la
> sección "no verificado". Verificá además: (a) al menos 3 escenarios verificables con uno feliz, uno de
> error de negocio y uno de borde; (b) que cada tarea de `tasks.md` diga cómo se verificará; (c) que no haya
> decisiones de dominio sin respaldo en la KB.»

## 2. Resultado obtenido

15 hallazgos: **2 `BLOQUEANTE`, 11 `MAYOR`, 2 `MENOR`**.

| ID | Sev. | Hallazgo (resumen) | Cita |
|---|---|---|---|
| H-01 | **BLOQUEANTE** | El panel `GET /agenda/pendientes-confirmacion` devolvía nombre, teléfono y link `wa.me` del paciente **sin exigir sesión ni rol**: el requirement no mencionaba auth y su único escenario era feliz. La KB exige auth para todo el panel interno. | `spec.md:73`, `:75-79` vs `design.md:87` |
| H-02 | **BLOQUEANTE** | Faltaba el borde **exacto** de 24 h: los escenarios fijaban 26 h y 8 h, así que un `>` en vez de `>=` prometía una ventana que el sistema rechaza. | `spec.md:11`, `:23` |
| H-03 | MAYOR | La spec decía reutilizar `POST /turnos/:id/confirmar` «existente» de C-06, pero esa ruta HTTP **no existe**: C-06 sólo expone `/turnos/:token/confirmar`. | `spec.md:63`, `tasks.md:39`, `src/c06/app.py:142-147` |
| H-04 | MAYOR | `INSERT OR IGNORE` no sólo ignora `UNIQUE`: absorbe también `CHECK`/FK, así que un `tipo` inválido daba `rowcount == 0` y se respondía `200 duplicado` en lugar del `422` prometido. | `design.md:51`, `:53`, `:67` |
| H-05 | MAYOR | `ausente` y `atendido` se enumeraban como estados a rechazar, pero ningún escenario ni tarea los ejercitaba. | `spec.md:29`, `:63` |
| H-06 | MAYOR | «`enviado_por` viene de la sesión y nunca del cuerpo» no tenía escenario negativo. | `spec.md:29` |
| H-07 | MAYOR | Dos ramas del requirement sin escenario: log sobre turno `confirmado` y `tipo = recordatorio`. | `spec.md:29` |
| H-08 | MAYOR | `UNIQUE (turno_id, tipo)` impide registrar el reintento manual que contempla el Flujo 3 y contradice el `1 — N` del modelo; declarado como riesgo, sin respaldo en la KB. | `design.md:51`, `:84`, KB `07:56` |
| H-09 | MAYOR | «Día siguiente» no fijaba zona horaria: con el reloj UTC, a las 22:00 del consultorio el default apuntaba al día equivocado. | `spec.md:73`, `src/c06/ventana.py:20-22` |
| H-10 | MAYOR | «No ocurre ninguna petición HTTP saliente» no era observable ni tenía seam de verificación. | `spec.md:85-89`, `tasks.md:40` |
| H-11 | MAYOR | El parámetro `?fecha=` explícito nunca se ejercitaba (ni el caso de formato inválido). | `spec.md:73` |
| H-12 | MAYOR | El guard de estado del log era check-then-insert: una cancelación concurrente podía dejar fila sobre un turno cancelado (viola R3). | `spec.md:29`, `design.md:85` |
| H-13 | MENOR | El «Leer antes» de C-08 en `CHANGES.md` no listaba `RN-TUR-01/04` ni `10_preguntas_abiertas.md`. | `CHANGES.md:263-268` |
| H-14 | MENOR | Tres redacciones distintas para el mismo mensaje «dentro de 24 h». | `spec.md:25`, `src/c06/servicio.py:24-27` |
| H-15 | MENOR | El escenario 401/403 no afirmaba que el turno conservara su estado, a diferencia de los otros rechazos. | `spec.md:55-59` |

**Verificado a favor (sin hallazgo)**: la spec **no inventa** el monto de la seña (usa «Seña: a confirmar con
el consultorio», coherente con `10_preguntas_abiertas.md`), y el umbral 24 h está respaldado por RN-TUR-01.

## 3. Qué aportó al change

| Métrica | Antes | Después |
|---|---|---|
| Escenarios en la spec | 11 | **19** (+8) |
| Tareas verificables en `tasks.md` | 27 | **36** (+9) |
| Requirements con auth explícita | 0 de 5 | 2 de 5 (log y panel) |
| Decisiones de diseño corregidas | — | D3, D4 y D5 |

## 4. Antes / después (tres casos)

### Caso A — H-03: endpoint fantasma

- **Cómo lo detectamos**: la skill contrastó la spec con el código real (`src/c06/app.py`), donde sólo hay
  `/turnos/<token>/{confirmar,cancelar,reprogramar}`; la operación por `id` existe como función de servicio
  (`servicio.confirmar_por_id`, `src/c06/servicio.py:231`).
- **Regla que permitió corregirlo**: consigna de verificabilidad del TP + RN-TUR-04 (la transición es real,
  la ruta no).

**Antes** (`spec.md:63`):
> Marcar confirmado SHALL reutilizar la transición existente de C-06 (`POST /turnos/:id/confirmar`, …).

**Después**:
> Marcar confirmado SHALL reutilizar la transición `reservado → confirmado` de C-06 mediante su función de
> servicio por `id` `servicio.confirmar_por_id`… Como el endpoint HTTP staff por `id` **no** existe en C-06
> (sólo expone `/turnos/:token/confirmar`), este change SHALL exponer `POST /turnos/:id/confirmar` en
> `src/c08/app.py`, sin modificar `src/c06/*`.

Y `tasks.md:5.3` dejó de afirmar «sin cambios» como si la ruta ya existiera: ahora incluye implementarla.

### Caso B — H-01: panel interno sin autenticación

- **Cómo lo detectamos**: la matriz RN × escenario dejó la fila del panel sin caso de error; al buscar el
  respaldo apareció `knowledge-base/03_actores_y_roles.md:24` («todo el panel interno requiere autenticación
  con rol») y el propio `design.md:87` asumía `401`, contradicción que la spec no reflejaba.
- **Fuente que permitió corregirlo**: KB `03_actores_y_roles.md` + `06_funcionalidades.md` (actor
  recepcionista). No es una decisión nueva: estaba en la KB y faltaba en el contrato.

**Antes** (`spec.md:73`): el requirement del panel no mencionaba sesión; el único escenario era el feliz.

**Después**: el requirement exige rol `recepcionista`/`dueño`, `401` sin sesión y `403` con rol no staff
«sin devolver datos de pacientes», más el escenario *Sin sesión o rol no staff no lista pendientes* que
verifica que el cuerpo no contenga nombres, teléfonos ni links.

### Caso C — H-04: `INSERT OR IGNORE` que se comía los errores de validación

- **Cómo lo detectamos**: releyendo la cita de SQLite que el propio MCP había traído
  (`03-mcp-context7.md` §3, `sqlite.org/lang-conflict.html`): `IGNORE` no devuelve error ante *cualquier*
  violación de constraint, incluidos `CHECK` y `FOREIGN KEY`. Con `rowcount == 0` como señal de duplicado,
  el `422` de tipo inválido era imposible.
- **Fuente que permitió corregirlo**: documentación oficial de SQLite obtenida vía Context7 + R3.

**Antes** (`design.md:49-51`): «`UNIQUE (turno_id, tipo)` + `INSERT OR IGNORE` … si `cur.rowcount == 0` la
fila ya existía».

**Después**: `INSERT … ON CONFLICT (turno_id, tipo) DO NOTHING`, que limita la resolución del conflicto a
esa unicidad y deja propagarse los demás errores de integridad; se agregó el escenario *Tipo fuera del
alcance no se registra* (`422`, 0 filas) y su tarea.

## 5. Disposición de los hallazgos

| ID | Disposición |
|---|---|
| H-01, H-02, H-03, H-04, H-05, H-06, H-07, H-09, H-10, H-11, H-12, H-13, H-15 | **Corregidos** en `spec.md`, `design.md`, `tasks.md` y `CHANGES.md` |
| H-08 | **Aceptado como riesgo declarado** (OQ-3): la unicidad impide contar reintentos; cambiarlo exige cambiar el modelo y lo decide el dueño con C-12 |
| H-14 | **Diferido a OQ-1**: el literal del aviso lo define el dueño; los escenarios sólo afirman lo observable |

## 6. Defectos propios del agente (no del change)

- El validador de `skill-creator` falló por `ModuleNotFoundError: No module named 'yaml'` → se instaló
  `pyyaml` y se repitió la validación (`01-skill-creator-invocacion.md` §4).
- La skill no se descubrió en la misma sesión en que se creó (`Skill "…" not found`): el runtime lista las
  skills al iniciar. Se verificó en una sesión nueva con `opencode run` (`02-descubrimiento-skill.md` §3).

## 7. Limitaciones de esta revisión

- Revisión de sólo lectura: no se ejecutaron los escenarios porque `src/c08/` todavía no existe.
- El borde de encoding se verificó contra el literal del spec y la semántica documentada de
  `urllib.parse.quote`; no se probó `wa.me` en un dispositivo real.
- No se verificó empíricamente `BEGIN IMMEDIATE` / `busy_timeout` (queda cubierto por las tareas 4.5–4.6).
- El test en rojo `tests/test_e2e_pagina.py::test_confirmar_sin_login` es un defecto **preexistente** de
  C-06: se documenta, no se corrige en este TP.
