# Visión y Objetivos

## Propósito del sistema

Sistema de turnos odontológicos para consultorios y clínicas chicas/medianas de Argentina que elimina la gestión manual de agenda por WhatsApp/teléfono, reduciendo turnos perdidos, huecos sin cubrir y ausentismo.

El sistema centraliza la agenda multi-profesional/sillón, expone disponibilidad real con reserva online 24/7, exige seña por Mercado Pago, factura vía ARCA y sincroniza con Google Calendar, operando con costo operativo cero en v1 (WhatsApp manual desde la app).

## Objetivos por actor

| Actor | Objetivo principal | Objetivos secundarios |
|-------|--------------------|-----------------------|
| Paciente | Reservar online 24/7 sin llamar ni escribir | Confirmar / cancelar / reprogramar con 24h; pagar seña online |
| Recepcionista / secretaria | Gestionar agenda multi-profesional sin solapamientos | Confirmar manualmente por WhatsApp (v1); cobrar y conciliar; cubrir huecos con sobreturnos y lista de espera |
| Odontólogo / dueño | Configurar agenda y reglas, ver ocupación y cobros | Definir prestaciones, duraciones, topes y seña; decidir con reportes básicos |

## Alcance v1.0

- Reserva online 24/7 con disponibilidad real por profesional/sillón.
- Agenda diaria/semanal multi-profesional y multi-sillón con duración variable por prestación, bloqueos y anti-solapamiento.
- Confirmación / cancelación / reprogramación por el paciente con 24h de anticipación.
- Sobreturnos con tope por día/profesional + lista de espera para cubrir huecos.
- Confirmación y recordatorio manual desde la app vía WhatsApp (costo cero; API automática en v2).
- Seña online obligatoria por Mercado Pago + facturación electrónica ARCA + sync Google Calendar por profesional.
- Reportes básicos: ocupación, ausentismo y cobros.

## Fuera de alcance

- Odontograma + ficha clínica completa (backlog post-lanzamiento).
- Portal del paciente con historial (backlog).
- Recordatorios automáticos por WhatsApp API (backlog; v1 manuales).
- Campañas de marketing, recuperación de inactivos, reseñas Google (fuera de alcance).
- Liquidación / validación online de obras sociales (radar v2, decisión consciente).
- Multi-sucursal desde el día 1 (pregunta abierta — v1 asume un solo consultorio/sede salvo definición contraria).

## Métricas de éxito

- Reducción de ausentismo vs. línea base manual (objetivo a definir; referencia mercado: -40%/-65% declarado por competidores, no auditado).
- % de turnos reservados online vs. por WhatsApp/teléfono.
- % de huecos cubiertos vía sobreturnos / lista de espera.
- Ocupación por profesional/sillón y cobro efectivo de señas.
