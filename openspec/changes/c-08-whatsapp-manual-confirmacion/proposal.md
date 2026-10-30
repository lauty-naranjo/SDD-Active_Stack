# Propuesta — C-08 whatsapp-manual-confirmacion

## Por qué

C-06 cierra el ciclo del turno, pero el consultorio sigue sin poder avisar: cada confirmación se resuelve por fuera del sistema y no queda registro de quién avisó ni cuándo, así que el ausentismo no se puede trabajar ni auditar. La API oficial de WhatsApp cuesta por mensaje (RN-INT-03) y ningún flujo v1 puede depender de ella (RN-CONF-02), con presupuesto cero (RN-GLB-01). C-08 captura el valor con un deep-link `wa.me` manual (costo cero) y un log de envío (RN-CONF-01, US-021).

## Qué cambia

- Deep link por turno: `https://wa.me/<telefono_normalizado>?text=<plantilla_percent_encoded>`, armado en el servidor. La plantilla incluye profesional, fecha/hora, seña y ventana de 24 h (RN-CONF-03) y es una constante parametrizable, no texto concatenado en la vista.
- Teléfono normalizado a formato internacional sin `+`, espacios, paréntesis ni guiones; texto percent-encoded en UTF-8 (`urllib.parse.quote(..., safe="")`) para no romper tildes, `ñ` ni el `+54 9`.
- `POST /turnos/:id/whatsapp-log` autenticado (rol `recepcionista`/`dueño`) que registra `{tipo, enviado_por, enviado_en}` en `MensajeWhatsApp` con `canal = manual_wa_me`. `enviado_por` sale de la sesión (nunca del body) y `enviado_en` del reloj del servidor (nunca del cliente).
- Log idempotente: `UNIQUE (turno_id, tipo)` en DB + `INSERT OR IGNORE`. Dos envíos concurrentes del mismo tipo dejan **una** fila, sin error 500 (R3/R4).
- Panel "pendientes de confirmación del día siguiente" (Flujo 3, paso 1): lista solo turnos `reservado` de la fecha pedida, con el link ya calculado.
- Marcar confirmado tras la respuesta del paciente reutiliza `POST /turnos/:id/confirmar` de C-06 (`reservado → confirmado`, RN-TUR-04). C-08 no agrega transiciones de estado.
- Módulo nuevo `src/c08/` con el mismo stack de C-06 (Python stdlib + `sqlite3` + `http.server`, R7) y migración 008: tabla `mensajes_whatsapp`.
- **Fuera de alcance**: API de Meta y recordatorios automáticos (backlog v2, RN-CONF-02); enviar el mensaje (lo envía la persona desde su WhatsApp); recibir o interpretar respuestas del paciente; el envío de `ofrecimiento_hueco` (es de C-09; la tabla lo admite por el modelo de datos, el endpoint de C-08 no); decidir el monto de la seña (pregunta abierta Alta).

## Capacidades

### Capacidades nuevas

- Ninguna. C-08 extiende una capability existente.

### Capacidades modificadas

- `gestion-turnos`: se agregan requisitos de confirmación/recordatorio manual por `wa.me` (link + plantilla, log idempotente, panel del día siguiente, operación sin credenciales de Meta). Los requisitos existentes de ventana 24 h, máquina de estados y seam GCal no cambian.

## Impacto

- **Depende de**: C-06 (`turnos` con `estado`, `inicio`, `fin`, `paciente_telefono`, `profesional_id`; transición `reservado → confirmado`; patrón `src/c06`) y C-03 (sesión y rol para `enviado_por` / RBAC). C-03 no está implementado: el diseño fija la interfaz mínima `sesion_actual()` y la prueba con un doble de test (OQ-2 del diseño).
- **Desbloquea**: C-12 (los reportes pueden leer `mensajes_whatsapp` para confirmaciones/ausentismo). No bloquea a ningún otro change.
- **APIs nuevas**: `POST /turnos/:id/whatsapp-log`, `GET /agenda/pendientes-confirmacion`.
- **DB**: migración 008, tabla `mensajes_whatsapp` con `UNIQUE (turno_id, tipo)` + índice por `turno_id` (005–007 ya reservadas por C-09/C-10/C-11 en `CHANGES.md`).
- **Dependencias nuevas**: ninguna (stdlib: `urllib.parse`, `sqlite3`, `re`). Sin credenciales de Meta (RN-CONF-02) y sin secretos nuevos (R2).
