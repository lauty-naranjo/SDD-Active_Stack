# Discovery — Sistema de turnos odontológicos (Argentina)

**Fecha**: 2026-09-29
**Fuentes investigadas**: 23 sistemas (8 Argentina + 8 LatAm + 7 internacionales) con fuentes verificables — sitios oficiales, documentación pública, páginas de precios, centros de ayuda y reseñas verificadas. Sin scraping automático (`web-scraper` no disponible en esta corrida); relevamiento vía investigación directa con URL y fecha de consulta por ficha.
**Regla**: solo funcionalidad demostrada públicamente. Lo no demostrado figura como "No evidenciado". Las cifras de adopción/eficacia de los proveedores se tratan como afirmación comercial no auditada.

## 1. Problema que resuelve

Los consultorios y clínicas odontológicas chicas/medianas coordinan turnos por WhatsApp y teléfono de forma manual, lo que genera pérdida de turnos, huecos sin cubrir y ausentismo alto por falta de confirmación y recordatorios sistemáticos.

## 2. Usuarios / roles

- **Paciente**: reserva un turno online sin llamar ni escribir, confirma/cancela/reprograma y paga la seña.
- **Recepcionista/secretaria**: gestiona la agenda multi-profesional, confirma turnos manualmente (v1), cobra y concilia.
- **Odontólogo/dueño**: configura agenda y prestaciones, ve ocupación y cobros, define reglas (antelación, seña, topes).

## 3. Casos de uso

1. Como paciente, quiero ver horarios libres reales y reservar online 24/7 para no depender del horario de secretaría.
2. Como paciente, quiero confirmar/cancelar/reprogramar con 24h de anticipación para liberar el horario a tiempo.
3. Como recepcionista, quiero una agenda multi-profesional/sillón sin solapamientos, con sobreturnos acotados y lista de espera, para cubrir huecos.
4. Como odontólogo, quiero cobrar seña por Mercado Pago y facturar (ARCA) sin salir del sistema.
5. Como dueño, quiero ver ocupación, ausentismo y cobros para decidir (reportes básicos).

## 4. Competidores / soluciones existentes

Resumen ejecutivo. Fichas completas con URL + fecha de consulta en la Sección A.

| # | Sistema / Origen | Segmento | Precio publicado |
|---|---|---|---|
| 1 | DentalSoft (AR) | Consultorio/clínica PyME | ARS 0 / 30k / 50k / 75k por mes |
| 2 | DentalCore (AR) | Consultorio a multi-sucursal | USD 50 + 10 por usuario/mes |
| 3 | Bilog (AR) | Consultorio/clínica/institución | Freemium; resto a cotización |
| 4 | DentalTec (AR) | Odontólogo/institución/círculos | No publica (demo) |
| 5 | Odonthia (AR) | Independiente/equipo chico | Gratis / ARS 20,9k / 46,9k |
| 6 | Dentalink (CL, opera AR) | Clínica mediana/grande, cadenas | No publica (cotización) |
| 7 | Dentiqa (LatAm, opera AR) | Clínica/cadena | USD 89 / 149 / 249 por mes |
| 8 | Dentaly (AR) | Independiente/clínica | ARS 35k / 100k / custom |
| 9 | Dentatools (AR) | Particulares sin OS | $30.000/mes hasta 3 odontólogos |
| 10 | ClinIA (AR) | Institucional/hospitalario | No publica (demo a medida) |
| 11 | Doctocliq (PE) | Independiente a multi-sede | Gratis / USD 19 / 29 / 49 |
| 12 | Dentidesk (CL) | Clínicas, sindicatos, universidades | No publica (trial 15 días) |
| 13 | AgendaPro (CL/MX) | Belleza-salud, vertical dental | No publica vertical dental |
| 14 | Doctoralia Pro (ES/MX/CL) | Especialistas, clínicas | CLP 59k/89k; MX a cotización |
| 15 | Nimbo (MX) | Consultorio a red dental | Desde MXN 175 anual + módulos |
| 16 | Simples Dental (BR) | Consultorios/clínicas BR | BRL, a consultar (trial 7 días) |
| 17 | Medesk (Intl, MX/CO) | Consultorios, clínicas, IPS | Gratis / USD 16 por 50 citas |

**Notas**: DentalSoft es el competidor más directo (mismo segmento, cobertura funcional AR más completa). DentalTec/Bilog mandan en volumen institucional de obras sociales. Odonthia/Dentatools son el piso gratuito sin OS. Doctoralia, NexHealth, Doctolib, Open Dental, Curve y Dentally son referencias de UX/agenda, no competidores clínicos directos.

## 5. Funcionalidades necesarias

- Reserva de turno online 24/7 con disponibilidad real por profesional/sillón.
- Agenda diaria/semanal multi-profesional y multi-sillón, con duración variable por prestación, bloqueos y prevención de solapamientos.
- Confirmación/cancelación/reprogramación por el paciente con 24h de anticipación.
- Sobreturnos con tope por día/profesional + lista de espera para cubrir huecos.
- Confirmación y recordatorio manual desde la app (costo cero; WhatsApp API queda para v2).
- Cobro de seña online (Mercado Pago) + facturación (ARCA) + reportes básicos de ocupación y cobros.

## 6. Funcionalidades opcionales

- Odontograma + ficha clínica completa (backlog post-lanzamiento).
- Portal del paciente con historial de turnos (backlog).
- Recordatorios automáticos pagos/WhatsApp API (backlog; v1 manuales).
- Fuera de alcance por ahora: campañas de marketing, recuperación de inactivos, reseñas Google, liquidación/validación online de obras sociales (esto último, radar v2).

## 7. Reglas de negocio

- No se puede cancelar ni reprogramar con menos de 24 horas de anticipación.
- Cada prestación tiene duración propia (ej. limpieza 30', conducto 90'); la agenda no permite solapamientos en el mismo profesional/sillón.
- La reserva online exige seña obligatoria (monto a definir en `kb-creator`).
- Los sobreturnos tienen tope por día y por profesional (número a definir en `kb-creator`).

## 8. Integraciones

- WhatsApp manual desde la app en v1 (costo cero; la recepcionista confirma) — API automática con costo Meta en v2.
- Mercado Pago para seña online (obligatoria v1).
- Facturación electrónica ARCA (obligatoria v1).
- Google Calendar, sincronización por profesional (obligatoria v1).
- Ninguna integración con obras sociales en v1 (decisión consciente; va a v2).

## 9. Restricciones

- Presupuesto cero: solo servicios gratuitos (WhatsApp manual, tiers free de APIs, infra sin costo).
- Proyecto académico (Metodología I), sin plazo duro ni stack impuesto.
- Todo lo que implique costo por mensaje o suscripción paga queda fuera de la v1 por definición.

## 10. Riesgos

- **Supuesto sin probar**: que los pacientes adopten la reserva online en vez de seguir escribiendo por WhatsApp por costumbre — no validado con usuarios reales.
- **Riesgo (a)**: WhatsApp automático es impagable con presupuesto cero; la v1 manual puede percibirse como poco diferencial frente a reservar por chat.
- **Riesgo (b)**: ARCA puede trabar el semestre por complejidad técnica (homologación gratuita pero no trivial).
- **Riesgo (c)**: el alcance (agenda multi-sillón + 4 integraciones + pagos) puede no entrar en los tiempos de cursada — el recorte de OS y de lo clínico es la defensa.
- **Riesgo**: si no se valida el catálogo de prestaciones/duraciones con un odontólogo real, la agenda muestra huecos irreales.

## 11. Preguntas abiertas

- ¿Monto de la seña? ¿Fijo o porcentaje del tratamiento?
- ¿Tope numérico de sobreturnos por día/profesional?
- ¿Catálogo inicial de prestaciones con duraciones (validado con quién)?
- ¿Un solo consultorio/sede en v1, o multi-sucursal desde el día 1?
- ¿El paciente se identifica con DNI, o alcanza nombre + teléfono?

---

# A. Tabla comparativa (17 sistemas, ordenados por relevancia para Argentina)

| # | Producto / Empresa / País / URL (consulta 2026-09-29) | Segmento / Modalidad | Agenda | Turnos digitales | Automatización | Clínico | Admin/cobros | Integraciones locales | Precio |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **DentalSoft** — DentalSoft, AR — dentalsoft.com.ar | Indep./clínica PyME / SaaS nube | Diaria/semanal/mensual, multi-prof., sobreturnos con anti-solapamiento, bloqueos | Web propia 24/7 + portal paciente, confirma por WhatsApp | Recordatorios auto WA/email, reactivación inactivos, IA recepcionista (plan alto) | Odontograma 18 estados FDI, ortodoncia, presupuestos con OS, consentimientos | Caja + MP + liquidación OS y comisiones, KPI tiempo real | GCal, WA, MP / API y ARCA: No evidenciado | ARS 0/30k/50k/75k |
| 2 | **DentalCore** — Di Tullio, La Plata AR — dentalcore.app | Cons./multi-sucursal / SaaS FHIR | Multi-doctor drag&drop, confirma WA, auto-relleno huecos | Portal 24/7 + bot + teleodontología | 9 flows WA, recall, NPS, voz "Sani" | 15 especialidades, perio, consentimientos Ley 26.529 | Caja, MP QR, ARCA C/B con CAE, 20+ convenios OS | MP, ARCA, WA QR, FHIR | USD 50+10/user |
| 3 | **Bilog** — Bilog SI, AR — bilog.com.ar | Cons./clínica/institución / híbrida | Por profesional + Bilog Turnos online | Reserva online Bilog Turnos | Recordatorios WA e IA iAngela (packs aparte) | Odontograma, imágenes, recetas | Nomenclador OS, liquidación OS/profesionales (Premium) | App móvil / MP, ARCA: No evidenciado | Freemium; resto cotizar |
| 4 | **DentalTec** — Tándem Digital, San Juan AR — web.dentaltec.com.ar | Odontólogo/institución / SaaS nube | Agenda integrada (detalle No evidenciado) | Confirmación WA; reserva 24/7 No evidenciada | Confirmación auto WA (-40% ausentismo afir.) | HC digital, odontograma, imágenes | Validación OS tiempo real + ARCA + liquidaciones, 15 OS | WA oficial, WS OS | No publica |
| 5 | **Odonthia** — Genera Impacto, AR — odonthia.com | Indep./equipo chico / nube navegador | Día/semana, bloqueos; multi-sillón No evidenciado | Reserva con aprobación profesional | IA por créditos (Rx, voz, posts) | Odontograma FDI, presupuestos con firma, Ley 26.529 | Tarifario por cobertura, sin liquidación ni ARCA | Firma Ley 25.506, GCal | Gratis/ARS 20,9k/46,9k |
| 6 | **Dentalink** — Healthatom, CL — softwaredentalink.com | Clínica/cadena / SaaS nube | Smart diary multi-sillón/doctor | Reserva 24/7 + IA Contact Center | Recall, campañas email, relleno huecos | Odontograma + perio, IA Rx, firma y receta | Cobros online/presenciales, convenios; MP AR y ARCA: No evidenciado | WA, pagos por país | No publica |
| 7 | **Dentiqa** — Violet Wave, LatAm/AR — dentiqa.app/ar | Clínica/cadena / SaaS nube | Multi-dentista, bloqueos, anti-doble-reserva | Chatbot IA WA oficial 24/7 | CRM pipeline, campañas WA, coach IA | HC 8 tabs, odontograma versionado, perio BOP/NIC | Facturación por profesional; ARCA solo Pro; OS: No evidenciado | WA Business API, MP (suscripción) | USD 89/149/249 |
| 8 | **Dentaly** — Dentaly, AR — dentaly.com.ar | Indep./clínica / SaaS nube | Diaria/semanal multi-prof. (detalle No evidenciado) | Agenda 24/7 declarada (detalle No evidenciado) | Recordatorios WA (-65% afir.) | Odontograma + perio, consentimientos | Finanzas + inventario; MP, ARCA, liquidación: No evidenciado | No evidenciado | ARS 35k/100k/custom |
| 9 | **Dentatools** — Dentatools, AR — dentatools.co/ar | Particulares / nube | Auto-agendado por link | Link auto-agendado | No evidenciado | Rx storage, presupuestos PDF | Cuentas por cobrar; sin OS ni AFIP (declarado) | No evidenciado | $30.000/mes |
| 10 | **ClinIA** — ClinIA, AR — clinia.com.ar/odontologia | Institucional/hospitalario / SaaS | Por profesional/especialidad/sillón + turnero web 24/7 + IA WA | Turnero 24/7, reagendamiento auto | IA WA, confirmaciones | Odontograma 3D, HCE, receta ReNaPDiS | PUCO, AFIP, liquidación OS, PAMI/SUMAR+ | HL7 FHIR | No publica |
| 11 | **Doctocliq** — Doctocliq, PE — doctocliq.com | Indep./multi-sede / SaaS + app | Multi-prof. (Avanzado), link online, importa GCal | Link 24/7, confirma WA | Recordatorios WA con tope, IA Soyla (adicional), marketing (adicional) | Odontograma + perio desde Gratis | Caja, comisiones; facturación e-PE/MX/EC/CO/RD (adicional) | WA API, GCal, Kommo | Gratis/USD 19/29/49 |
| 12 | **Dentidesk** — Dentidesk, CL — dentidesk.com | Clínicas/sindicatos/univ. / SaaS + app | Personalizable multi-usuario | Online como add-on | Recordatorios genéricos; WA auto en roadmap 2026 | Odontograma + fichas especialidad, voz | Facturación SII CL; pagos online: No evidenciado | SII, Alegra RD | No publica |
| 13 | **AgendaPro** — AgendaPro, CL/MX — agendapro.com | Belleza-salud / SaaS + app + marketplace | Multi-prof./sucursal, auto-llenado | Reservas 24/7 + marketplace | Doble confirmación, emailing, comisiones | Odontograma como anexo (no editor evidenciado) | Caja multi-sucursal, POS; fiscal MX: No evidenciado | WA | No publica dental |
| 14 | **Doctoralia Pro** — Docplanner, ES — pro.doctoralia.com.mx | Especialistas/clínicas / SaaS + marketplace | Multi-especialista, reserva multicanal 24/7 | 24/7, lista de espera inteligente, Noa 24/7 | Recordatorios, campañas, Noa Notes | No odontológico | Reportes; pagos/caja dental: No evidenciado | WA/SMS/email | CLP 59k/89k; MX cotizar |
| 15 | **Nimbo** — Ecaresoft, MX — nimbo-x.com | Consultorio/red / SaaS modular + portal | Multi-médico, portal por médico | Portal paciente | Recordatorios WA/email, encuestas | Odontograma adulto+infantil | Facturación MX, Stripe, inventario | WA, GCal, Stripe, Zoom | MXN 175 anual base |
| 16 | **Simples Dental** — Simples, BR — simplesdental.com | Cons./clínicas BR / SaaS + Alexa | Multi-equipo, encaixes, voz | Link 24/7 + Secretária IA WA | Confirmación auto, campañas WA | Prontuario + odontograma, firma, receta digital | Financeiro Pix/boleto, notas fiscales BR | WA/Meta, Asaas | BRL a consultar |
| 17 | **Medesk** — Medesk, Intl — medesk.net/es | Cons./clínicas/IPS / SaaS | Multi-prof./sala, reglas antelación, sync GCal | Reserva 24/7 multicanal + telemedicina | Recordatorios SMS/email, SMS masivos, CRM | Odontograma: No evidenciado | Facturación (Facele aparte), pagos online anticipo | GCal/iCal, SMS propio | Gratis/USD 16 |

Referencias internacionales de UX (fuera de tabla, insumo de patrones): **Open Dental** (Web Sched Recall/New/ASAP + eConfirm, USD 199→149/sede), **Curve Dental** (Sidekick 1-2 clics + SmartFill), **Dentally** (pricing por sillón £265/380/510 + Portal), **CareStack** (DSO multi-sede + Voice AI, USD 829+), **NexHealth** (capa experience + waitlist ROI + API), **Doctolib** (marketplace + freemium dentistas), **Dentrix/Ascend** (eligibility + IA imagen).

# B. Matriz de puntuación (0–5, estimaciones propias sobre evidencia verificada 2026-09-29)

Pesos: Turnos+automatización 25% · Clínico 20% · Integraciones locales+WA 15% · Admin/cobros/facturación 15% · Experiencia paciente 10% · Seguridad/exportación 10% · Precio/adopción 5%.

| Sistema | Turnos 25% | Clínico 20% | Integ. 15% | Admin 15% | Exp.pac. 10% | Seg. 10% | Precio 5% | **Total** |
|---|---|---|---|---|---|---|---|---|
| DentalCore | 4 | 5 | 3 | 5 | 3 | 3 | 2 | **3,90** |
| DentalSoft | 4 | 4 | 3 | 4 | 4 | 2 | 4 | **3,65** |
| Dentalink | 4 | 4 | 2 | 3 | 4 | 3 | 1 | **3,30** |
| Dentiqa | 4 | 4 | 2 | 2 | 4 | 3 | 2 | **3,20** |
| ClinIA | 3 | 3 | 3 | 4 | 2 | 3 | 1 | **2,95** |
| Odonthia | 3 | 3 | 2 | 2 | 3 | 3 | 5 | **2,80** |
| Doctocliq | 3 | 3 | 2 | 3 | 3 | 2 | 4 | **2,80** |
| Simples Dental | 4 | 3 | 1 | 3 | 3 | 2 | 2 | **2,80** |
| Bilog | 3 | 3 | 2 | 4 | 2 | 2 | 2 | **2,75** |
| Nimbo | 3 | 3 | 2 | 3 | 3 | 2 | 2 | **2,70** |
| DentalTec | 2 | 3 | 3 | 4 | 2 | 2 | 1 | **2,60** |
| Medesk | 3 | 1 | 2 | 3 | 3 | 3 | 4 | **2,50** |
| Doctoralia Pro | 4 | 1 | 1 | 1 | 5 | 4 | 2 | **2,50** |
| Dentidesk | 2 | 4 | 1 | 3 | 2 | 1 | 2 | **2,30** |
| AgendaPro | 3 | 1 | 1 | 3 | 3 | 1 | 3 | **2,10** |
| Dentaly | 2 | 3 | 1 | 2 | 2 | 1 | 4 | **2,05** |
| Dentatools | 2 | 2 | 1 | 2 | 2 | 2 | 5 | **2,00** |

Lectura: el liderazgo lo disputan DentalCore (admin local + clínico) y DentalSoft (equilibrio privado). Ninguno baja de 3,5 con precio accesible + OS + ARCA a la vez: ahí está el hueco.

# C. Análisis competitivo

**Estándar de mercado (lo que ya nadie puede no tener)**: reserva online 24/7 con disponibilidad real; confirmación y recordatorio por WhatsApp; cancelación/reprogramación por el paciente; agenda multi-profesional con estados de turno; presupuestos y cuenta corriente; precios o trial visibles. En LatAm se suma: planes gratis o de entrada en USD 16–49 y odontograma incluido.

**Diferenciadores reales (pocos los tienen)**: validación y liquidación de obras sociales argentinas (Bilog, DentalTec); factura electrónica ARCA + Mercado Pago cobro paciente en el mismo flujo (DentalCore); IA conversacional que agenda por WhatsApp (Dentiqa, DentalSoft plan alto); waitlist ASAP que rellena huecos con reclamo único (Open Dental, NexHealth, Doctoralia); pricing por sillón transparente (Dentally); marketplace que capta pacientes (Doctoralia, Doctolib, AgendaPro); CDSS/voz clínica (DentalCore).

**Vacíos frecuentes del mercado argentino**: nadie combina reserva online + WhatsApp oficial + OS + ARCA + MP + precio ARS publicado; la automatización real vive en planes caros o packs aparte; WhatsApp suele ser manual o con costo Meta trasladado; sin evidencia de cumplimiento Ley 25.326/26.529 publicado en casi todos; exportación masiva de datos y auditoría, ausentes; el segmento consultorio chico particular queda entre lo gratis sin OS y lo caro con todo.

**Oportunidades de innovación**: v1 enfocada (agenda excelente + seña MP + ARCA + GCal, costo cero con WA manual) en el hueco entre Odonthia/Dentatools y DentalSoft; waitlist con link único de reclamo vía WhatsApp (patrón ASAP adaptado a costo cero); validador OS como diferencial v2 cuando haya espalda; portal paciente liviano antes que odontograma pesado; publicar precio y onboarding en minutos como arma contra los que cotizan a pedido.

# D. Recomendación final

** Cinco competidores prioritarios para demo**: DentalSoft (equilibrio a batir), DentalCore (vara ARCA+MP+clínico), Bilog (vara OS institucional), DentalTec (vara validación OS + ARCA), Odonthia (vara costo cero y transparencia).

** Tres productos de referencia para UX**: Open Dental — Web Sched ASAP/recall/eConfirm (patrón a copiar); Dentally — Portal + pricing por sillón; Doctoralia/Doctolib — marketplace, lista de espera inteligente y reserva sin fricción.

** MVP sugerido**:
- Imprescindibles: reserva online 24/7 con disponibilidad real; agenda multi-profesional/sillón con duración variable, bloqueos y anti-solapamiento; confirmación/cancelación/reprogramación con 24h; sobreturnos con tope + lista de espera; confirmación manual por WhatsApp desde la app; seña por Mercado Pago; facturación ARCA; sync Google Calendar; reportes de ocupación y cobros.
- Diferenciadores v1: seña obligatoria atada a la reserva; waitlist con reclamo único; onboarding sin fricción y precio publicado (vs. cotización); costo operativo cero.
- Para etapas posteriores: odontograma + ficha clínica; portal del paciente; recordatorios automáticos (WhatsApp API); validación/liquidación de obras sociales; campañas y recuperación de inactivos.
