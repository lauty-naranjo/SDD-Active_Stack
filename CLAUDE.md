# turnos - odontologia — Instrucciones para Agentes

> Este archivo (y su copia `CLAUDE.md`) es lo PRIMERO que todo agente lee al entrar al repo.
> Generado a partir de `knowledge-base/` y `CHANGES.md`. No editar a mano sin re-sincronizar ambos archivos.

---

## Stack Tecnológico

> Stack a decidir en C-01 (ADR-01, costo cero obligatorio). Tabla best-effort de la KB — ver pregunta abierta `[DISCOVERY] stack`.

| Capa | Tecnología | Versión |
|------|------------|---------|
| Frontend | A definir (web responsive: reserva pública + panel interno) | — |
| Backend | A definir (obligatorio: webhooks MP, CAE ARCA, OAuth GCal) | — |
| Base de datos | A definir (relacional sugerida: agenda transaccional + anti-solapamiento) | — |
| Infra / despliegue | Tier gratuito, costo cero | — |
| Integraciones | Mercado Pago · ARCA · Google Calendar · WhatsApp manual (`wa.me`) | — |

Detalle completo: [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md)

---

## Base de Conocimiento

La fuente de verdad del dominio vive en `knowledge-base/`. **Leé el archivo relevante ANTES de implementar.**

| Archivo | Cuándo leerlo |
|---------|---------------|
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Entender propósito y alcance |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Auth, RBAC, permisos |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Entidades, ERD, migraciones |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | Reglas codificadas (RN-XX) |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Historias de usuario por épica |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | Flujos E2E |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Patrones, estructura, env vars |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | ⚠️ Inconsistencias a resolver ANTES de codear |
| [11_pagos_facturacion_e_integraciones.md](knowledge-base/11_pagos_facturacion_e_integraciones.md) | MP + ARCA + GCal + WA manual |

> ⚠️ Resolver las preguntas de prioridad **Alta** de `10_preguntas_abiertas.md` antes de arrancar el primer change.

---

## Skills Disponibles

Fuente de verdad: [.atl/skill-registry.md](.atl/skill-registry.md) (no versionado — el orquestador resuelve los compact rules en runtime).

| Agente | Rol | Skills que carga |
|--------|-----|------------------|
| **Backend Core** | Modelos, migraciones, anti-solapamiento, concurrencia | `supabase-postgres-best-practices`, `tdd` |
| **Backend Integraciones** | MP, ARCA, GCal, webhooks idempotentes | `tdd`, `supabase-postgres-best-practices` |
| **Frontend** | Reserva pública, agenda, reportes | `vercel-react-best-practices`, `webapp-testing` |
| **QA / E2E** | Flujos sin login, ventana 24h, `wa.me` | `webapp-testing` |
| **Orquestación** | SDD / OPSX / docs | `kb-creator`, `roadmap-generator`, `discovery-research`, `skill-registry`, `find-skill`, `active-orchestrator` |
| **Proyecto** | Auditar specs de turnos antes de implementar | `revisor-escenarios-turnos` (propia, versionada en el repo) |

Cargá la skill correspondiente al contexto ANTES de escribir código.

### Skill propia: `revisor-escenarios-turnos`

Vive en `.opencode/skills/revisor-escenarios-turnos/SKILL.md` y está versionada en el repo.

- **Cuándo usarla**: al preparar o revisar un change de turnos (`propose` / `verify`), antes de escribirlo
  código. Es obligatoria antes de `/opsx:apply` en cualquier change que toque agenda, turnos, ventana 24h,
  pagos o espera.
- **Qué necesita**: la ruta del change, la capability afectada y la lista de RN del scope (sale de
  "Leer antes" en `CHANGES.md`). Si falta alguno, lo pide; no completa el scope solo.
- **Qué devuelve**: tabla de cobertura RN × escenario, hallazgos con severidad (`BLOQUEANTE` / `MAYOR` /
  `MENOR`) y cita `archivo:línea`, preguntas abiertas detectadas y una sección "no verificado".
- **Cómo revisar su salida**: todo hallazgo tiene que citar una RN o un archivo de la KB; ningún valor
  numérico puede aparecer sin respaldo en la KB (R5); los `BLOQUEANTE` se corrigen antes de implementar.
  La skill **solo reporta**, no reescribe la spec: el fix lo hacemos nosotros.

---

## MCP integrado: Context7

No es una skill: es una integración que expone herramientas externas.

| Aspecto | Detalle |
|---|---|
| **Propósito** | Traer documentación actualizada de librerías y APIs al contexto del agente |
| **Tipo** | Servidor MCP remoto (upstash/context7), `https://mcp.context7.com/mcp` |
| **Herramientas que usamos** | `resolve-library-id` (ubicar la librería) y `query-docs` (traer fragmentos y ejemplos) |
| **Cuándo usarlo** | Al preparar `design.md` o al dudar del comportamiento real de una API del stack (`sqlite3`, `urllib.parse`, `http.server`), y ante cualquier librería que no esté en la KB |
| **Límites** | Solo lectura de documentación pública. No modifica el repo ni la base de datos. No se le pasan datos de pacientes ni credenciales. La API key, si se usa, va en `.env` y nunca al repo (R2) |
| **Configuración y verificación** | Ver `README.md` §MCP y `docs/skills-mcp/mcp.json.example` |

---

> Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md` (generado por `skill-registry`; no versionado — no está en el repo). Esta tabla solo mapea skill→rol.

---

## Roadmap de Changes

El plan de implementación completo está en [CHANGES.md](CHANGES.md). Resumen:

- **Total**: 12 changes (C-01…C-12) en 4 fases.
- **Camino crítico** (7): `C-01 → C-02 → C-03 → C-04 → C-05 → C-06 → C-12` (+ rama co-crítica `C-05 → C-07 → C-10` para cobro).
- **Primer change**: `C-01` (`foundation-setup-stack`, incluye ADR-01 de stack costo cero).

**Antes de cualquier `/opsx:propose`**: leé [CHANGES.md](CHANGES.md), identificá las dependencias del change y los archivos de "Leer antes".

---

## Reglas Duras

> No hay `~/.claude/CLAUDE.md` global en esta máquina: este archivo es la única sede de reglas. Las confirma el dueño del proyecto una por una; son contrato — romperlas es un defecto.

- **R1 — Datos de pacientes** → NUNCA datos reales de pacientes en repo, ejemplos, seeds o tests → fixtures ficticios con nombres obviamente falsos (ej. "Juan Pérez Demo").
- **R2 — Secretos** → NUNCA credenciales en código ni commits (MP token, ARCA cert/key, GCal secrets) → solo `.env` local + `.env.example` con placeholders.
- **R3 — Anti-solapamiento en DB** → NUNCA validar solapamiento solo en aplicación → constraint de exclusión o transacción serializable en DB (C-04); el código solo propaga el error.
- **R4 — TDD en seams** → NUNCA producción sin su test rojo-primero en concurrencia, idempotencia (MP/ARCA) y ventana 24h → test que falla, después el mínimo código.
- **R5 — Sin tests tautológicos** → NUNCA test que recalcule lo que el código hace → valores esperados de fuente independiente (literal, ejemplo trabajado, RN de la KB).
- **R6 — Commits** → NUNCA commitear ni pushear sin pedido explícito → cambios en working tree; si se pide commit, formato convencional sin co-autoría IA.
- **R7 — Tipado estricto (condicional al ADR-01)** → Si el stack elegido es tipado: NUNCA `any` ni dicts sin schema en bordes (webhooks, CAE, eventos GCal) → tipar. Si el stack final es otro, se revisa en C-01.

---

## Flujo de Trabajo

```
1. Leer la KB relevante (knowledge-base/)        → entender el dominio
2. Identificar el change en CHANGES.md           → respetar dependencias
3. /opsx:propose C-NN-nombre                     → proposal + design + specs + tasks
4. Revisar la spec con revisor-escenarios-turnos → cerrar huecos y valores inventados
5. Implementar las tasks (cargando skills)       → respetando las reglas duras
6. /opsx:archive C-NN-nombre + marcar [x]        → cerrar el change
```

Aplicar TODAS las reglas duras en cada paso. Ante conflicto entre la KB y este archivo, las reglas duras prevalecen.
