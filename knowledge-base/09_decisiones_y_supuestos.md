# Decisiones y Supuestos

## Decisiones documentadas

### DD-01 — Sin obras sociales en v1
**Decisión**: ninguna integración con obras sociales en v1; va a radar v2.
**Contexto**: Bilog/DentalTec mandan en volumen institucional OS, inalcanzable en un semestre académico.
**Alternativas consideradas**: (a) validación OS mínima; (b) nada de OS.
**Justificación**: el recorte de OS es la defensa contra el riesgo de alcance (discovery §10, riesgo c).
**Trade-offs aceptados**: se resigna el segmento institucional; foco en particulares/consultorio chico.

### DD-02 — WhatsApp manual en v1, API en v2
**Decisión**: confirmación/recordatorio manual desde la app vía `wa.me` (costo cero); API automática con costo Meta en backlog.
**Contexto**: presupuesto cero excluye costo por mensaje o suscripción.
**Alternativas consideradas**: (a) API oficial desde v1; (b) manual v1.
**Justificación**: restricción dura de presupuesto; lo automático es impagable en v1.
**Trade-offs aceptados**: menor diferencial vs. reservar por chat; carga operativa en recepcionista.

### DD-03 — Seña obligatoria atada a la reserva online
**Decisión**: toda reserva online exige seña por Mercado Pago; diferenciador v1.
**Contexto**: ausentismo alto por falta de confirmación sistemática.
**Alternativas consideradas**: (a) seña opcional; (b) seña obligatoria.
**Justificación**: reduce no-shows y es el diferencial declarado del MVP.
**Trade-offs aceptados**: fricción de pago; monto/porcentaje aún abierto.

### DD-04 — Backend propio obligatorio
**Decisión**: el sistema incluye backend con DB propia (no solo frontend + APIs terceras).
**Contexto**: MP exige webhooks, ARCA exige homologación/CAE, GCal exige OAuth/sync.
**Alternativas consideradas**: (a) frontend-only; (b) backend propio.
**Justificación**: ninguna integración es resoluble solo del lado cliente con idempotencia y secretos.
**Trade-offs aceptados**: mayor superficie a desplegar aun con presupuesto cero.

### DD-05 — Clínico pesado fuera de v1
**Decisión**: odontograma/ficha quedan en backlog; antes un portal paciente liviano.
**Contexto**: análisis competitivo: el hueco está en agenda + cobros, no en lo clínico.
**Alternativas consideradas**: (a) odontograma en v1; (b) agenda excelente primero.
**Justificación**: recomendación D del discovery + riesgo de alcance.
**Trade-offs aceptados**: no compite en lo clínico con DentalCore/DentalSoft en v1.

## Supuestos inferidos

### SU-01 — Pacientes adoptan la reserva online
**Supuesto**: los pacientes usarán la web 24/7 en vez de seguir escribiendo por WhatsApp.
**Origen**: discovery §10 (riesgo declarado: supuesto sin probar).
**Riesgo si es falso**: la v1 pierde su diferencial central.
**Cómo validar**: prueba con usuarios reales del consultorio antes del lanzamiento.

### SU-02 — Una sede en v1
**Supuesto**: v1 opera un solo consultorio/sede (multi-sucursal en pregunta abierta).
**Origen**: inferido — discovery no define sede; pregunta abierta §11.
**Riesgo si es falso**: el modelo de datos y la agenda deben soportar multi-sede desde el día 1.
**Cómo validar**: responder pregunta abierta de sede en `10_preguntas_abiertas.md`.

### SU-03 — Catálogo de prestaciones validable
**Supuesto**: existe un odontólogo real que validará prestaciones y duraciones.
**Origen**: discovery §10 (riesgo: huecos irreales sin validación).
**Riesgo si es falso**: la disponibilidad real es ficticia.
**Cómo validar**: conseguir referente clínico en sprint 1.
