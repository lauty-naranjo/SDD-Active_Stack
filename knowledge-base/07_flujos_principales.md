# Flujos Principales

Cada flujo se documenta extremo a extremo, mostrando interacciones entre componentes.

## Flujo 1: Reserva online con seña

**Disparador**: paciente entra a la web pública 24/7
**Actor**: Paciente

**Pasos**:
1. [Frontend] muestra prestaciones y profesionales/sillones con disponibilidad real (franja − turnos − bloqueos).
2. [Paciente] elige horario → [Frontend] crea pre-reserva (`pendiente_sena`).
3. [Backend] genera preferencia Mercado Pago → [Paciente] paga.
4. [Mercado Pago] notifica por webhook → [Backend] acredita seña (idempotente) y pasa el turno a `reservado`.
5. [Backend] escribe el turno en Google Calendar del profesional y envía enlace de gestión (confirmar/cancelar/reprogramar).

**Diagrama de secuencia** (ASCII):
```
Paciente → Frontend → API → DB (pre-reserva pendiente_sena)
Paciente → MP (paga) → Webhook → API → DB (reservado)
API → GCal (sync) ; API → Paciente (enlace con token)
```

**Casos de error**:
- Pago no acreditado en timeout → se libera el horario (RN-PAGO-03).
- Webhook duplicado → se ignora por idempotencia (RN-PAGO-02).
- Hueco tomado en concurrente → se rechaza la segunda reserva (RN-AGEN-01).

## Flujo 2: Confirmación / cancelación / reprogramación (ventana 24h)

**Disparador**: paciente abre su enlace de turno o recepcionista lo gestiona
**Actor**: Paciente / Recepcionista

**Pasos**:
1. [Actor] solicita confirmar / cancelar / reprogramar.
2. [Backend] valida ventana: si faltan <24h para el inicio, rechaza cancelación/reprogramación (RN-TUR-01).
3. [Backend] actualiza estado y, si se liberó un hueco, ofrece primero a la lista de espera (RN-SOB-04).
4. [Backend] sincroniza el cambio con Google Calendar.

**Casos de error**:
- Intento fuera de ventana → mensaje claro + opción de contactar al consultorio.
- Hueco de reprogramación ocupado → se ofrece lista de espera.

## Flujo 3: Confirmación manual por WhatsApp (v1, costo cero)

**Disparador**: recepcionista repasa agenda del día siguiente
**Actor**: Recepcionista

**Pasos**:
1. [Panel] lista turnos pendientes de confirmación con botón WhatsApp por turno.
2. [Recepcionista] pulsa → se abre `wa.me/<tel>?text=<plantilla con turno>` (RN-CONF-01/03).
3. [Recepcionista] envía desde su WhatsApp → [Backend] registra log (quién, cuándo, tipo).
4. [Paciente] responde por WhatsApp → [Recepcionista] marca confirmado en el panel.

**Casos de error**:
- Paciente no responde → el turno sigue pendiente; se reintenta manual o se libera según regla del consultorio.
- Sin API en v1: ningún paso automático depende de Meta (RN-CONF-02).

## Flujo 4: Sobreturno + lista de espera (reclamo único)

**Disparador**: agenda llena o cancelación que libera hueco
**Actor**: Recepcionista / Paciente en espera

**Pasos**:
1. [Recepcionista] crea sobreturno → [Backend] valida tope diario/profesional (RN-SOB-01/02).
2. Ante cancelación válida, [Backend] ofrece el hueco a la lista de espera con enlaces de reclamo único.
3. [Primer paciente] que reclama ocupa el hueco; los demás enlaces caducan (RN-SOB-03).

**Casos de error**:
- Tope alcanzado → rechazo con mensaje + sugerencia de lista de espera.
- Doble reclamo concurrente → solo el primero ocupa (token único atómico).

## Flujo 5: Cobro, factura ARCA y reportes

**Disparador**: seña acreditada o cobro en mostrador
**Actor**: Recepcionista / Dueño

**Pasos**:
1. [Backend] concilia pago MP con turno (PagoSena).
2. [Recepcionista] emite factura → [Backend] llama a ARCA → guarda CAE y comprobante (RN-FACT-01/02).
3. [Dueño] consulta reportes de ocupación, ausentismo y cobros por profesional/período (RN-REP-01/02).

**Casos de error**:
- ARCA caído o homologación pendiente → factura en `error`, reintento idempotente sin duplicar (RN-FACT-02).
- Pago sin turno asociado → bandeja de conciliación manual.
