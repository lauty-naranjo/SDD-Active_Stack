# Reglas de Negocio

Cada regla tiene un código único `RN-{DOMINIO}-{NN}` para trazabilidad.

## Dominio: Turnos y ventana 24h (RN-TUR)

- **RN-TUR-01**: No se puede cancelar ni reprogramar con menos de 24 horas de anticipación al inicio del turno.
- **RN-TUR-02**: La disponibilidad mostrada es siempre real: se calcula restando turnos vigentes + bloqueos a la franja del profesional/sillón.
- **RN-TUR-03**: El fin del turno se deriva de inicio + duración de la prestación; el paciente no elige duración libre.
- **RN-TUR-04**: Todo turno tiene estado trazable (pendiente_sena → reservado → confirmado → atendido/ausente/cancelado); sin saltos inválidos.

## Dominio: Agenda multi-profesional/sillón (RN-AGEN)

- **RN-AGEN-01**: La agenda no permite solapamientos: dos turnos no pueden compartir el mismo profesional ni el mismo sillón en intervalos intersectados.
- **RN-AGEN-02**: Cada prestación tiene duración propia (ej. limpieza 30', conducto 90'); duraciones sin validar con odontólogo real se marcan provisorias.
- **RN-AGEN-03**: Los bloqueos (ausencias, feriados, mantenimiento) restan disponibilidad antes de mostrar huecos; tienen motivo obligatorio.
- **RN-AGEN-04**: Desactivar profesional/sillón oculta disponibilidad futura sin borrar historial.

## Dominio: Sobreturnos y lista de espera (RN-SOB)

- **RN-SOB-01**: Los sobreturnos tienen tope por día y por profesional (número a definir en kb — ver pregunta abierta).
- **RN-SOB-02**: Un sobreturno nunca desplaza ni solapa un turno regular; ocupa hueco marginal o extensión al final de franja.
- **RN-SOB-03**: La lista de espera asigna huecos por reclamo único: el primer paciente que reclama el enlace ocupa el hueco; los demás enlaces caducan.
- **RN-SOB-04**: Al liberarse un hueco (cancelación ≥24h), se ofrece primero a la lista de espera antes de abrirlo al público general.

## Dominio: Confirmación WhatsApp manual (RN-CONF)

- **RN-CONF-01**: En v1 toda confirmación/recordatorio es manual desde la app (deep-link `wa.me`, costo cero); queda log de quién lo envió y cuándo.
- **RN-CONF-02**: Ningún flujo v1 depende de la API automática de WhatsApp (costo Meta); lo automático es backlog v2.
- **RN-CONF-03**: El mensaje manual parte de plantilla con datos del turno (profesional, fecha/hora, seña, ventana 24h).

## Dominio: Pagos / seña Mercado Pago (RN-PAGO)

- **RN-PAGO-01**: La reserva online exige seña obligatoria acreditada (monto fijo o % a definir).
- **RN-PAGO-02**: El webhook de Mercado Pago es idempotente: pagos duplicados no duplican turnos ni señas.
- **RN-PAGO-03**: Sin seña acreditada el turno queda en `pendiente_sena` y el horario se libera tras el timeout a definir.

## Dominio: Facturación ARCA (RN-FACT)

- **RN-FACT-01**: Cada cobro puede emitir comprobante electrónico ARCA con CAE; sin CAE no hay factura válida.
- **RN-FACT-02**: Reintentos de emisión son idempotentes (no duplicar comprobantes ante error de red).
- **RN-FACT-03**: Los datos fiscales del emisor se configuran una vez (CUIT, punto de venta, tipo de comprobante) y se auditan.

## Dominio: Integraciones (RN-INT)

- **RN-INT-01**: El sync con Google Calendar es por profesional (un calendar por profesional), bidireccional mínima lectura/escritura a definir.
- **RN-INT-02**: Ninguna integración con obras sociales en v1 (decisión consciente; va a v2).
- **RN-INT-03**: Todo lo que implique costo por mensaje o suscripción paga queda fuera de v1 por definición (restricción presupuesto cero).

## Dominio: Reportes (RN-REP)

- **RN-REP-01**: Reportes v1 mínimos: ocupación, ausentismo y cobros (por profesional y período).
- **RN-REP-02**: Ausente vs. cancelado se distinguen siempre (el ausentismo alimenta métrica de éxito).

## Dominio: Excepciones globales

- **RN-GLB-01**: Presupuesto cero: solo servicios gratuitos en v1; cualquier dependencia paga bloquea el diseño y va a backlog.
- **RN-GLB-02**: Identidad del paciente v1: nombre + teléfono obligatorios; DNI pendiente de decisión (ver pregunta abierta).
- **RN-GLB-03**: Alcance v1 = una sede; multi-sucursal solo si se responde la pregunta abierta a favor (ver `10_preguntas_abiertas.md`).
