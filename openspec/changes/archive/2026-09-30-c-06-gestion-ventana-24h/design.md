# Diseño — C-06 gestion-ventana-24h

## Contexto

Ver `proposal.md` (Por qué) y `specs/gestion-turnos/spec.md` (contrato de comportamiento). Estado previo asumido de C-03/C-04/C-05 (no implementados — greenfield): existe `Turno { id, profesional_id, sillon_id, prestacion_id, paciente_id, inicio, fin, estado, origen, token_publico, token_expira_en }` con anti-solapamiento transaccional (C-04) y `token_publico` único con expiración (C-03). Stack aún sin decidir (ADR-01 de C-01 pendiente): este diseño evita atarse a framework; donde la sintaxis difiere se indica la alternativa. Restricciones duras: R3 (transiciones y solapamiento en DB, no solo la aplicación), R4 (TDD en ventana 24h), R1 (fixtures ficticios), R2 (sin secretos).

## Objetivos / No objetivos

**Objetivos:**

- Ventana 24h calculada en servidor con semántica de borde inequívoca (`< 24h` rechaza, `== 24h` acepta).
- Transiciones de estado imposibles de violar aunque el código aplique mal la regla (CHECK en DB).
- Reprogramación atómica sin doble-reserva ni hueco fantasma bajo concurrencia.
- Desacople con C-09 (espera) y C-11 (GCal) vía eventos, sin llamadas directas entre módulos.

**No objetivos:**

- Transición `pendiente_sena → reservado` (C-07), tope/sobreturnos y reclamo único (C-09), OAuth y escritura GCal (C-11), WhatsApp (C-08), cobros/factura/reportes (C-07/C-10/C-12).
- Definir monto de seña, timeout `pendiente_sena`, tope de sobreturnos (preguntas abiertas del dueño).
- Decidir stack (ADR-01, C-01).

## Decisiones

### D1 — Hook hacia C-09 como evento `HuecoLiberado` (recomendado) vs llamada directa

**Decisión**: evento de dominio `HuecoLiberado { turno_id, profesional_id, sillon_id, inicio, fin, liberado_en }` publicado en la misma transacción que la cancelación/reprogramación (outbox transaccional o `LISTEN/NOTIFY` si el stack es Postgres; cola en memoria con registro persistido si el ADR-01 elige otro motor — ver D4). C-09 suscribe y ofrece a la espera antes de abrir al público (RN-SOB-04).

**Alternativa descartada**: llamada directa `c06 → c09.ofrecerHueco()`. Crea dependencia circular (C-09 también muta turnos al reclamar) y acopla el camino crítico de cancelación a la latencia de la espera. El evento mantiene C-06 verde aunque C-09/C-11 no existan todavía (tests con suscriptor falso).

### D2 — Ventana 24h: reloj servidor + comparación en SQL/UTC

**Decisión**: `ahora = now()` del servidor de DB (o reloj backend en UTC si el motor no es Postgres), `inicio` almacenado en `timestamptz`. Regla: aceptar ⟺ `inicio - ahora >= interval '24 hours'`; rechazar ⟺ `< interval '24 hours'`. La igualdad exacta acepta (borde 24h00 del spec). El mensaje de rechazo incluye siempre texto claro + contacto del consultorio (parametrizable, valor provisorio `APP_CONTACTO` hasta respuesta del dueño).

**Alternativa descartada**: calcular en frontend o con hora del cliente — falsificable y con zonas horarias inconsistentes. Tampoco se redondea a días calendario: son 24h exactas de reloj (23:59 rechaza, 24:01 acepta, casos del spec con literales 2026-10-15T10:00 vs 10:01/09:59 del día anterior).

### D3 — Reprogramación atómica en una transacción corta

**Decisión**: `BEGIN; SELECT turno … FOR UPDATE; validar ventana; validar destino (anti-solapamiento C-04 + bloqueos); UPDATE turno SET inicio/fin, estado='reservado'; publicar HuecoLiberado(origen)+TurnoReprogramado; COMMIT`. `fin = nuevo_inicio + prestacion.duracion_min` re-derivado en servidor (RN-TUR-03), nunca aceptado del body. Intervalos semiabiertos `[inicio, fin)`: el constraint de exclusión usa `&&` sobre `tstzrange(inicio, fin, '[)')`, de modo que `fin == inicio` vecino no colisiona (borde de adyacencia del spec). Ante destino ocupado: `ROLLBACK` + `409` con sugerencia de lista de espera; el origen queda intacto.

**Alternativa descartada**: cancelar + crear (dos operaciones). Deja ventana de carrera donde el origen se libera pero el destino falla, o dos turnos duplicados.

### D4 — Máquina de estados con CHECK constraints + índice (estado)

**Decisión** (supabase-postgres-best-practices): si ADR-01 confirma Postgres, migración de C-06 añade `CHECK (estado IN (...))` más constraint de transición válida implementado como trigger `BEFORE UPDATE` o tabla de transiciones (`estado_origen, estado_destino` con FK compuesta) — a elegir en C-01 según convención de migraciones; el spec solo exige que la transición inválida falle en DB. Índices: `(estado)` para panel "pendientes de confirmación" y `token_publico UNIQUE` (ya de C-03; referenciado). Transacciones cortas con `FOR UPDATE` solo sobre la fila del turno; sin locks de tabla.

**Alternativa descartada**: validar solo en aplicación (viola R3) o máquina de estados en cliente.

### D5 — Superficie API y errores

**Decisión**: públicos `POST /turnos/:token/confirmar | /cancelar | /reprogramar` (reprogramar exige body `{ nuevo_inicio: ISO8601 }`); staff `POST /turnos/:id/confirmar | /cancelar | /reprogramar | /marcar-atendido | /marcar-ausente` bajo auth + RBAC (recepcionista/dueño). Errores: `404` token/id inexistente, `410` token expirado, `409` ventana insuficiente o transición inválida o destino ocupado, `422` body inválido (`nuevo_inicio` pasado o mal formato). Solo-staff expone `atendido/ausente`; el token nunca permite marcarlos. Página `/turnos/:token` server-rendered o estática + fetch según ADR-01; E2E sin login (webapp-testing).

## Riesgos / Compromisos

- [Riesgo] Stack sin decidir (ADR-01 pendiente) → sintaxis SQL/eventos del diseño no ejecutable aún. Mitigación: diseño agnóstico con ramas Postgres/otro; tasks empiezan por confirmar ADR-01 o fijar supuesto SQL estándar.
- [Riesgo] Destino de la seña al cancelar/reprogramar roza C-07 (`PagoSena` acreditada: ¿se devuelve, se traslada, se pierde?). Mitigación: supuesto abierto documentado (ver Preguntas abiertas); C-06 no muta `PagoSena`, solo expone `turno_id` en el evento para que C-07 decida.
- [Riesgo] Doble clic concurrente sobre confirmar/cancelar → doble evento. Mitigación: transición condicional (`UPDATE … WHERE estado = <esperado>`) + idempotencia por `(turno_id, operacion)` en outbox; test de concurrencia en tasks.
- [Compromiso] Evento vs llamada directa añade infraestructura outbox a cambio de desacoplar GATE 6 (C-08/C-09/C-11 en paralelo sin bloquearse).
- [Riesgo] Reloj: DST/zonas si el deploy y la DB difieren. Mitigación: todo en UTC/`timestamptz`, tests con literales `-03:00` del spec.

## Plan de migración

1. Migración C-06 (numeración según convención de C-01): CHECK/transiciones + índice `(estado)`; sin backfill (no hay datos: greenfield).
2. Deploy sin dependencias nuevas (sin credenciales GCal/MP/ARCA; R2).
3. Reversión: revertir migración + endpoints (eventos no consumidos aún por C-09/C-11: pérdida nula).

## Preguntas abiertas

- **OQ-1 (roce C-07)**: al cancelar/reprogramar un turno con seña acreditada, ¿la seña se devuelve, se traslada al nuevo horario o se retiene? Supuesto provisorio: no se muta `PagoSena` en C-06; se deja el dato en el evento. Decisor: dueño + C-07. No cambia specs de C-06 (solo payload del evento).
- **OQ-2**: código exacto de rechazo de ventana (`409` vs `422`) según convención de errores del ADR-01/C-01. Supuesto: `409`. No cambia escenarios (solo el literal del status).
- **OQ-3**: texto final del mensaje de rechazo + contacto del consultorio. Supuesto: plantilla parametrizable `APP_CONTACTO`. No cambia comportamiento.
