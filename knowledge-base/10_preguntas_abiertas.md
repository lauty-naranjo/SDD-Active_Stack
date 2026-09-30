# Preguntas Abiertas

## Inconsistencias detectadas

Ninguna contradicción dura entre `docs/discovery/informe-discovery.md` (primaria) y `informe-discovery.pdf` (secundaria, mismo contenido). Discrepancia potencial a vigilar: si el PDF difiriera en precios/matriz de la Sección A–B, vale la versión del `.md` (fuente primaria con fecha 2026-09-29).

## Preguntas abiertas (priorizadas)

| Prioridad | Pregunta | Bloquea | Decisor |
|-----------|----------|---------|---------|
| Alta | Monto de la seña: ¿fijo o porcentaje del tratamiento? ¿Cuánto? | Pagos / US-002 | Dueño |
| Alta | Tope numérico de sobreturnos por día/profesional: ¿cuántos? | Agenda / US-030 | Dueño |
| Alta | Catálogo inicial de prestaciones con duraciones: ¿validado con quién? | Agenda real / US-010 | Odontólogo referente |
| Alta | ¿Una sede o multi-sucursal en v1? (KB asume sede única) | Modelo de datos | Dueño |
| Alta | Identificación del paciente: ¿DNI o alcanza nombre + teléfono? | Modelo Paciente | Dueño |
| Media | Timeout de liberación de `pendiente_sena`: ¿cuántos minutos? | US-002 | Equipo técnico |
| Media | Alcance del sync GCal: ¿solo escritura o bidireccional con conflictos? | US-050 | Equipo técnico |
| Media | [DISCOVERY] `system_type` could not be inferred with confidence from the source docs. Please confirm: ¿qué tipo de sistema se construirá (web_app con panel + reserva pública, u otro)? Valor provisional: `web_app (inferred, low confidence)`. Contexto: proyecto académico, presupuesto cero, sin stack impuesto. | Arquitectura / roadmap | Equipo técnico |
| Media | [DISCOVERY] `stack` could not be inferred with confidence from the source docs. Please confirm: ¿qué stack (lenguaje, framework, DB, hosting gratuito) se usará? Valor provisional: `Por definir (inferred, low confidence)`. Contexto: proyecto académico, presupuesto cero, sin stack impuesto. | Implementación | Equipo técnico |
| Baja | Punto de venta y tipos de comprobante ARCA del consultorio | US-040 | Dueño / contador |
| Baja | ¿Precio publicado y onboarding en minutos como arma comercial en v1? | Lanzamiento | Dueño |
