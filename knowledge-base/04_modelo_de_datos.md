# Modelo de Datos

## Dominios

- **Agenda**: profesionales, sillones, prestaciones, franjas, bloqueos, turnos, sobreturnos.
- **Pacientes**: identificación liviana v1 (nombre + teléfono; DNI en pregunta abierta).
- **Pagos y facturación**: señas (Mercado Pago), facturas (ARCA).
- **Integraciones**: sync Google Calendar por profesional, mensajes WhatsApp manuales.
- **Espera**: lista de espera y reclamos de huecos.

## ERD (Entity Relationship Diagram)

```
Sede (1)──< Profesional (1)──< FranjaHoraria / Bloqueo
  │              │
  │              └──< Turno >── Paciente
  │                     │  ├── PagoSena (MP) 1..1
  │                     │  └── Factura (ARCA) 0..n
  ├──< Sillon (1)──┘ (Turno ocupa 1 Profesional + 1 Sillón en franja)
  ├──< Prestacion (duración propia)──┘
  └──< ListaEspera >── Paciente (reclamo único de hueco)
Profesional (1)──< GCalSync (token OAuth + calendarId + última sync)
Turno (1)──< MensajeWhatsApp (manual, log de confirmación/recordatorio)
```

Regla estructural: un turno ocupa exactamente un (profesional, sillón, intervalo [inicio, fin)); dos turnos no pueden solaparse en el mismo profesional ni en el mismo sillón (RN-AGEN-01).

## Entidades

### Paciente
- Atributos: id, nombre, teléfono, dni (nullable — pendiente decisión IDENT), email (nullable), creado_en.
- Relaciones: 1 Paciente — N Turnos; 1 Paciente — N entradas ListaEspera.
- Constraints: teléfono obligatorio (canal WhatsApp manual); unicidad (teléfono) o (dni) según decisión IDENT.
- Índices: teléfono, dni.

### Profesional
- Atributos: id, nombre, especialidad, sede_id, gcal_calendar_id (nullable), activo.
- Relaciones: 1 — N FranjaHoraria, Bloqueo, Turno; 1 — 1 GCalSync.
- Constraints: activo=false oculta disponibilidad futura sin borrar historial.

### Sillon
- Atributos: id, sede_id, nombre, activo.
- Relaciones: 1 — N Turnos (anti-solapamiento por sillón).
- Constraints: v1 asume una sede (multi-sucursal en pregunta abierta).

### Prestacion
- Atributos: id, nombre, duración_min (ej. limpieza 30, conducto 90), seña_monto o seña_porcentaje (nullable — monto a definir), activa.
- Relaciones: 1 — N Turnos.
- Constraints: duración_min > 0; catálogo validado con odontólogo real (riesgo discovery §10).

### Turno
- Atributos: id, paciente_id, profesional_id, sillon_id, prestacion_id, inicio, fin (derivado: inicio + duración), estado (pendiente_sena | reservado | confirmado | cancelado | ausente | atendido), origen (online | mostrador), token_publico, creado_en.
- Relaciones: N — 1 con Paciente/Profesional/Sillón/Prestación; 1 — 1 PagoSena; 1 — N Factura; 1 — N MensajeWhatsApp.
- Constraints: fin > inicio; sin solapamiento por (profesional, intervalo) ni (sillón, intervalo); cancelación/reprogramación solo con ≥24h (RN-TUR-01); sobreturno marcado con flag + tope (RN-SOB-01).
- Índices: (profesional_id, inicio), (sillon_id, inicio), estado, token_publico (único).

### Sobreturno
- Modelado como Turno con `es_sobreturno=true` + validación de tope por día/profesional (número a definir).
- Constraints: tope diario por profesional; nunca desplaza un turno regular.

### ListaEspera
- Atributos: id, paciente_id, profesional_id (nullable), prestacion_id, ventana_desde/hasta, estado (activa | ofrecida | reclamada | vencida), token_reclamo_unico.
- Relaciones: N — 1 Paciente/Profesional/Prestación.
- Constraints: token de reclamo único e irrepetible (patrón ASAP adaptado a costo cero).

### PagoSena (Mercado Pago)
- Atributos: id, turno_id (único), mp_preference_id, mp_payment_id, monto, estado (pendiente | acreditada | devuelta), pagado_en.
- Relaciones: 1 — 1 Turno.
- Constraints: reserva online exige seña acreditada (RN-PAGO-01); idempotencia por webhook.

### Factura (ARCA)
- Atributos: id, turno_id, tipo_cbte, punto_venta, nro_cbte, cae, cae_vto, monto, estado (pendiente | emitida | error), raw_respuesta.
- Relaciones: N — 1 Turno.
- Constraints: no emitir duplicados ante reintento (idempotencia por turno + tipo).

### Bloqueo
- Atributos: id, profesional_id (nullable), sillon_id (nullable), inicio, fin, motivo.
- Relaciones: bloquea disponibilidad (la agenda lo resta antes de mostrar huecos).

### GCalSync
- Atributos: id, profesional_id (único), oauth_refresh_token (sensible), calendar_id, ultima_sync_en, estado.
- Constraints: refresh_token cifrado en reposo.

### MensajeWhatsApp
- Atributos: id, turno_id, tipo (confirmacion | recordatorio | ofrecimiento_hueco), canal (manual_wa_me), enviado_por, enviado_en.
- Nota v1: log de envío manual (sin Message-ID de API); en v2 se agrega `proveedor_message_id`.

## Seed data inicial

- 1 sede ("Consultorio demo — sede única v1").
- 2 profesionales + 2 sillones (para probar multi-profesional/sillón y anti-solapamiento).
- Catálogo mínimo de prestaciones con duraciones (limpieza 30', consulta 20', conducto 90' — a validar).
- 1 usuario recepcionista + 1 odontólogo/dueño; horarios base Lun–Vie + bloqueos de ejemplo.
