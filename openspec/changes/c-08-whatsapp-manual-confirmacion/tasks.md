# Tareas — C-08 whatsapp-manual-confirmacion

> Orden: TDD rojo-primero en cada seam (R4). Los valores esperados de los tests son literales del spec, nunca recalculados con la misma función que se está probando (R5). Fixtures ficticios (R1): `Juan Pérez Demo`, `+54 9 11 0000-0001`, `tur-demo-001`. Sin secretos (R2). Stack = Python stdlib + `sqlite3` + `http.server`, igual que `src/c06` (R7): no se agregan frameworks ni dependencias.

## 1. Revisión previa y supuestos

- [ ] 1.1 Ejecutar la skill `revisor-escenarios-turnos` con la ruta `openspec/changes/c-08-whatsapp-manual-confirmacion`, la capability `gestion-turnos` y las RN del scope (`RN-CONF-01/02/03`, `RN-TUR-01/04`) y verificar que no queda ningún hallazgo `BLOQUEANTE` antes de escribir código (artefacto: informe con la matriz RN × escenario)
- [ ] 1.2 Verificar que `design.md` §OQ-2 declara el seam `sesion_actual() -> Sesion | None` (rol `recepcionista`/`dueño`) como interfaz mínima de C-03; si C-03 ya existe, verificar que la firma real coincide con la que consume `src/c08/app.py`
- [ ] 1.3 Verificar que `src/c06/db.py` expone `turnos` con `paciente_telefono`, `estado`, `inicio`, `fin` y que `src/c06/servicio.py` expone `ROLES_STAFF`/`ahora_servidor()`/`_fila_por_id`; si falta algo, verificar que queda escrito como supuesto en `design.md` y que no se duplica la tabla `turnos`

## 2. Migración del log (R3)

- [ ] 2.1 Escribir el test rojo `tests/test_whatsapp_log.py::test_unique_turno_tipo_impide_duplicado_en_db` (dos `INSERT ... ON CONFLICT (turno_id, tipo) DO NOTHING` con el mismo `(turno_id, tipo)`: la segunda devuelve `rowcount == 0` y `SELECT COUNT(*) == 1`) y verificar que falla antes de crear la tabla
- [ ] 2.2 Implementar la migración 008 en `src/c08/db.py` (`mensajes_whatsapp` con CHECK de `tipo`/`canal`, `UNIQUE (turno_id, tipo)`, FK a `turnos(id)`, índice `turno_id`) y verificar que 2.1 pasa y que `PRAGMA index_list('mensajes_whatsapp')` muestra el índice único
- [ ] 2.3 Verificar con `PRAGMA foreign_keys=ON` que un `turno_id` inexistente devuelve `IntegrityError` en `tests/test_whatsapp_log.py::test_fk_turno_inexistente_rechazado`

## 3. Link y plantilla (TDD)

- [ ] 3.1 Escribir `tests/test_whatsapp_link.py::test_encoding_tildes_enye_y_telefono` con los literales del spec: `+54 9 11 0000-0001` → `5491100000001`, el query contiene `Se%C3%B1or%2Fa%20Juan%20P%C3%A9rez%20Demo`, el link no tiene espacios ni `+` crudos y `unquote(text)` devuelve la plantilla renderizada; verificar que falla antes de implementar
- [ ] 3.2 Implementar `normalizar_telefono()` y `construir_link()` en `src/c08/whatsapp.py` con `urllib.parse.quote(texto, safe="")` (D1) y verificar que 3.1 pasa
- [ ] 3.3 Escribir `tests/test_whatsapp_link.py::test_plantilla_feliz_completa` con `ahora = 2026-10-14T08:00:00-03:00` y turno de inicio `2026-10-15T10:00:00-03:00`, afirmando que el texto decodificado contiene `Dra. Demo Uno`, `15/10/2026 10:00`, `Seña: a confirmar con el consultorio` y `Podés cancelar o reprogramar hasta el 14/10/2026 10:00`; verificar que falla antes de implementar
- [ ] 3.4 Implementar `PLANTILLA_CONFIRMACION`/`PLANTILLA_RECORDATORIO` (constantes parametrizables con override `WA_PLANTILLA_CONFIRMACION`) y `construir_mensaje()` con los placeholders de D2 y verificar que 3.3 pasa
- [ ] 3.5 Escribir `tests/test_whatsapp_link.py::test_ventana_vencida_no_promete_ventana` con `ahora = 2026-10-15T02:00:00-03:00`, afirmando que el texto NO contiene `Podés cancelar o reprogramar hasta` y SÍ contiene `Estás dentro de las 24 h previas al turno` más el contacto `APP_CONTACTO`; verificar que falla antes de la rama de D6 y pasa después
- [ ] 3.6 Escribir `tests/test_whatsapp_link.py::test_borde_exacto_24h_si_promete_ventana` con `ahora = 2026-10-14T10:00:00-03:00` (exactamente 24 h de anticipación) y verificar que el texto SÍ contiene `Podés cancelar o reprogramar hasta el 14/10/2026 10:00`; el test debe fallar si la implementación usa `>` en lugar de `>=` (RN-TUR-01)

## 4. Endpoint de log idempotente (TDD)

- [ ] 4.1 Escribir `tests/test_whatsapp_log.py::test_log_feliz_registra_quien_cuando_y_tipo` (`201`, 1 fila, `canal = manual_wa_me`, `enviado_por = recepcion-demo-01`, `enviado_en = 2026-10-14T08:00:00-03:00`, turno sigue `reservado`) y verificar que falla antes de implementar
- [ ] 4.2 Escribir `tests/test_whatsapp_log.py::test_rechazo_turno_cancelado_no_muta_ni_loguea` (`409`, estado `cancelado`, `COUNT(*) == 0`) y `::test_rechazo_turno_pendiente_sena_no_loguea` (`409`, estado `pendiente_sena`, 0 filas), y verificar que fallan antes de implementar
- [ ] 4.3 Implementar `POST /turnos/:id/whatsapp-log` en `src/c08/app.py` más `registrar_envio()` en `src/c08/servicio.py` con `INSERT ... ON CONFLICT (turno_id, tipo) DO NOTHING`, `enviado_en` del reloj inyectado y rechazo `409` fuera de `reservado|confirmado` (D4), y verificar que 4.1 y 4.2 pasan
- [ ] 4.4 Verificar la idempotencia secuencial con `tests/test_whatsapp_log.py::test_segundo_post_es_idempotente`: segunda llamada → `200` con `duplicado: true`, 1 sola fila y el `enviado_en` original intacto
- [ ] 4.5 Escribir `tests/test_whatsapp_concurrencia.py::test_dos_posts_concurrentes_una_fila` con dos conexiones `sqlite3` reales al mismo archivo temporal, `threading.Barrier` y `PRAGMA busy_timeout`, y verificar que el test falla contra una implementación con `SELECT` previo (afirma: 1 fila para `(tur-demo-001, confirmacion)`, status en `{200, 201}` y ninguna excepción ni `5xx`)
- [ ] 4.6 Ajustar la transacción (`BEGIN IMMEDIATE` + `busy_timeout`, con la lectura de estado y el alta dentro de la misma transacción) hasta que 4.5 pase de forma estable, y verificarlo corriendo el test 20 veces seguidas (`for ($i=1; $i -le 20; $i++) { python -m pytest tests/test_whatsapp_concurrencia.py -q }`) sin fallos intermitentes
- [ ] 4.7 Escribir `tests/test_whatsapp_log.py::test_sin_sesion_401_y_rol_no_staff_403` y verificar que `mensajes_whatsapp` no registra filas en ninguno de los dos casos y que el turno conserva `reservado`
- [ ] 4.8 Escribir `tests/test_whatsapp_log.py::test_ausente_y_atendido_rechazados` (turnos `tur-demo-004` en `ausente` y `tur-demo-005` en `atendido` → `409`, 0 filas para cada uno) y verificar que falla antes del guard de estado y pasa después
- [ ] 4.9 Escribir `tests/test_whatsapp_log.py::test_tipo_invalido_422_sin_fila` (`{"tipo": "ofrecimiento_hueco"}` → `422`, turno en `reservado`, `COUNT(*) == 0`) y verificar que falla si la resolución de conflicto absorbe el `CHECK` como duplicado
- [ ] 4.10 Escribir `tests/test_whatsapp_log.py::test_enviado_por_del_body_se_ignora` (`{"tipo": "confirmacion", "enviado_por": "admin-falso"}` → `201` con `enviado_por = "recepcion-demo-01"`) y verificar que falla si la implementación lee el campo del cuerpo
- [ ] 4.11 Escribir `tests/test_whatsapp_log.py::test_recordatorio_sobre_confirmado` (`{"tipo": "recordatorio"}` sobre `tur-demo-006` en `confirmado` → `201`, 1 fila con `tipo = "recordatorio"`, turno sigue `confirmado`) y verificar que falla si el guard de estado excluye `confirmado`

## 5. Panel y confirmación manual

- [ ] 5.1 Escribir `tests/test_whatsapp_panel.py::test_panel_dia_siguiente_solo_reservados` con los tres turnos literales del spec (`tur-A` incluido, `tur-B` de otra fecha, `tur-C` cancelado) y `ahora = 2026-10-14T18:00:00-03:00`, y verificar que falla antes de implementar
- [ ] 5.2 Implementar `GET /agenda/pendientes-confirmacion` en `src/c08/app.py` (fecha por defecto = día siguiente según `ahora_servidor()`, filtro `estado = 'reservado'`, link precalculado por turno) y verificar que 5.1 pasa
- [ ] 5.3 Escribir `tests/test_whatsapp_panel.py::test_confirmar_tras_respuesta_conserva_log` (log previo de `confirmacion` → `POST /turnos/tur-demo-001/confirmar` → `200`, estado `confirmado`, 1 fila de log con el mismo `enviado_por`/`enviado_en`), implementar la ruta staff `POST /turnos/:id/confirmar` en `src/c08/app.py` delegando en `servicio.confirmar_por_id` de C-06 (C-06 solo publica la ruta por `token`) sin modificar `src/c06/*`, y verificar que el test falla antes (ruta inexistente) y pasa después
- [ ] 5.4 Verificar con `tests/test_whatsapp_sin_meta.py::test_flujo_sin_credenciales_meta` que, con el entorno sin `WHATSAPP_*` ni `META_*` y `socket.create_connection` sustituido por un doble que falla si se invoca, el link se genera y el log responde `201` con `canal = manual_wa_me` y cero conexiones salientes (US-021 CA-3)
- [ ] 5.5 Escribir `tests/test_whatsapp_panel.py::test_panel_sin_sesion_401_y_rol_no_staff_403` y verificar que el cuerpo de ninguna de las dos respuestas contiene el nombre, el teléfono ni el link `wa.me` del paciente (KB `03_actores_y_roles.md`)
- [ ] 5.6 Escribir `tests/test_whatsapp_panel.py::test_borde_zona_horaria_dia_siguiente` con `ahora = 2026-10-15T01:00:00+00:00` (22:00 del 14/10 en `-03:00`) y `tur-A` con inicio `2026-10-15T10:00:00-03:00`, afirmando que el default devuelve `[tur-A]`; el test debe fallar si el día se calcula con la fecha UTC
- [ ] 5.7 Escribir `tests/test_whatsapp_panel.py::test_fecha_invalida_400` (`?fecha=15-10-2026` → `400` sin turnos ni links) y verificar que falla antes de la validación de formato

## 6. Verificación integral

- [ ] 6.1 Ejecutar `python -m pytest -q` completo y verificar suite de C-06 en verde (cero regresiones), que ningún test usa datos reales y que no hay credenciales en el código (R1/R2)
- [ ] 6.2 Ejecutar `openspec validate c-08-whatsapp-manual-confirmacion --strict` y verificar que proposal, design, specs y tasks figuran sin errores de validación
- [ ] 6.3 Re-ejecutar la skill `revisor-escenarios-turnos` sobre el change ya implementado y verificar que no quedan hallazgos `BLOQUEANTE` ni `MAYOR` abiertos (cierre de la revisión de 1.1)
- [ ] 6.4 Verificar la trazabilidad escenario → tarea recorriendo los 19 escenarios de `specs/gestion-turnos/spec.md` y confirmando que cada uno está nombrado por al menos una tarea de este archivo (ningún escenario huérfano)

## 7. Documentación y cierre (al archivar, no antes)

- [ ] 7.1 Actualizar `CHANGES.md` sección `### [C-08] whatsapp-manual-confirmacion` a `[x]` con la migración 008 y los tests agregados, y verificar que el árbol de dependencias y los gates siguen coherentes (solo al archivar; no editar durante la implementación)
- [ ] 7.2 Archivar el change con `/opsx:archive c-08-whatsapp-manual-confirmacion` y verificar que `openspec/specs/gestion-turnos/spec.md` incorpora los requisitos nuevos sin perder los de C-06
