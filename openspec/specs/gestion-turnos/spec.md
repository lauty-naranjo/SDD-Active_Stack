# gestion-turnos Specification

## Purpose
Permite al paciente (sin login, vía token) y a la recepcionista confirmar, cancelar y reprogramar turnos dentro de la ventana de 24 horas, con máquina de estados trazable y liberación de huecos hacia la lista de espera.

## Requirements

### Requirement: Ventana de 24h para cancelar y reprogramar

El sistema SHALL rechazar toda cancelación o reprogramación (paciente por token o recepcionista autenticado) cuando falte menos de 24 horas para el `inicio` del turno, respondiendo error con mensaje claro y contacto del consultorio. La comparación SHALL usar el reloj del servidor (`ahora = now()` servidor, zona del consultorio) y el `inicio` persistido, nunca valores del cliente. El umbral es `inicio - ahora >= 24h` para aceptar; `< 24h` para rechazar. La confirmación (marcar `confirmado`) SHALL estar siempre permitida independientemente de la ventana.

#### Scenario: Cancelación feliz fuera de ventana (dado/cuando/entonces)

- **DADO** un turno en estado `reservado` con `inicio = 2026-10-15T10:00:00-03:00`
- **CUANDO** el paciente pide `POST /turnos/:token/cancelar` siendo `ahora = 2026-10-14T09:59:00-03:00` en el servidor (diferencia 24h01min ≥ 24h)
- **ENTONCES** el sistema responde `200`, el estado pasa a `cancelado` y emite el evento `HuecoLiberado`

#### Scenario: Rechazo de negocio dentro de ventana (dado/cuando/entonces)

- **DADO** un turno en estado `reservado` con `inicio = 2026-10-15T10:00:00-03:00`
- **CUANDO** el paciente pide `POST /turnos/:token/cancelar` siendo `ahora = 2026-10-14T10:01:00-03:00` en el servidor (diferencia 23h59min < 24h)
- **ENTONCES** el sistema responde `409` (o `422` según ADR-01) sin cambiar el estado, con mensaje claro ("ya estás dentro de las 24 horas…") más el contacto del consultorio, y NO emite `HuecoLiberado`

#### Scenario: Borde exacto 24h00

- **DADO** un turno en estado `reservado` con `inicio = 2026-10-15T10:00:00-03:00`
- **CUANDO** la operación llega siendo `ahora = 2026-10-14T10:00:00-03:00` en el servidor (diferencia exactamente 24h00min00s)
- **ENTONCES** el sistema la ACEPTA (el rechazo es estrictamente `< 24h`; igualdad acepta)

#### Scenario: Reprogramación dentro de ventana también se rechaza

- **DADO** un turno en estado `reservado` o `confirmado` con `inicio = 2026-10-15T10:00:00-03:00`
- **CUANDO** se pide `POST /turnos/:token/reprogramar` con `nuevo_inicio` libre siendo `ahora = 2026-10-14T12:00:00-03:00` (diferencia 22h < 24h)
- **ENTONCES** el sistema responde `409`/`422` con mensaje + contacto, el turno conserva su `inicio` original y su estado, y no se reserva el destino

### Requirement: Máquina de estados del turno

El sistema SHALL persistir el estado del turno con las únicas transiciones válidas `reservado → confirmado → atendido | ausente | cancelado` y `reservado → cancelado` y `confirmado → cancelado` (la transición `pendiente_sena → reservado` pertenece a C-05/C-07 y solo se referencia). Toda transición inválida (p. ej. `cancelado → confirmado`, `atendido → cancelado`, `ausente → *`) SHALL ser rechazada sin mutar el turno. `ausente` y `cancelado` SHALL ser estados distintos y consultables por separado (RN-REP-02). Las transiciones válidas SHALL estar impuestas por CHECK constraint en DB (R3); el código solo propaga el error.

#### Scenario: Confirmación feliz reservado → confirmado

- **DADO** un turno en estado `reservado` con ventana válida (`inicio - ahora ≥ 24h`, o cualquier `ahora` pues confirmar no exige ventana)
- **CUANDO** el paciente pide `POST /turnos/:token/confirmar` (o recepcionista `POST /turnos/:id/confirmar`)
- **ENTONCES** el sistema responde `200` y el estado pasa a `confirmado`

#### Scenario: Transición inválida rechazada

- **DADO** un turno en estado `cancelado`
- **CUANDO** se pide `POST /turnos/:token/confirmar` con token válido
- **ENTONCES** el sistema responde `409`/`422` (transición inválida), el estado sigue `cancelado` y el error es propagación del CHECK constraint de DB

#### Scenario: Ausente y cancelado se distinguen

- **DADO** dos turnos pasados, uno marcado `ausente` por recepcionista y otro `cancelado` en ventana válida
- **CUANDO** se consultan los turnos (agenda o futuro reporte C-12)
- **ENTONCES** el sistema devuelve `estado = ausente` para uno y `estado = cancelado` para el otro, sin colapsarlos en un único valor

### Requirement: Cancelación válida libera el hueco y notifica a la espera

Toda cancelación aceptada SHALL liberar el intervalo `[inicio, fin)` del turno (disponible para C-04/C-05) y emitir exactamente una vez el evento de dominio `HuecoLiberado { turno_id, profesional_id, sillon_id, inicio, fin }` para consumo de C-09 (RN-SOB-04). El evento NO SHALL abrir el hueco al público general antes de ofrecerlo a la lista de espera (orden garantizado por C-09; este change solo garantiza emisión única y payload completo).

#### Scenario: Cancelación válida emite HuecoLiberado una vez

- **DADO** un turno `reservado` con `inicio = 2026-10-20T10:00:00-03:00`, `fin = 2026-10-20T10:30:00-03:00` y `ahora` con ≥ 24h de anticipación
- **CUANDO** se acepta `POST /turnos/:token/cancelar`
- **ENTONCES** el intervalo `[10:00, 10:30)` vuelve a estar disponible y se emite un único `HuecoLiberado` con `{ turno_id, profesional_id, sillon_id, inicio = 2026-10-20T10:00:00-03:00, fin = 2026-10-20T10:30:00-03:00 }`

### Requirement: Reprogramación atómica con anti-solapamiento y borde de adyacencia

La reprogramación aceptada SHALL ser atómica: en una sola transacción corta valida ventana sobre el turno origen, verifica que el destino `[nuevo_inicio, nuevo_inicio + duracion)` no solape ningún turno vigente del mismo profesional ni del mismo sillón (delegando en el constraint transaccional de C-04) ni caiga en bloqueo, y solo entonces mueve el turno (mismo `id`, nuevo `inicio`/`fin`, estado resultante `reservado`). Si el destino está ocupado o en bloqueo, SHALL rechazar sin mutar el origen y sugerir lista de espera. Los intervalos son semiabiertos `[inicio, fin)`: `fin == inicio` del vecino NO solapa (borde de adyacencia permitido).

#### Scenario: Reprogramación feliz a hueco libre

- **DADO** un turno `reservado` `[2026-10-20T10:00:00-03:00, 2026-10-20T10:30:00-03:00)` y un destino `[2026-10-21T10:00:00-03:00, 2026-10-21T10:30:00-03:00)` libre de turnos y bloqueos, con `ahora` a ≥ 24h del origen
- **CUANDO** se pide `POST /turnos/:token/reprogramar` con `nuevo_inicio = 2026-10-21T10:00:00-03:00`
- **ENTONCES** el sistema responde `200`, el turno conserva su `id` con `inicio = 2026-10-21T10:00:00-03:00`, `fin` re-derivado (`nuevo_inicio + duracion_prestacion`), estado `reservado`, y emite `HuecoLiberado` del origen más evento de ocupación del destino (hacia C-11)

#### Scenario: Borde de adyacencia fin==inicio no solapa (dado/cuando/entonces)

- **DADO** un turno existente del mismo profesional y sillón en `[2026-10-21T10:30:00-03:00, 2026-10-21T11:00:00-03:00)` y un turno origen `reservado` a reprogramar, con ventana válida
- **CUANDO** se pide `reprogramar` con `nuevo_inicio = 2026-10-21T10:00:00-03:00` y duración 30min (destino `[10:00, 10:30)`, cuyo `fin == 10:30` coincide exactamente con el `inicio` del vecino)
- **ENTONCES** el sistema ACEPTA la reprogramación (fin==inicio no es solapamiento según RN-AGEN-01 con intervalos semiabiertos)

#### Scenario: Destino ocupado rechaza sin mutar y sugiere espera

- **DADO** un turno origen `reservado` `[2026-10-20T10:00:00-03:00, 2026-10-20T10:30:00-03:00)` y un destino `[2026-10-21T10:00:00-03:00, 2026-10-21T10:30:00-03:00)` que intersecta (no solo toca) un turno vigente del mismo profesional o sillón, con ventana válida
- **CUANDO** se pide `reprogramar` a ese `nuevo_inicio`
- **ENTONCES** el sistema responde `409` con mensaje que sugiere anotarse en lista de espera, el origen conserva `inicio`/`fin`/estado intactos y no se emite ningún evento

### Requirement: Gestión por token sin login y equivalentes de recepcionista

El paciente SHALL poder ver y gestionar su turno en la página pública `/turnos/:token` sin cuenta ni login (US-020 CA-3): ver estado, profesional, fecha/hora y usar confirmar/cancelar/reprogramar con los mismos errores de ventana que la API. Token inexistente o expirado SHALL responder `404`/`410` sin revelar datos de otros turnos. La recepcionista (rol `recepcionista` o `dueño`) SHALL poder ejecutar las mismas tres operaciones por `id` desde el panel autenticado, sin estar sujeta a exenciones de ventana (misma RN-TUR-01), y marcar `atendido`/`ausente` (transiciones solo-staff, no expuestas por token).

#### Scenario: Paciente gestiona sin login

- **DADO** un turno `reservado` con `token_publico = "tok-demo-001"` vigente
- **CUANDO** el paciente abre `/turnos/tok-demo-001` sin sesión y pulsa confirmar
- **ENTONCES** la página muestra el turno y la confirmación resulta en estado `confirmado` sin pedir credenciales

#### Scenario: Token inválido no filtra datos

- **DADO** ningún turno con `token_publico = "tok-inexistente-999"`
- **CUANDO** se abre `/turnos/tok-inexistente-999` o se llama `POST /turnos/tok-inexistente-999/cancelar`
- **ENTONCES** el sistema responde `404` sin exponer datos de otros turnos

### Requirement: Cambios publicados como seam hacia Google Calendar

Cada cambio de estado o de horario aceptado SHALL publicar un evento de dominio (`TurnoConfirmado | TurnoCancelado | TurnoReprogramado` con payload completo) consumible por C-11. Este change NO SHALL escribir en Google Calendar ni exigir credenciales (`GCAL_CLIENT_ID/SECRET` ausentes ⇒ el flujo sigue verde); el fallo futuro de GCal nunca rompe el turno (contrato que C-11 honrará).

#### Scenario: Evento publicado sin GCal configurado

- **DADO** un turno `reservado` sin ninguna credencial GCal en el entorno
- **CUANDO** se acepta `confirmar`
- **ENTONCES** el cambio persiste `confirmado`, el evento `TurnoConfirmado` queda publicado para C-11 y la respuesta es `200` sin error de integración
