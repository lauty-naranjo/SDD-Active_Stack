# Turnos Odontológicos — Base de Conocimiento

Base de conocimiento generada por ingesta silenciosa (Mode A) desde `docs/discovery/informe-discovery.md` (fuente primaria) y `docs/discovery/informe-discovery.pdf` (secundaria), más la sección `discovery` de `.active-orchestrator-state.json`.

## Índice de Archivos

| Archivo | Contenido |
|---------|-----------|
| [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito, objetivos por actor, alcance v1.0, fuera de alcance, métricas |
| [02_descripcion_general.md](02_descripcion_general.md) | Stack (a definir), arquitectura, 4 integraciones v1, API REST |
| [03_actores_y_roles.md](03_actores_y_roles.md) | Paciente, recepcionista, odontólogo/dueño; RBAC; rutas públicas |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | 11 entidades, ERD, anti-solapamiento, seed mínima |
| [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | 25 reglas RN-TUR/AGEN/SOB/CONF/PAGO/FACT/INT/REP/GLB |
| [06_funcionalidades.md](06_funcionalidades.md) | 6 épicas, 11 US (US-001…US-050) con CA y reglas |
| [07_flujos_principales.md](07_flujos_principales.md) | Reserva con seña, ventana 24h, WA manual, sobreturno/espera, cobro-factura |
| [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones, directorios, seguridad, env vars |
| [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | 5 DD (OS fuera, WA manual, seña, backend, backlog clínico) + 3 SU |
| [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | 5 abiertas del discovery + técnicas + 2 [DISCOVERY] (system_type, stack) |
| [11_pagos_facturacion_e_integraciones.md](11_pagos_facturacion_e_integraciones.md) | Extra: MP + ARCA + GCal + WA manual; OS fuera de v1 |

## Quick Start para Desarrolladores

1. Entender el dominio → [01](01_vision_y_objetivos.md), [03](03_actores_y_roles.md)
2. Entender los datos → [04](04_modelo_de_datos.md)
3. Entender las reglas → [05](05_reglas_de_negocio.md)
4. Entender la arquitectura → [02](02_descripcion_general.md), [08](08_arquitectura_propuesta.md)
5. Implementar → [07](07_flujos_principales.md), [06](06_funcionalidades.md)
6. Antes de codificar → [10](10_preguntas_abiertas.md)

## Resumen Ejecutivo

Sistema de turnos odontológicos que reemplaza la agenda manual por WhatsApp con reserva online 24/7, agenda multi-profesional/sillón sin solapamientos, seña por Mercado Pago, factura ARCA y sync con Google Calendar — con costo operativo cero en v1 y obras sociales/clínico pesado en backlog.
