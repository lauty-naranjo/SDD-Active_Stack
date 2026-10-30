# Spec Delta — gestion-turnos

## ADDED Requirements

### Requirement: Deep link wa.me con plantilla del turno

El sistema SHALL exponer, por cada turno, un deep link construido en el servidor con la forma `https://wa.me/<telefono_normalizado>?text=<plantilla_percent_encoded>`. El teléfono SHALL normalizarse al formato internacional sin `+`, espacios, paréntesis ni guiones (solo dígitos). El texto SHALL percent-encodearse en UTF-8 con `urllib.parse.quote(..., safe="")`, de modo que el link no contenga espacios ni `+` crudos y el mensaje llegue byte-exacto. La plantilla SHALL incluir profesional, fecha y hora del turno, seña y ventana de 24 horas (RN-CONF-03), y SHALL ser una constante parametrizable, nunca texto armado dentro de la vista. El envío SHALL ser manual: el sistema NO SHALL llamar a la API de WhatsApp/Meta ni exigir credenciales para generar el link (RN-CONF-01, RN-CONF-02, US-021 CA-1/CA-3).

#### Scenario: Link feliz con teléfono normalizado y plantilla completa

- **DADO** un turno ficticio `tur-demo-001` en estado `reservado`, paciente `Juan Pérez Demo`, teléfono `+54 9 11 0000-0001`, profesional `Dra. Demo Uno`, prestación `limpieza`, inicio `2026-10-15T10:00:00-03:00`, y `ahora = 2026-10-14T08:00:00-03:00` en el servidor (26 h de anticipación)
- **CUANDO** se pide el link del turno
- **ENTONCES** el link empieza con `https://wa.me/5491100000001?text=`, el texto decodificado contiene `Dra. Demo Uno`, `15/10/2026 10:00`, `Seña: a confirmar con el consultorio` y `Podés cancelar o reprogramar hasta el 14/10/2026 10:00`, y no aparece ningún monto de seña (la KB lo deja abierto)

#### Scenario: Borde de encoding con tildes, ñ y +54 9

- **DADO** el turno `tur-demo-001` con paciente `Juan Pérez Demo` y teléfono `+54 9 11 0000-0001`
- **CUANDO** se construye el link
- **ENTONCES** el segmento de teléfono es `5491100000001` (sin `+`, espacios ni guiones), el query contiene el literal `Se%C3%B1or%2Fa%20Juan%20P%C3%A9rez%20Demo`, el link completo no contiene espacios ni el carácter `+`, y al decodificar el `text` se recupera exactamente la plantilla renderizada (ida y vuelta sin pérdida)

#### Scenario: Borde de ventana — la plantilla no promete una ventana ya vencida

- **DADO** un turno `reservado` con inicio `2026-10-15T10:00:00-03:00` y `ahora = 2026-10-15T02:00:00-03:00` en el servidor (faltan 8 h, menos de las 24 h de RN-TUR-01)
- **CUANDO** se construye el link
- **ENTONCES** el texto NO contiene `Podés cancelar o reprogramar hasta`; SÍ contiene `Estás dentro de las 24 h previas al turno` y el contacto del consultorio (`APP_CONTACTO`); el texto exacto de este caso queda declarado como OQ-1 del diseño porque la KB no lo fija

#### Scenario: Borde exacto de 24 h — el umbral se promete con igualdad

- **DADO** un turno `reservado` con inicio `2026-10-15T10:00:00-03:00` y `ahora = 2026-10-14T10:00:00-03:00` en el servidor (exactamente 24 h 00 de anticipación)
- **CUANDO** se construye el link
- **ENTONCES** el texto SÍ contiene `Podés cancelar o reprogramar hasta el 14/10/2026 10:00`, porque RN-TUR-01 rechaza únicamente `< 24 h` y el borde por igualdad se acepta (`ventana_ok` de C-06 compara `>= 24 h`)

### Requirement: Registro idempotente del envío manual

`POST /turnos/:id/whatsapp-log` SHALL requerir sesión con rol `recepcionista` o `dueño` y SHALL registrar en `mensajes_whatsapp` `{ turno_id, tipo, canal = 'manual_wa_me', enviado_por, enviado_en }`. `enviado_por` SHALL provenir de la sesión y nunca del cuerpo del request; `enviado_en` SHALL ser el reloj del servidor en el momento del request y nunca la hora del cliente. En este endpoint `tipo` SHALL ser `confirmacion` o `recordatorio` (`ofrecimiento_hueco` pertenece a C-09); un `tipo` fuera de ese conjunto SHALL rechazarse con `422` sin escribir fila. La unicidad `(turno_id, tipo)` SHALL imponerse en la base de datos con `UNIQUE` más `INSERT ... ON CONFLICT (turno_id, tipo) DO NOTHING` (R3): la resolución de conflicto SHALL limitarse a la violación de unicidad, de modo que una violación de `CHECK` de `tipo` o de `FOREIGN KEY` NO SHALL absorberse como duplicado. El alta SHALL ser idempotente: repetir el mismo `(turno_id, tipo)` NO SHALL crear otra fila ni responder error `5xx` (R4). La verificación de estado y el alta SHALL ocurrir dentro de la misma transacción `BEGIN IMMEDIATE`, para que una cancelación concurrente no deje una fila de log sobre un turno ya cancelado. El registro SHALL aceptarse solo sobre turnos en estado `reservado` o `confirmado`; `pendiente_sena`, `cancelado`, `ausente` y `atendido` SHALL rechazarse con `409`, sin mutar el estado del turno y sin escribir ninguna fila de log.

#### Scenario: Log feliz con quién, cuándo y tipo

- **DADO** el turno `tur-demo-001` en estado `reservado`, una sesión con `usuario_id = "recepcion-demo-01"` y rol `recepcionista`, y `ahora = 2026-10-14T08:00:00-03:00` en el servidor
- **CUANDO** se pide `POST /turnos/tur-demo-001/whatsapp-log` con `{"tipo": "confirmacion"}`
- **ENTONCES** responde `201`, `mensajes_whatsapp` tiene exactamente 1 fila con `turno_id = "tur-demo-001"`, `tipo = "confirmacion"`, `canal = "manual_wa_me"`, `enviado_por = "recepcion-demo-01"` y `enviado_en = "2026-10-14T08:00:00-03:00"`, y el turno sigue en estado `reservado`

#### Scenario: Recordatorio sobre turno ya confirmado

- **DADO** el turno `tur-demo-006` en estado `confirmado`, una sesión de recepcionista y `ahora = 2026-10-14T08:00:00-03:00` en el servidor
- **CUANDO** se pide `POST /turnos/tur-demo-006/whatsapp-log` con `{"tipo": "recordatorio"}`
- **ENTONCES** responde `201`, se registra 1 fila con `tipo = "recordatorio"` y `canal = "manual_wa_me"`, y el turno sigue en `confirmado` (el log no muta el estado)

#### Scenario: Rechazo de negocio sobre turno cancelado

- **DADO** el turno `tur-demo-002` en estado `cancelado` y una sesión de recepcionista
- **CUANDO** se pide `POST /turnos/tur-demo-002/whatsapp-log` con `{"tipo": "confirmacion"}`
- **ENTONCES** responde `409` con mensaje que indica que el turno no está vigente, el turno sigue en estado `cancelado` y `mensajes_whatsapp` no tiene ninguna fila para `tur-demo-002`

#### Scenario: Rechazo sobre turno pendiente_sena

- **DADO** el turno `tur-demo-003` en estado `pendiente_sena` (seña sin acreditar, RN-PAGO-03) y una sesión de recepcionista
- **CUANDO** se pide `POST /turnos/tur-demo-003/whatsapp-log` con `{"tipo": "confirmacion"}`
- **ENTONCES** responde `409`, el turno sigue en estado `pendiente_sena` y `mensajes_whatsapp` no registra ninguna fila para `tur-demo-003`

#### Scenario: Rechazo sobre turno ausente o atendido

- **DADO** el turno `tur-demo-004` en estado `ausente` y el turno `tur-demo-005` en estado `atendido`, ambos con sesión de recepcionista
- **CUANDO** se pide `POST /turnos/:id/whatsapp-log` con `{"tipo": "confirmacion"}` sobre cada uno
- **ENTONCES** ambas respuestas son `409`, los dos turnos conservan su estado y `mensajes_whatsapp` no registra filas para `tur-demo-004` ni `tur-demo-005`

#### Scenario: Tipo fuera del alcance no se registra

- **DADO** el turno `tur-demo-001` en estado `reservado` y una sesión de recepcionista
- **CUANDO** se pide `POST /turnos/tur-demo-001/whatsapp-log` con `{"tipo": "ofrecimiento_hueco"}`
- **ENTONCES** responde `422` (el tipo pertenece a C-09), el turno sigue en `reservado` y `mensajes_whatsapp` no registra ninguna fila

#### Scenario: Concurrencia — dos POST del mismo tipo dejan una sola fila

- **DADO** el turno `tur-demo-001` en estado `reservado` y dos conexiones `sqlite3` reales abiertas contra el mismo archivo de base
- **CUANDO** dos `POST /turnos/tur-demo-001/whatsapp-log` con `{"tipo": "confirmacion"}` se ejecutan concurrentemente
- **ENTONCES** ambas respuestas son exitosas (`201` la primera y `200` con `duplicado: true` la segunda, en cualquier orden), `mensajes_whatsapp` tiene exactamente 1 fila para `(tur-demo-001, confirmacion)` y ninguna respuesta es `5xx`

#### Scenario: Sin sesión o con rol no staff no se registra

- **DADO** el turno `tur-demo-001` en estado `reservado`
- **CUANDO** se pide el log sin sesión, o con una sesión de rol `paciente`
- **ENTONCES** responde `401` sin sesión y `403` con rol no staff, `mensajes_whatsapp` no registra ninguna fila y el turno conserva el estado `reservado`

#### Scenario: El enviado_por del cuerpo se ignora

- **DADO** el turno `tur-demo-001` en estado `reservado` y una sesión con `usuario_id = "recepcion-demo-01"`
- **CUANDO** se pide `POST /turnos/tur-demo-001/whatsapp-log` con `{"tipo": "confirmacion", "enviado_por": "admin-falso"}`
- **ENTONCES** responde `201` y la fila registrada tiene `enviado_por = "recepcion-demo-01"`: el valor del cuerpo se descarta y no se persiste

### Requirement: Confirmación manual del turno tras la respuesta del paciente

Marcar confirmado SHALL reutilizar la transición `reservado → confirmado` de C-06 (RN-TUR-04) mediante su función de servicio por `id` `servicio.confirmar_por_id`, que ya existe en `src/c06/`. Como el endpoint HTTP staff por `id` **no** existe en C-06 (C-06 solo expone `/turnos/:token/confirmar`), este change SHALL exponer `POST /turnos/:id/confirmar` en `src/c08/app.py`, sin modificar `src/c06/*`. Este change NO SHALL agregar transiciones de estado ni duplicar la lógica de la máquina de estados; el trigger `trg_turno_transicion` de C-06 SHALL seguir siendo la garantía (R3). Las transiciones desde `cancelado`, `ausente`, `atendido` y `pendiente_sena` SHALL seguir rechazándose. La confirmación NO SHALL alterar ni borrar las filas de `mensajes_whatsapp` del turno.

#### Scenario: Confirmar tras la respuesta conserva el log

- **DADO** el turno `tur-demo-001` en estado `reservado` con 1 fila de log `confirmacion` de `recepcion-demo-01`, y una sesión de recepcionista
- **CUANDO** el paciente responde por WhatsApp y la recepcionista pide `POST /turnos/tur-demo-001/confirmar`
- **ENTONCES** responde `200`, el estado pasa a `confirmado` y sigue habiendo exactamente 1 fila de log `confirmacion` con el mismo `enviado_por` y el mismo `enviado_en`

### Requirement: Panel de pendientes de confirmación del día siguiente

`GET /agenda/pendientes-confirmacion?fecha=YYYY-MM-DD` SHALL requerir sesión con rol `recepcionista` o `dueño`, porque todo el panel interno exige autenticación (KB `03_actores_y_roles.md`): sin sesión SHALL responder `401` y con rol no staff `403`, sin devolver datos de pacientes. Con sesión válida SHALL listar los turnos en estado `reservado` cuyo `inicio` cae en la fecha pedida —por defecto, el día siguiente al del reloj del servidor **en la zona del consultorio** (`-03:00`, la misma de `inicio`; el cálculo NO SHALL usar la fecha UTC cruda)—, cada uno con su link `wa.me` ya calculado (Flujo 3 paso 1, RN-CONF-03). Una `fecha` con formato distinto de `YYYY-MM-DD` SHALL rechazarse con `400`. NO SHALL incluir turnos en `pendiente_sena`, `confirmado`, `cancelado`, `ausente` ni `atendido`, ni turnos de otras fechas. El panel SHALL ser de lectura y NO SHALL exigir credenciales de Meta (RN-CONF-02).

#### Scenario: Lista solo los reservados del día siguiente

- **DADO** tres turnos ficticios: `tur-A` en estado `reservado` con inicio `2026-10-15T10:00:00-03:00`, `tur-B` en estado `reservado` con inicio `2026-10-16T10:00:00-03:00` y `tur-C` en estado `cancelado` con inicio `2026-10-15T11:00:00-03:00`, y `ahora = 2026-10-14T18:00:00-03:00` en el servidor
- **CUANDO** se pide `GET /agenda/pendientes-confirmacion` sin parámetro `fecha` con una sesión de recepcionista
- **ENTONCES** devuelve exactamente `[tur-A]` con su link `wa.me` precalculado, y excluye `tur-B` (otra fecha) y `tur-C` (cancelado)

#### Scenario: Borde de zona horaria del día siguiente

- **DADO** `ahora = 2026-10-15T01:00:00+00:00` en el servidor (22:00 del 14/10 en el consultorio, `-03:00`), el turno `tur-A` en `reservado` con inicio `2026-10-15T10:00:00-03:00` y una sesión de recepcionista
- **CUANDO** se pide `GET /agenda/pendientes-confirmacion` sin `fecha`
- **ENTONCES** devuelve `[tur-A]`: el día siguiente se calcula en la zona del consultorio (15/10) y no con la fecha UTC (que ya es 15/10 y daría 16/10)

#### Scenario: Fecha inválida no lista nada

- **DADO** una sesión de recepcionista y el turno `tur-A` en `reservado`
- **CUANDO** se pide `GET /agenda/pendientes-confirmacion?fecha=15-10-2026`
- **ENTONCES** responde `400` y el cuerpo no incluye turnos ni links `wa.me`

#### Scenario: Sin sesión o rol no staff no lista pendientes

- **DADO** el turno `tur-A` en estado `reservado` con teléfono de paciente cargado
- **CUANDO** se pide `GET /agenda/pendientes-confirmacion` sin sesión, o con una sesión de rol `paciente`
- **ENTONCES** responde `401` sin sesión y `403` con rol no staff, y el cuerpo no contiene nombres, teléfonos ni links `wa.me` del paciente

### Requirement: Operación sin credenciales de Meta

Ninguna funcionalidad de este change SHALL requerir variables de entorno, credenciales ni llamadas salientes a la API de WhatsApp/Meta (RN-CONF-02, US-021 CA-3). Generar el link, registrar el log y listar el panel SHALL funcionar con el entorno vacío de credenciales de mensajería, y el canal registrado SHALL ser siempre `manual_wa_me`.

#### Scenario: Entorno sin credenciales de mensajería sigue verde

- **DADO** un entorno sin `WHATSAPP_*`, sin `META_*` y sin token de Meta, y el turno `tur-demo-001` en estado `reservado`
- **CUANDO** se genera el link y se registra el log de `confirmacion` con `socket.create_connection` sustituido por un doble que falla el test si se invoca
- **ENTONCES** el link se genera, el log responde `201` y el doble de red no registra ninguna conexión saliente a Meta/WhatsApp (RN-CONF-02)
