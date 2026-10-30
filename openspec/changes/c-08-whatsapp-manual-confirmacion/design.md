# Diseño — C-08 whatsapp-manual-confirmacion

## Contexto

Ver `proposal.md` (Por qué) y `specs/gestion-turnos/spec.md` (contrato de comportamiento). Estado real del repo: C-06 está implementado en `src/c06/` con Python stdlib + `sqlite3` + `http.server` (R7, sin frameworks): `db.py` crea `turnos` (`paciente_telefono TEXT NOT NULL`, `inicio`/`fin` ISO8601 con offset, `estado`, `token_publico UNIQUE`), `bloqueos` y `eventos_outbox`; `servicio.py` expone `ROLES_STAFF = ("recepcionista", "dueño")`, `_fila_por_id`, `ahora_servidor()` y emite eventos con `INSERT OR IGNORE`. Este change **no modifica** `src/c06/*`: lo importa y lo extiende. C-03 (auth/RBAC) no está implementado; C-02/C-05 tampoco existen como módulos reales, así que el `turnos` operativo es el stub de C-06.

Restricciones duras: R1 (fixtures ficticios), R2 (sin secretos), R3 (unicidad y estados en DB), R4 (TDD en idempotencia y ventana 24 h), R5 (valores esperados literales), R7 (stack actual). Dato de soporte ya verificado por MCP Context7: `docs/skills-mcp/evidencias/03-mcp-context7.md` (§3 fragmentos de SQLite, §4 decisiones que alimentan este diseño).

## Objetivos / No objetivos

**Objetivos:**

- Link `wa.me` correcto byte a byte con teléfonos argentinos reales (`+54 9`, espacios, guiones) y texto con tildes/`ñ`.
- Un log que no se pueda duplicar ni por doble clic ni por concurrencia, con la garantía en la DB.
- Plantilla coherente con la ventana de 24 h: nunca prometer algo que RN-TUR-01 ya prohíbe.
- Cero costo y cero dependencias: sin API de Meta, sin librerías nuevas.

**No objetivos:**

- Enviar, recibir o interpretar mensajes (lo hace la persona en su WhatsApp; v1 no tiene Message-ID, KB 11).
- API de Meta / recordatorios automáticos (backlog v2, RN-CONF-02).
- `ofrecimiento_hueco` (lo produce C-09; la tabla lo admite por el modelo, el endpoint no).
- Definir el monto de la seña (pregunta abierta Alta) ni cambiar `PagoSena` (C-07).
- Reimplementar la confirmación `reservado → confirmado` (ya existe en C-06).

## Decisiones

### D1 — Deep link: teléfono solo dígitos y `quote(texto, safe="")`

**Decisión**: `normalizar_telefono(tel)` elimina todo lo que no sea dígito (`re.sub(r"\D", "", tel)`) y el link se arma como `https://wa.me/{normalizado}?text={quote(plantilla, safe="")}`.

**Justificación con el borde real:**

- `+54 9 11 0000-0001` → `5491100000001`. El `+` crudo en el path de `wa.me` es inválido y, además, en decodificación tipo formulario un `+` significa espacio; los espacios y guiones rompen el path.
- Tildes y `ñ`: `quote` codifica el `str` en UTF-8 por defecto y escapa todo byte fuera del conjunto siempre-seguro (`A-Z a-z 0-9 _ . - ~`). Documentado en CPython (`Doc/library/urllib.parse.rst`): `quote('/El Niño/')` → `'/El%20Ni%C3%B1o/'`; con `safe=""`, `quote('Señor/a')` → `'Se%C3%B1or%2Fa'`. Sin encoding, el navegador o el sistema operativo puede re-codificar el texto (clásico `SeÃ±or`) y el paciente recibe basura. Con encoding el mensaje viaja byte-exacto UTF-8.
- `safe=""` en vez del default `'/'`: el texto va en el query, un `/` suelto no aporta nada y dejarlo sin escapar hace ambiguo el valor esperado del test (R5). Así el literal es único y verificable.
- La normalización ocurre al renderizar, no al persistir: `paciente_telefono` es texto libre del stub de C-06 y no se migran datos (R3 no aplica acá; la normalización es de presentación).

**Alternativa descartada**: `quote_plus` / `urlencode` — usan `+` para los espacios; en `text=` de `wa.me` ese `+` queda literal o se confunde con el `+` del teléfono. También se descartó `quote` con `safe="/"` por la ambigüedad mencionada.

### D2 — Plantilla como constante parametrizable con placeholders

**Decisión**: `PLANTILLA_CONFIRMACION` y `PLANTILLA_RECORDATORIO` en `src/c08/whatsapp.py`, con placeholders `{paciente}`, `{profesional}`, `{fecha_hora}`, `{sena}`, `{ventana}`; override por entorno (`WA_PLANTILLA_CONFIRMACION`) siguiendo el patrón ya usado en C-06 (`CONTACTO = os.environ.get("APP_CONTACTO", ...)`). La capa HTTP y la vista solo llaman `construir_mensaje(turno, ...)`; no concatenan texto.

**Justificación**: RN-CONF-03 fija el **contenido** (profesional, fecha/hora, seña, ventana 24 h), no la redacción. Separar plantilla de vista permite corregir el texto sin tocar el endpoint y testear el render solo, sin levantar `http.server`. El formato de fecha es de presentación: `DD/MM/YYYY HH:MM` en la zona del `inicio` del turno (`-03:00`), no una regla de negocio.

**Alternativa descartada**: plantilla dentro del HTML/endpoint — no se puede testear sin HTTP y se duplica en cada pantalla que muestre el botón.

### D3 — Idempotencia en DB: `UNIQUE (turno_id, tipo)` + `ON CONFLICT DO NOTHING`

**Decisión**: migración 008 crea `mensajes_whatsapp` con `UNIQUE (turno_id, tipo)`. El servicio hace **un solo** `INSERT INTO mensajes_whatsapp (...) VALUES (...) ON CONFLICT (turno_id, tipo) DO NOTHING`; si `cur.rowcount == 0` la fila ya existía: se lee la original y se responde `200 {"duplicado": true, ...}` conservando su `enviado_en`. La primera inserción responde `201`.

**Justificación (documentación oficial de SQLite vía Context7)**: `docs/skills-mcp/evidencias/03-mcp-context7.md` §3 cita `https://www.sqlite.org/lang-conflict.html`: *"IGNORE — When an applicable constraint violation occurs, the IGNORE resolution algorithm skips the one row that contains the constraint violation and continues processing subsequent rows of the SQL statement as if nothing went wrong. […] No error is returned for uniqueness, NOT NULL, and UNIQUE constraint errors when the IGNORE conflict resolution algorithm is used."* Esa es la razón por la que **no** se usa `INSERT OR IGNORE`: absorbe *cualquier* violación de constraint —incluidos `CHECK` y `FOREIGN KEY`— y el `rowcount == 0` resultante se confundiría con un duplicado, devolviendo `200` donde el contrato exige `422` (tipo inválido) o `4xx` (turno inexistente). `ON CONFLICT (turno_id, tipo) DO NOTHING` limita la resolución a **esa** unicidad: el perdedor de la carrera sigue siendo un no-op, pero los demás errores de integridad se propagan. Se elimina igual el `SELECT` previo que abría la ventana entre chequeo e inserción. La misma evidencia (§3, `https://www.sqlite.org/isolation.html`) confirma que en WAL los lectores y escritores conviven pero los escritores se serializan; por eso el test de concurrencia usa dos conexiones reales (no un mock) y cada conexión se abre con `busy_timeout` para que el segundo escritor **espere** en lugar de recibir `SQLITE_BUSY`.

**Alternativa descartada**: `SELECT` + `INSERT` con lógica "si existe no inserto" (carrera, viola R3). `INSERT OR IGNORE` queda descartado por absorver `CHECK`/FK (ver arriba).

### D4 — Estados: confirmar solo desde `reservado`; log solo sobre turno vigente

**Decisión**: marcar confirmado reutiliza `servicio.confirmar_por_id` de C-06 (`UPDATE ... WHERE estado='reservado'` + `trg_turno_transicion` en DB) y **C-08 expone** la ruta staff `POST /turnos/:id/confirmar` en `src/c08/app.py`, porque C-06 solo publica `/turnos/:token/confirmar` (por token, no por `id`). No se modifica `src/c06/*`: C-08 no agrega transiciones ni toca el trigger (RN-TUR-04, R3). Sobre `cancelado`, `ausente`, `atendido` y `pendiente_sena` la confirmación se rechaza y el estado no muta. El endpoint de log acepta turnos `reservado` **o** `confirmado` y rechaza los demás con `409`, sin escribir fila; el chequeo de estado y el alta van dentro de la misma transacción `BEGIN IMMEDIATE` para que una cancelación concurrente no deje log sobre un turno cancelado (R3).

**Justificación**: `MensajeWhatsApp.tipo` incluye `recordatorio` (KB 04) y un recordatorio sobre un turno ya confirmado sigue siendo un envío legítimo; lo que no es legítimo es la transición, que solo existe desde `reservado`. Confirmar un turno `cancelado` o sin seña acreditada generaría estados imposibles (RN-TUR-04).

**Alternativa descartada**: permitir log sobre cualquier estado — ensucia el log con turnos muertos y debilita la trazabilidad de RN-CONF-01.

### D5 — Superficie API y seam de sesión (C-03 ausente)

**Decisión**: `POST /turnos/:id/whatsapp-log` con body `{"tipo": "confirmacion" | "recordatorio"}`; `enviado_por` **nunca** viene del body, sale de `sesion_actual(request) -> Sesion { usuario_id, rol }`. Sin sesión → `401`; rol fuera de `ROLES_STAFF` → `403`; `tipo` distinto de `confirmacion|recordatorio` (p. ej. `ofrecimiento_hueco`) → `422`. `GET /agenda/pendientes-confirmacion?fecha=YYYY-MM-DD` **también exige sesión staff** (`401`/`403`), porque todo el panel interno requiere autenticación (KB `03_actores_y_roles.md`): sin eso el panel filtraba nombre, teléfono y link `wa.me` del paciente. El default es el día siguiente al del reloj del servidor **convertido a la zona del consultorio** (`-03:00`, la de `inicio`), no la fecha UTC cruda; una `fecha` que no sea `YYYY-MM-DD` responde `400`. Solo `reservado`, con el link precalculado.

**Estado del supuesto (OQ-2)**: C-03 no existe en el repo. Este change fija la interfaz mínima como seam inyectable: los tests pasan un doble (`Sesion("recepcion-demo-01", "recepcionista")`) y el HTTP real responde `401` hasta que C-03 provea la sesión. El contrato no cambia cuando C-03 llegue: solo se reemplaza la implementación de `sesion_actual()`.

**Alternativa descartada**: aceptar `enviado_por` en el body — falsificable, y rompe el "quién" que exige RN-CONF-01.

### D6 — Ventana de 24 h dentro de la plantilla (comportamiento provisorio, OQ-1)

**Decisión**: si `inicio - ahora >= 24 h` (misma `ventana_ok` de `src/c06/ventana.py`), la plantilla incluye el límite `DD/MM/YYYY HH:MM` (= `inicio - 24 h`). Si faltan `< 24 h`, **no** promete la ventana: emite "Estás dentro de las 24 h previas al turno; si no podés asistir, comunicate con el consultorio: {contacto}", reusando la semántica de `MENSAJE_VENTANA` de C-06.

**Justificación**: RN-CONF-03 obliga a incluir la ventana; RN-TUR-01 hace que la promesa sea falsa dentro de las 24 h (el sistema rechaza cancelar/reprogramar). La KB **no** define el texto de este caso, así que queda como OQ-1 y el escenario solo afirma lo observable (no aparece la promesa vencida, sí aparece el contacto).

**Alternativa descartada**: omitir siempre la mención de ventana — contradice RN-CONF-03.

## Riesgos / Compromisos

- [Riesgo] `paciente_telefono` es texto libre en el stub de C-06; un número sin código de país genera un link a un número equivocado y `wa.me` no valida nada. → Mitigación: se normaliza a dígitos y el panel muestra el número normalizado junto al link; la validación de longitud/prefijo no está en la KB, queda como OQ-4 (no se inventa un mínimo).
- [Riesgo] `UNIQUE (turno_id, tipo)` impide registrar dos envíos del mismo tipo (p. ej. reintento porque el paciente no respondió). → Es deliberado (R3/R4): el reintento no se cuenta. Si el negocio necesita contar intentos, hay que cambiar el modelo (OQ-3).
- [Riesgo] SQLite tiene un solo escritor: una ráfaga de logs concurrentes puede devolver `SQLITE_BUSY`. → `busy_timeout` en la conexión + `BEGIN IMMEDIATE` corto; test con dos conexiones reales y corrida repetida.
- [Compromiso] El log es declarativo: registra que la persona pulsó el botón, no que WhatsApp entregó el mensaje (sin Message-ID en v1, KB 11). Consistente con RN-CONF-01.
- [Riesgo] Sin C-03 el endpoint de log y el panel responden `401` en un deploy real. → No bloquea la generación del link (función pura y testeable); el change queda listo para engancharse cuando C-03 exista.

## Plan de migración

1. Migración **008** (siguiente número libre: 005, 006 y 007 ya están reservadas por C-09, C-10 y C-11 en `CHANGES.md`): `CREATE TABLE mensajes_whatsapp` + índice `turno_id`. Sin backfill (greenfield, no hay datos previos).
2. Activar `PRAGMA foreign_keys=ON` en la conexión de `src/c08/db.py` (SQLite no lo trae activo por defecto; sin eso la FK a `turnos` no se aplica).
3. Deploy sin dependencias ni credenciales nuevas (R2); sin llamadas de red salientes.
4. Reversión: `DROP TABLE mensajes_whatsapp` + retirar endpoints y panel. No afecta tablas de otros módulos.

## Preguntas abiertas

- **OQ-1 (bloquea el literal, no el comportamiento)**: texto final de la plantilla y frase de seña. El monto de seña es pregunta abierta **Alta** de la KB (`10_preguntas_abiertas.md`), así que la plantilla nunca imprime un número: usa "Seña: a confirmar con el consultorio" y queda parametrizable. Decisor: dueño + C-07. No cambia escenarios, solo el literal.
- **OQ-2**: `enviado_por` ¿id de usuario, email o nombre? Supuesto: `usuario_id` (texto), tal como lo entregue C-03. Decisor: C-03.
- **OQ-3**: ¿se permite registrar `recordatorio` sobre un turno `confirmado` y qué pasa con reenviar el mismo tipo (la UNIQUE lo bloquea para siempre)? Supuesto: `confirmado` se acepta para log; el reenvío no crea fila nueva y responde idempotente. Decisor: dueño + C-12 (si los reportes necesitan contar envíos).
- **OQ-4**: ¿se valida longitud/prefijo del teléfono al generar el link? La KB solo exige "teléfono obligatorio" (RN-GLB-02). Supuesto: normalizar a dígitos y no rechazar por longitud en v1; el panel muestra el número resultante para que la recepcionista lo revise antes de abrir WhatsApp. Decisor: dueño.
