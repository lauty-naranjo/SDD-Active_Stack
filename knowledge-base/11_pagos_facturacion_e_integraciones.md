# Pagos, Facturación e Integraciones

> Extra de dominio (1X_): detalla las 4 integraciones v1 que el discovery declara obligatorias (MP, ARCA, GCal, WhatsApp manual) y la exclusión consciente de obras sociales.

## Mercado Pago — seña online obligatoria (v1)

- Flujo: pre-reserva `pendiente_sena` → preferencia de pago → webhook → `reservado`.
- Reglas: RN-PAGO-01/02/03. Monto (fijo o %) y timeout de liberación, abiertos (ver `10_preguntas_abiertas.md`).
- Requisitos: `MP_ACCESS_TOKEN` + `MP_WEBHOOK_SECRET`; verificación de firma; idempotencia por `mp_payment_id`.
- Entidad: `PagoSena` (1–1 con Turno) — ver `04_modelo_de_datos.md`.

## ARCA — factura electrónica (v1)

- Flujo: cobro conciliado → emisión → CAE + comprobante guardado; reintento idempotente.
- Reglas: RN-FACT-01/02/03. Riesgo conocido: la homologación puede trabar el semestre (discovery §10, riesgo b) — atacar temprano en ambiente de homologación.
- Requisitos: CUIT, punto de venta, certificado/firma; tipos de comprobante a definir con el dueño/contador.
- Entidad: `Factura` (N–1 con Turno) — ver `04_modelo_de_datos.md`.

## Google Calendar — sync por profesional (v1)

- Flujo: alta/cancelación/reprogramación de turno → reflejo en el calendar del profesional (OAuth por profesional).
- Reglas: RN-INT-01. Alcance exacto (solo escritura vs. bidireccional) abierto.
- Requisitos: `GCAL_CLIENT_ID/SECRET`; `refresh_token` cifrado; `calendar_id` por profesional.
- Entidad: `GCalSync` — ver `04_modelo_de_datos.md`.

## WhatsApp manual desde la app (v1, costo cero)

- Flujo: botón por turno → `wa.me/<tel>?text=<plantilla>` → envío manual → log (quién/cuándo/tipo).
- Reglas: RN-CONF-01/02/03. La API oficial con costo Meta es backlog v2.
- Entidad: `MensajeWhatsApp` (log, sin Message-ID en v1).

## Obras sociales — explícitamente fuera de v1

- Decisión consciente (DD-01, RN-INT-02): sin validación/liquidación OS en v1; radar v2. Referencias de vara: Bilog, DentalTec.
