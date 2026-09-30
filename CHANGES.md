# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **turnos - odontologia** (sistema de turnos odontológicos, fundación active-orchestrator).
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

> Alineación MVP (discovery sección D, fuente primaria `docs/discovery/informe-discovery.md`): imprescindibles v1 = reserva online 24/7, agenda multi-profesional/sillón (duración variable, bloqueos, anti-solapamiento), ventana 24h confirmación/cancelación/reprogramación, sobreturnos con tope + lista de espera, WhatsApp manual costo cero, seña Mercado Pago, factura ARCA, sync Google Calendar, reportes básicos. Diferenciadores v1: seña obligatoria, waitlist con reclamo único, onboarding sin fricción (sin cuenta obligatoria para el paciente), costo cero.

---

## Cómo usar este documento

1. Identificar el change a implementar (verificar que sus dependencias están en `openspec/changes/archive/`).
2. Leer los docs de la knowledge-base indicados en "Leer antes".
3. Ejecutar `/opsx:propose <nombre-del-change>`.
4. Al terminar el change, archivarlo con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` en este archivo.

---

## Árbol de dependencias

```
C-01 foundation-setup-stack
  └── C-02 core-models
        └── C-03 auth-panel-rbac                 ← desbloquea TODO lo demás
              └── C-04 agenda-motor-disponibilidad
                    └── C-05 reserva-online-publica
                          │
                          ├── C-06 gestion-ventana-24h
                          │     ├── C-08 whatsapp-manual-confirmacion   ← paralelo
                          │     ├── C-09 sobreturnos-lista-espera       ← paralelo
                          │     ├── C-11 sync-google-calendar           ← paralelo
                          │     └── C-12 reportes-basicos               ← + C-07
                          │
                          └── C-07 sena-mercadopago                     ← paralelo con C-06
                                └── C-10 factura-arca
```

### Paralelismo por fase

> Cada "gate" es un punto de sincronización. Los changes dentro de un grupo pueden ejecutarse en paralelo.

```
GATE 0: ninguna
  → C-01 (solo)

GATE 1: C-01 ✓
  → C-02 (solo)

GATE 2: C-02 ✓
  → C-03 (solo)

GATE 3: C-03 ✓
  → C-04 (solo — motor transaccional, base de todo)

GATE 4: C-04 ✓
  → C-05 (solo — crea el concepto Turno reservable)

GATE 5: C-05 ✓                     ← FORK (2 paralelos: gestión vs. dinero)
  → C-06 gestion-ventana-24h       [Agente A]
  → C-07 sena-mercadopago          [Agente B]

GATE 6: C-06 ✓                     ← FORK (3 paralelos)
  → C-08 whatsapp-manual           [Agente C]
  → C-09 sobreturnos-lista-espera  [Agente A]
  → C-11 sync-google-calendar      [Agente B]

GATE 7: C-07 ✓ (ideal si C-06 ✓ — homologación ARCA en paralelo temprano)
  → C-10 factura-arca              [Agente B]

GATE 8: C-06 + C-07 ✓
  → C-12 reportes-basicos          [Agente C]
```

### Camino crítico (7 changes — mínimo irreducible)

```
C-01 → C-02 → C-03 → C-04 → C-05 → C-06 → C-12
```

> Rama co-crítica para el cobro (misma longitud, sin ella no hay MVP): `C-05 → C-07 → C-10*`. El asterisco marca que C-10 es el "último" alternativo del camino crítico: sin seña acreditada (C-07) ni factura (C-10) la reserva online no es válida según RN-PAGO-01. Atacar C-10 temprano en ambiente de homologación ARCA aunque su gate formal sea el 7.

### Plan óptimo con 3 agentes

```
Paso │ Agente A (Backend Core)      │ Agente B (Backend Integraciones) │ Agente C (Frontend/Agenda UI)
─────┼──────────────────────────────┼──────────────────────────────────┼─────────────────────────────────
  1  │ C-01 foundation-setup-stack  │         —                        │         —
  2  │ C-02 core-models             │         —                        │         —
  3  │ C-03 auth-panel-rbac         │         —                        │         —
  4  │ C-04 agenda-motor            │         —                        │         —
  5  │ C-05 reserva-online-publica  │         —                        │         —
  6  │ C-06 gestion-ventana-24h     │ C-07 sena-mercadopago            │         —
  7  │ C-09 sobreturnos-espera      │ C-11 sync-google-calendar        │ C-08 whatsapp-manual
  8  │         —                    │ C-10 factura-arca                │ C-12 reportes-basicos
```

### Riesgos conocidos y mitigaciones (discovery §10 + KB)

- **WhatsApp automático impagable** → v1 exclusivamente manual (`wa.me` + log, RN-CONF-02). Ningún change introduce dependencia de la API Meta. Riesgo residual: poco diferencial → mitigado por seña obligatoria + waitlist con reclamo único.
- **ARCA traba el semestre** → C-10 ataca homologación lo antes posible en paralelo (GATE 7 puede solaparse con GATE 6); factura en estado `error` con reintento idempotente, nunca bloquea la reserva.
- **Alcance (4 integraciones + multi-sillón) vs. tiempos** → recorte consciente ya aplicado: sin obras sociales (DD-01), sin odontograma/ficha (DD-05), sede única v1 (SU-02). Si hay desvío, recortar en orden: C-11 (GCal) → C-12 (reportes) → C-10 (ARCA a modo manual), nunca el núcleo C-04/C-05/C-06/C-07.
- **Supuestos sin probar** (adopción online SU-01, catálogo validable SU-03, sede única SU-02, identidad paciente RN-GLB-02) → valores provisorios parametrizables (monto seña, tope sobreturnos, timeout, DNI nullable) para no re-migrar cuando se respondan las preguntas abiertas.

### Backlog explícito (no v1 — no son changes activos)

Odontograma/ficha clínica · Portal del paciente · Recordatorios automáticos WhatsApp API · Obras sociales/liquidación (radar v2) · Campañas/recuperación de inactivos (fuera de alcance). Ver `knowledge-base/06_funcionalidades.md` §Backlog y `knowledge-base/09_decisiones_y_supuestos.md` DD-01/DD-02/DD-05.

---

## FASE 0 — Cimientos y decisiones

> C-01 desbloquea todo. C-02 es referenciado por todos los demás. C-03 es prerrequisito de cualquier recurso protegido.

### [C-01] `foundation-setup-stack`
- **Estado**: `[ ]` pendiente
- **Scope**: Scaffolding + decisión de stack costo cero documentada (no asumir en silencio)
  - `ADR-01 stack costo cero`: decidir y documentar con alternativas (p. ej. A: backend Python FastAPI + Postgres gratis Supabase/Neon + frontend Vite+React en Vercel/Render free-tier; B: Node+Nest + misma DB; C: monolito Next.js + Postgres gratis). Criterio: webhooks MP, homologación ARCA, OAuth GCal y deploy tier gratuito. Registrar decisión en `docs/adr/001-stack.md`
  - Estructura `backend/app/{domain,application,infrastructure}` + `frontend/src/{features,shared,pages}` según `08_arquitectura_propuesta.md` §Estructura
  - `GET /api/health`, `.env.example` con `DATABASE_URL, MP_ACCESS_TOKEN, MP_WEBHOOK_SECRET, ARCA_CUIT/PTO_VTA/CERT/KEY, GCAL_CLIENT_ID/SECRET, APP_BASE_URL, SENA_TIMEOUT_MIN` (sin secretos hardcodeados)
  - Migraciones inicializadas vacías (convención `Migración 001` reservada a C-02), CI mínima (lint+test backend/frontend)
  - Tests: health check, carga de env, convención de migraciones
- **Dependencias**: ninguna
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` (alcance v1 y fuera de alcance)
  - `knowledge-base/02_descripcion_general.md` §Stack (valores low-confidence a decidir)
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios
  - `knowledge-base/10_preguntas_abiertas.md` ([DISCOVERY] `stack`, `system_type`)
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-04 (backend propio obligatorio)

---

### [C-02] `core-models`
- **Estado**: `[ ]` pendiente
- **Scope**: Entidades base + migraciones iniciales + seed demo (sede única v1)
  - Modelos: `Sede, Paciente (dni nullable — decisión IDENT abierta), Profesional, Sillon, Prestacion (duracion_min, seña_monto/porcentaje nullable), FranjaHoraria, Bloqueo` con mixins `created_at/updated_at/is_active/deleted_at`
  - `BaseRepository[T]` + `UnitOfWork`; unicidad paciente parametrizable (teléfono o DNI según RN-GLB-02)
  - Migración 001: tablas core + índices `(profesional_id,inicio), (sillon_id,inicio), telefono, dni`
  - Seed: 1 sede demo, 2 profesionales + 2 sillones, catálogo mínimo (limpieza 30', consulta 20', conducto 90' provisorias), 1 recepcionista + 1 dueño, horarios Lun–Vie + 1 bloqueo ejemplo
  - Tests: constraints, unicidad paciente, seed idempotente
- **Dependencias**: C-01
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Entidades (Paciente, Profesional, Sillon, Prestacion) + §Seed
  - `knowledge-base/05_reglas_de_negocio.md` §RN-AGEN-02/04, §RN-GLB-02/03
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones
  - `knowledge-base/10_preguntas_abiertas.md` (sede, IDENT, catálogo)
  - `knowledge-base/03_actores_y_roles.md` (quién opera cada entidad)

---

### [C-03] `auth-panel-rbac`
- **Estado**: `[ ]` pendiente
- **Scope**: Auth del panel interno + RBAC + tokens públicos de paciente (sin cuenta obligatoria)
  - `POST /api/auth/login` (rate limit 5/60s por IP+email), `POST /api/auth/refresh` con rotación, `POST /api/auth/logout`, `GET /api/auth/me`
  - RBAC: Paciente (solo sus turnos vía token), Recepcionista (agenda/turnos/sobreturnos/espera, config solo lectura, cobrar/conciliar), Dueño (total + facturar + exportar) según matriz `03_actores_y_roles.md`
  - `token_publico` único con expiración por turno (gestionar/reclamar sin login); validación en backend de ventana/topes/anti-solapamiento, nunca solo frontend
  - Migración 002: tablas auth (users, roles) + columna `token_publico` en turnos
  - Tests: login/refresh/logout, RBAC por rol, token expirado, rate limit
- **Dependencias**: C-02
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` (matriz RBAC + rutas públicas)
  - `knowledge-base/05_reglas_de_negocio.md` §Excepciones globales
  - `knowledge-base/07_flujos_principales.md` §Flujo 2 (quién gestiona)
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad
  - `knowledge-base/04_modelo_de_datos.md` §Turno (`token_publico`)

---

## FASE 1 — Agenda y reserva (núcleo MVP)

> C-04 es prerrequisito de todo lo asistencial. C-05 crea el Turno reservable. US-001, US-010, US-011, US-012, US-020.

### [C-04] `agenda-motor-disponibilidad`
- **Estado**: `[ ]` pendiente
- **Scope**: Motor de disponibilidad real + anti-solapamiento transaccional (corazón del sistema)
  - `GET /disponibilidad?profesional=&sillon=&prestacion=&desde=&hasta=` = franja − turnos vigentes − bloqueos; `fin = inicio + prestacion.duracion_min` (RN-TUR-02/03)
  - Alta/mover/reasignar con lock transaccional o constraint de exclusión: rechazo ante solapamiento en `(profesional, intervalo)` o `(sillon, intervalo)` (RN-AGEN-01); CRUD `FranjaHoraria` + `Bloqueo` (motivo obligatorio, resta inmediata, RN-AGEN-03); desactivar profesional/sillón oculta futuro sin borrar historial (RN-AGEN-04)
  - Vista agenda día/semana por profesional y por sillón (backend lista para UI de C-05/C-06)
  - Migración 003: `franja_horaria, bloqueo`, constraint anti-solapamiento en turnos
  - Tests: concurrencia (doble reserva del mismo hueco → 1 gana), bloqueo resta disponibilidad, duración derivada, desactivación
- **Dependencias**: C-03
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Turno, §Bloqueo + regla estructural anti-solapamiento
  - `knowledge-base/05_reglas_de_negocio.md` §RN-AGEN-01/02/03/04, §RN-TUR-02/03
  - `knowledge-base/06_funcionalidades.md` §US-010, §US-011, §US-012
  - `knowledge-base/07_flujos_principales.md` §Flujo 1 (pasos 1–2)
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones (lock/constraint)

---

### [C-05] `reserva-online-publica`
- **Estado**: `[ ]` pendiente
- **Scope**: Reserva pública 24/7 con `pendiente_sena` (onboarding sin fricción)
  - Páginas `/, /reservar, /disponibilidad`: prestaciones + profesionales/sillones con huecos reales; `POST /turnos` crea pre-reserva `pendiente_sena` con `inicio/fin`, `origen=online`, `token_publico` y enlace de gestión (CA-1/CA-2/CA-3 US-001)
  - Sin disponibilidad no se ofrece el horario (ni overbooking silencioso); validación backend de duración/tope/ventana
  - Configuración de prestaciones/duraciones/topos/seña visible para dueño (US-012 CA-1/CA-2)
  - Migración 004: `turno (estado, origen, token_publico, es_sobreturno=false)` + tabla `paciente` liviana (nombre+teléfono obligatorios)
  - Tests: grilla sin huecos fantasma, fin derivado, doble clic concurrente, paciente sin cuenta reserva igual
- **Dependencias**: C-04
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-001, §US-012
  - `knowledge-base/07_flujos_principales.md` §Flujo 1 (pasos 1–2)
  - `knowledge-base/04_modelo_de_datos.md` §Turno, §Paciente, §Prestacion
  - `knowledge-base/05_reglas_de_negocio.md` §RN-TUR-02/03/04
  - `knowledge-base/03_actores_y_roles.md` §Rutas públicas

---

### [C-06] `gestion-ventana-24h`
- **Estado**: `[x]` archivado 2026-09-30 (`openspec/changes/archive/2026-09-30-c-06-gestion-ventana-24h/`, spec principal `openspec/specs/gestion-turnos/spec.md`)
- **Scope**: Confirmar/cancelar/reprogramar con ventana 24h + máquina de estados
  - `POST /turnos/:token/confirmar|/cancelar|/reprogramar` (paciente con token) + equivalentes autenticados para recepcionista; rechazo <24h con mensaje claro + contacto (RN-TUR-01, US-020 CA-1/CA-3)
  - Máquina de estados `pendiente_sena → reservado → confirmado → atendido/ausente/cancelado` sin saltos inválidos (RN-TUR-04); cancelación válida libera hueco y dispara oferta a lista de espera (hook a C-09, RN-SOB-04, US-020 CA-2); `ausente` vs `cancelado` siempre distintos (RN-REP-02)
  - Página `/turnos/:token` (gestión sin login) + panel recepcionista para operar
  - Tests: borde 24h (23:59 rechaza, 24:01 acepta), reprogramación a hueco ocupado → sugerencia de espera, transición inválida rechazada
- **Dependencias**: C-05
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-020
  - `knowledge-base/07_flujos_principales.md` §Flujo 2
  - `knowledge-base/05_reglas_de_negocio.md` §RN-TUR-01/04, §RN-SOB-04, §RN-REP-02
  - `knowledge-base/04_modelo_de_datos.md` §Turno (estados)
  - `knowledge-base/03_actores_y_roles.md` (quién puede qué)

---

## FASE 2 — Dinero y confirmación (diferenciadores v1)

> C-06 y C-07 corren en paralelo (GATE 5). C-08/C-09 dependen de C-06. US-002, US-021, US-030, US-031.

### [C-07] `sena-mercadopago`
- **Estado**: `[ ]` pendiente
- **Scope**: Seña obligatoria Mercado Pago con idempotencia y timeout (diferenciador v1)
  - `POST /pagos/sena` genera preferencia MP desde `pendiente_sena`; `POST /pagos/webhook` verifica firma (`MP_WEBHOOK_SECRET`), acredita idempotente por `mp_payment_id` y pasa turno a `reservado` + comprobante (RN-PAGO-01/02, US-002 CA-2/CA-3)
  - Job/timeout `SENA_TIMEOUT_MIN` (provisorio 30', parametrizable — pregunta abierta): sin pago acreditado libera el horario (RN-PAGO-03, US-002 CA-1)
  - Entidad `PagoSena` 1–1 con Turno (`mp_preference_id, mp_payment_id, monto, estado`); monto fijo o % parametrizable (pregunta abierta de seña)
  - Tests: webhook duplicado no duplica, timeout libera, firma inválida rechazada, pago sin turno → bandeja conciliación manual
- **Dependencias**: C-05
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-002
  - `knowledge-base/07_flujos_principales.md` §Flujo 1 (pasos 3–4) + §Flujo 5
  - `knowledge-base/11_pagos_facturacion_e_integraciones.md` §Mercado Pago
  - `knowledge-base/05_reglas_de_negocio.md` §RN-PAGO-01/02/03
  - `knowledge-base/04_modelo_de_datos.md` §PagoSena

---

### [C-08] `whatsapp-manual-confirmacion`
- **Estado**: `[ ]` pendiente
- **Scope**: Confirmación/recordatorio manual costo cero con log (sin API Meta)
  - Botón por turno en panel/agenda abre `wa.me/<tel>?text=<plantilla: profesional, fecha/hora, seña, ventana 24h>` (RN-CONF-01/03, US-021 CA-1); al enviar, `POST /turnos/:id/whatsapp-log` registra `{tipo, enviado_por, enviado_en}` en `MensajeWhatsApp` (US-021 CA-2)
  - Panel "pendientes de confirmación del día siguiente" (Flujo 3); marcar confirmado manual tras respuesta del paciente; ningún flujo exige API WhatsApp (RN-CONF-02, US-021 CA-3)
  - Tests: plantilla con datos correctos, log quién/cuándo/tipo, v1 funciona sin credenciales Meta
- **Dependencias**: C-06
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-021
  - `knowledge-base/07_flujos_principales.md` §Flujo 3
  - `knowledge-base/11_pagos_facturacion_e_integraciones.md` §WhatsApp manual
  - `knowledge-base/05_reglas_de_negocio.md` §RN-CONF-01/02/03
  - `knowledge-base/04_modelo_de_datos.md` §MensajeWhatsApp

---

### [C-09] `sobreturnos-lista-espera`
- **Estado**: `[ ]` pendiente
- **Scope**: Sobreturnos con tope + waitlist con reclamo único atómico (diferenciador v1)
  - `POST /sobreturnos` con flag `es_sobreturno=true`: valida tope diario/profesional parametrizable (número provisorio, pregunta abierta) y nunca desplaza ni solapa turno regular (RN-SOB-01/02, US-030 CA-1/CA-2); rechazo con mensaje + sugerencia de lista de espera
  - `GET/POST /lista-espera` (alta con `ventana_desde/hasta`) + oferta automática ante cancelación ≥24h (RN-SOB-04); enlaces de reclamo con `token_reclamo_unico`: el primero ocupa el hueco, los demás caducan, con actualización atómica ante doble reclamo concurrente (RN-SOB-03, US-031 CA-1/CA-2)
  - Migración 005: `lista_espera (estado: activa|ofrecida|reclamada|vencida, token_reclamo_unico)` + flag/columna sobreturno
  - Tests: tope alcanzado rechaza, doble reclamo concurrente → 1 gana, hueco liberado va primero a espera
- **Dependencias**: C-06
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-030, §US-031
  - `knowledge-base/07_flujos_principales.md` §Flujo 4
  - `knowledge-base/05_reglas_de_negocio.md` §RN-SOB-01/02/03/04
  - `knowledge-base/04_modelo_de_datos.md` §Sobreturno, §ListaEspera
  - `knowledge-base/10_preguntas_abiertas.md` (tope numérico)

---

## FASE 3 — Integraciones y cierre

> C-10 depende de C-07 (cobro conciliado). C-11 depende de C-06 (eventos de turno). C-12 depende de C-06 + C-07. US-040, US-050, US-041.

### [C-10] `factura-arca`
- **Estado**: `[ ]` pendiente
- **Scope**: Factura electrónica ARCA idempotente (atacar homologación temprano)
  - `POST /facturas` desde cobro conciliado: llama a ARCA (homologación primero), guarda `CAE, cae_vto, nro_cbte, tipo_cbte, punto_venta, raw_respuesta`; CAE visible y descargable (RN-FACT-01, US-040 CA-1); reintentos idempotentes por (turno+tipo) sin duplicar comprobantes (RN-FACT-02, US-040 CA-2)
  - Configuración fiscal única auditable (`ARCA_CUIT/PTO_VTA/CERT/KEY`, RN-FACT-03; punto de venta y tipos de comprobante provisorios hasta respuesta del dueño/contador)
  - Ante ARCA caído: factura en `error` + reintento manual; nunca bloquea la reserva
  - Migración 006: tabla `factura`; Tests: doble emisión no duplica, CAE guardado, fallo ARCA → `error` recuperable
- **Dependencias**: C-07
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-040
  - `knowledge-base/07_flujos_principales.md` §Flujo 5
  - `knowledge-base/11_pagos_facturacion_e_integraciones.md` §ARCA (riesgo homologación)
  - `knowledge-base/05_reglas_de_negocio.md` §RN-FACT-01/02/03
  - `knowledge-base/04_modelo_de_datos.md` §Factura

---

### [C-11] `sync-google-calendar`
- **Estado**: `[ ]` pendiente
- **Scope**: Sync de agenda por profesional con OAuth (alcance provisorio: escritura)
  - Conexión OAuth por profesional (`GCAL_CLIENT_ID/SECRET`, `calendar_id` dedicado, `refresh_token` cifrado en reposo — US-050 CA-1); alta/cancelación/reprogramación de turno refleja en GCal (US-050 CA-2, RN-INT-01)
  - Alcance provisorio solo-escritura hasta responder pregunta abierta (bidireccional con conflictos queda abierta); reintento con backoff ante cuota/error Google
  - Migración 007: `gcal_sync (profesional_id único, tokens cifrados, ultima_sync_en, estado)`; Tests: alta refleja evento, cancelación elimina/marca, token cifrado, fallo Google no rompe el turno
- **Dependencias**: C-06
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-050
  - `knowledge-base/07_flujos_principales.md` §Flujo 1 (paso 5) + §Flujo 2 (paso 4)
  - `knowledge-base/11_pagos_facturacion_e_integraciones.md` §Google Calendar
  - `knowledge-base/05_reglas_de_negocio.md` §RN-INT-01
  - `knowledge-base/04_modelo_de_datos.md` §GCalSync

---

### [C-12] `reportes-basicos`
- **Estado**: `[ ]` pendiente
- **Scope**: Tres reportes mínimos con filtros (cierre del MVP)
  - `GET /reportes?tipo=ocupacion|ausentismo|cobros&desde=&hasta=&profesional=`: ocupación por profesional/sillón/período, ausentismo (ausente ≠ cancelado, RN-REP-02), cobros conciliados con señas (RN-REP-01/02, US-041 CA-1/CA-2)
  - Página `/reportes` con filtros fecha+profesional y exportable simple (CSV); rol recepcionista solo lectura, dueño lectura+exportación
  - Tests: filtros por período/profesional, ausente vs cancelado se distinguen, cobros cuadran con `PagoSena`
- **Dependencias**: C-06, C-07
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §US-041
  - `knowledge-base/07_flujos_principales.md` §Flujo 5 (paso 3)
  - `knowledge-base/05_reglas_de_negocio.md` §RN-REP-01/02
  - `knowledge-base/04_modelo_de_datos.md` §Turno (estados), §PagoSena
  - `knowledge-base/01_vision_y_objetivos.md` §Métricas de éxito
