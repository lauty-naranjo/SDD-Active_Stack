# Descripción General

## Stack tecnológico

> Stack no impuesto por el discovery (proyecto académico, Metodología I, presupuesto cero). Valores best-effort de bajo nivel de confianza — ver `10_preguntas_abiertas.md` ([DISCOVERY] `stack`).

| Capa | Tecnologías | Versión mínima |
|------|-------------|----------------|
| Frontend web | A definir (web responsive para reserva pública + panel interno) | — |
| Backend API | A definir (exigido por MP/ARCA/GCal: webhooks, CAE, OAuth) | — |
| Base de datos | A definir (relacional sugerida por agenda transaccional + anti-solapamiento) | — |
| Infra / despliegue | Tier gratuito, costo cero (v1 sin suscripciones ni costo por mensaje) | — |

## Arquitectura general

```
Paciente (web pública 24/7) ─┐
Recepcionista / Odontólogo ──┼──► Frontend web ──► Backend API ──► DB relacional
(panel interno + agenda) ────┘                          │
                                                        ├──► Mercado Pago (seña)
                                                        ├──► ARCA (factura electrónica)
                                                        └──► Google Calendar (sync por profesional)
                                                             └──► WhatsApp manual (deep-link wa.me, sin API en v1)
```

Aplicación web multi-actor con backend propio obligatorio: las integraciones MP (webhooks de pago), ARCA (homologación + CAE) y Google Calendar (OAuth + sync) no son resolubles solo del lado cliente. La v1 evita todo costo recurrente: WhatsApp es manual (la recepcionista confirma desde la app vía enlace) y la API automática con costo Meta queda para v2.

## Integraciones externas

| Servicio | Propósito | Tipo |
|----------|-----------|------|
| Mercado Pago | Cobro de seña online obligatoria atada a la reserva | SDK / REST + webhooks |
| ARCA | Facturación electrónica (comprobantes con CAE) | WS / REST (homologación) |
| Google Calendar | Sincronización de agenda por profesional | REST (OAuth 2.0 + Calendar API) |
| WhatsApp (v1 manual) | Confirmación/recordatorio manual desde la app, costo cero | Deep-link `wa.me` (sin API) |
| WhatsApp API (v2) | Recordatorios automáticos | API oficial Meta (backlog, con costo) |

Detalle operativo en `11_pagos_facturacion_e_integraciones.md`. Sin integración con obras sociales en v1 (decisión consciente; radar v2).

## API REST

Recursos principales (agrupados, sin diseño definitivo):

- `GET /disponibilidad?profesional=&sillon=&prestacion=&desde=&hasta=` — horarios libres reales.
- `POST /turnos` (crea + exige seña) · `POST /turnos/:id/confirmar|juar cancelar|/reprogramar` (ventana 24h).
- `GET/POST /agenda` (vista diaria/semanal multi-profesional/sillón, bloqueos, sobreturnos).
- `GET/POST /lista-espera` (alta + reclamo único de hueco).
- `POST /pagos/sena` + `POST /pagos/webhook` (Mercado Pago) · `POST /facturas` (ARCA).
- `POST /integraciones/gcal/sync` · `GET /reportes?tipo=ocupacion|ausentismo|cobros`.
