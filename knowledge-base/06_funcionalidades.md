# Funcionalidades

Organizadas por **épica** y luego por **historia de usuario** (formato US-NNN).

## Épica 1: Reserva online 24/7

### US-001 — Ver disponibilidad real y reservar online
**Como** paciente
**Quiero** ver horarios libres reales por profesional/sillón y reservar 24/7
**Para** no depender del horario de secretaría

**Criterios de aceptación**:
- [ ] CA-1: La grilla muestra solo huecos reales (franja − turnos − bloqueos).
- [ ] CA-2: La reserva crea el turno con fin = inicio + duración de la prestación.
- [ ] CA-3: Sin disponibilidad no se ofrece el horario (ni overbooking silencioso).

**Reglas relacionadas**: RN-TUR-02, RN-TUR-03, RN-AGEN-01, RN-AGEN-02, RN-AGEN-03

### US-002 — Pagar seña obligatoria al reservar
**Como** paciente
**Quiero** pagar la seña online al reservar
**Para** asegurar mi turno

**Criterios de aceptación**:
- [ ] CA-1: Sin seña acreditada el turno queda `pendiente_sena` y el horario se libera tras timeout.
- [ ] CA-2: El webhook MP es idempotente (doble notificación no duplica turno).
- [ ] CA-3: El paciente recibe comprobante de seña.

**Reglas relacionadas**: RN-PAGO-01, RN-PAGO-02, RN-PAGO-03

## Épica 2: Gestión de agenda multi-profesional/sillón

### US-010 — Agenda diaria/semanal sin solapamientos
**Como** recepcionista
**Quiero** ver y gestionar la agenda diaria/semanal multi-profesional y multi-sillón
**Para** operar el consultorio sin choques

**Criterios de aceptación**:
- [ ] CA-1: Vista día y semana por profesional y por sillón.
- [ ] CA-2: El sistema rechaza cualquier alta que solape profesional o sillón.
- [ ] CA-3: Crear, mover y reasignar turnos respeta duraciones y bloqueos.

**Reglas relacionadas**: RN-AGEN-01, RN-AGEN-02, RN-AGEN-04

### US-011 — Bloqueos de agenda
**Como** odontólogo/dueño
**Quiero** crear bloqueos con motivo (ausencia, feriado, mantenimiento)
**Para** que no se ofrezcan esos horarios

**Criterios de aceptación**:
- [ ] CA-1: El bloqueo resta disponibilidad inmediatamente.
- [ ] CA-2: Motivo obligatorio y visible en agenda.

**Reglas relacionadas**: RN-AGEN-03

### US-012 — Configurar prestaciones y reglas
**Como** odontólogo/dueño
**Quiero** configurar prestaciones, duraciones, topes, seña y horarios
**Para** que la agenda refleje mi operatoria real

**Criterios de aceptación**:
- [ ] CA-1: CRUD de prestaciones con duración y seña.
- [ ] CA-2: Configuración de topes de sobreturnos y ventana 24h visible.

**Reglas relacionadas**: RN-AGEN-02, RN-SOB-01, RN-PAGO-01

## Épica 3: Confirmación / cancelación / reprogramación

### US-020 — Confirmar, cancelar o reprogramar con 24h
**Como** paciente
**Quiero** confirmar/cancelar/reprogramar mi turno con 24h de anticipación
**Para** liberar el horario a tiempo si no puedo ir

**Criterios de aceptación**:
- [ ] CA-1: Dentro de la ventana (<24h) la app rechaza cancelación/reprogramación con mensaje claro.
- [ ] CA-2: La cancelación válida libera el hueco y dispara oferta a lista de espera.
- [ ] CA-3: Acceso por enlace con token (sin cuenta obligatoria en v1).

**Reglas relacionadas**: RN-TUR-01, RN-TUR-04, RN-SOB-04

### US-021 — Confirmación manual por WhatsApp desde la app
**Como** recepcionista
**Quiero** confirmar/recordar turnos por WhatsApp manual desde la app (costo cero)
**Para** bajar el ausentismo sin pagar API

**Criterios de aceptación**:
- [ ] CA-1: Botón por turno que abre `wa.me` con plantilla precargada.
- [ ] CA-2: Queda log de mensaje enviado (quién, cuándo, tipo).
- [ ] CA-3: Ningún flujo exige API de WhatsApp en v1.

**Reglas relacionadas**: RN-CONF-01, RN-CONF-02, RN-CONF-03

## Épica 4: Sobreturnos y lista de espera

### US-030 — Sobreturnos con tope
**Como** recepcionista
**Quiero** crear sobreturnos con tope por día/profesional
**Para** atender demanda sin saturar

**Criterios de aceptación**:
- [ ] CA-1: Superado el tope, el sistema rechaza el sobreturno.
- [ ] CA-2: El sobreturno se marca y nunca desplaza un turno regular.

**Reglas relacionadas**: RN-SOB-01, RN-SOB-02

### US-031 — Lista de espera con reclamo único
**Como** paciente
**Quiero** anotarme en lista de espera y reclamar huecos liberados
**Para** conseguir turno antes

**Criterios de aceptación**:
- [ ] CA-1: Al liberarse un hueco se ofrece primero a la lista de espera.
- [ ] CA-2: El enlace de reclamo es único: el primero que lo usa ocupa el hueco, los demás caducan.

**Reglas relacionadas**: RN-SOB-03, RN-SOB-04

## Épica 5: Facturación y reportes

### US-040 — Facturar con ARCA
**Como** recepcionista
**Quiero** emitir factura electrónica ARCA del cobro
**Para** cumplir con facturación sin salir del sistema

**Criterios de aceptación**:
- [ ] CA-1: Emisión con CAE visible y descargable.
- [ ] CA-2: Reintentos idempotentes (sin duplicados).

**Reglas relacionadas**: RN-FACT-01, RN-FACT-02, RN-FACT-03

### US-041 — Reportes básicos
**Como** dueño
**Quiero** ver ocupación, ausentismo y cobros por profesional y período
**Para** decidir sobre agenda y precios

**Criterios de aceptación**:
- [ ] CA-1: Tres reportes mínimos con filtros por fecha y profesional.
- [ ] CA-2: Ausente y cancelado se distinguen en el reporte.

**Reglas relacionadas**: RN-REP-01, RN-REP-02

## Épica 6: Sincronización Google Calendar

### US-050 — Sync de agenda por profesional
**Como** odontólogo
**Quiero** sincronizar mi agenda con Google Calendar
**Para** ver mis turnos junto al resto de mi calendario

**Criterios de aceptación**:
- [ ] CA-1: Conexión OAuth por profesional con calendar dedicado.
- [ ] CA-2: Alta/cancelación de turno se refleja en GCal.

**Reglas relacionadas**: RN-INT-01

## Backlog explícito (no v1)

- Odontograma + ficha clínica · Portal del paciente · Recordatorios automáticos WhatsApp API · Obras sociales v2 · Campañas/recuperación inactivos (fuera de alcance).
