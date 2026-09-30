# Tareas — C-06 gestion-ventana-24h

> Orden: dependencias C-03/C-04/C-05 primero (revisar que existan; si faltan, las tareas 1.x fijan el supuesto). TDD rojo-primero en cada seam (R4); valores esperados = literales del spec (R5); fixtures ficticios (R1, ej. " María Demo "); sin secretos (R2).

## 1. Base de estados en DB

- [x] 1.1 Confirmar supuestos C-03/C-04/C-05 (Turno con estado/token_publico, constraint anti-solapamiento) o fijarlos como stub de interfaz, y verificar que el registro de decisiones de supuestos queda registrado en design.md OQ
- [x] 1.2 Escribir test rojo de transición inválida (`cancelado → confirmado` rechazado a nivel DB) con fixture ficticio, y verificar que falla antes del cambio
- [x] 1.3 Implementar CHECK/transiciones de estados + índice `(estado)` según D4 y verificar que el test 1.2 pasa y `UPDATE` inválido devuelve error desde DB (no solo la aplicación)

## 2. Ventana 24h + confirmar/cancelar por token (TDD)

- [x] 2.1 Escribir tests rojos de ventana con los literales del spec (24h01 acepta con `ahora=2026-10-14T09:59`, 23h59 rechaza con `ahora=2026-10-14T10:01`, 24h00 exactas acepta, inicio `2026-10-15T10:00-03:00`) y verificar que fallan antes de implementar
- [x] 2.2 Implementar `POST /turnos/:token/confirmar` y `POST /turnos/:token/cancelar` con reloj servidor (D2), token vigente/expirado (`404`/`410`) y rechazo `<24h` con mensaje + contacto (`409`), y verificar que los tests 2.1 pasan
- [x] 2.3 Escribir test rojo de cancelación válida que emite un único `HuecoLiberado` con payload completo y libera `[inicio, fin)`, y verificar que falla antes y pasa después de implementar el evento (D1, seam hacia C-09)

## 3. Reprogramación atómica + borde de adyacencia (TDD)

- [x] 3.1 Escribir tests rojos: reprogramación feliz a hueco libre (mismo `id`, `fin` re-derivado, estado `reservado`), adyacencia `fin==inicio` aceptada (`[10:00,10:30)` → vecino `[10:30,11:00)`), destino con intersección real rechazado sin mutar origen + sugerencia de espera, y verificar que fallan antes de implementar
- [x] 3.2 Implementar `POST /turnos/:token/reprogramar` en transacción corta (`FOR UPDATE`, valida ventana del origen, delega anti-solapamiento C-04 con rango semiabierto `'[)'`, `ROLLBACK` + `409` si destino ocupado) y verificar que los tests 3.1 pasan
- [x] 3.3 Escribir test rojo de concurrencia (doble reprogramación/confirmar-cancela simultánea → una gana, un solo evento, sin doble reserva) y verificar que falla antes y pasa después del `UPDATE … WHERE estado=<esperado>` + outbox idempotente

## 4. Staff, página pública y seam GCal

- [x] 4.1 Implementar endpoints staff `POST /turnos/:id/confirmar|cancelar|reprogramar|marcar-atendido|marcar-ausente` con RBAC recepcionista/dueño (misma ventana RN-TUR-01; `atendido/ausente` solo staff) y verificar con test de rol denegado (paciente/rol sin permiso → `403`) y test `ausente ≠ cancelado`
- [x] 4.2 Implementar página `/turnos/:token` (ver estado + confirmar/cancelar/reprogramar sin login, mismos errores de ventana; token inválido → `404` sin filtrar datos) y verificar con E2E sin sesión que cubre borde 23:59/24:01 (webapp-testing)
- [x] 4.3 Publicar `TurnoConfirmado|TurnoCancelado|TurnoReprogramado` en cada cambio aceptado sin escribir en GCal (seam C-11: sin credenciales el flujo sigue `200`) y verificar con test de evento emitido con GCal ausente

## 5. Verificación integral del change

- [x] 5.1 Ejecutar suite completa (transiciones DB + ventana + reprogramación + concurrencia + E2E `/turnos/:token`) y verificar cero regresiones y que ningún test usa datos reales ni secretos
- [x] 5.2 Validar artefactos OpenSpec (`openspec validate --change c-06-gestion-ventana-24h` o `openspec status`) y verificar que proposal/specs/design/tasks figuran `done`
