# Propuesta — C-06 gestion-ventana-24h

## Por qué

Sin gestión post-reserva el turno queda congelado: el paciente no puede confirmar, cancelar ni reprogramar, y el consultorio pierde el hueco cuando alguien no puede asistir. C-06 cierra el ciclo de vida del turno (US-020) imponiendo la ventana de 24h (RN-TUR-01) y una máquina de estados trazable (RN-TUR-04), de modo que cada cancelación válida libere el hueco hacia la lista de espera (RN-SOB-04).

## Qué cambia

- Endpoints paciente sin login (token público de C-03/C-05): `POST /turnos/:token/confirmar`, `POST /turnos/:token/cancelar`, `POST /turnos/:token/reprogramar` (con `nuevo_inicio` en body).
- Equivalentes autenticados para recepcionista (`POST /turnos/:id/confirmar|cancelar|reprogramar`, roles recepcionista/dueño según matriz RBAC).
- Validación de ventana 24h en backend: `inicio - ahora < 24h` → rechazo `409`/`422` con mensaje claro + contacto del consultorio (RN-TUR-01); sin validación solo en frontend.
- Máquina de estados persistida: `reservado → confirmado → atendido | ausente | cancelado` (más `pendiente_sena → reservado` preexistente de C-05/C-07, referenciado pero no redefinido); transiciones inválidas rechazadas; `ausente` ≠ `cancelado` siempre (RN-REP-02).
- Cancelación válida libera el hueco y emite evento `HuecoLiberado` consumido por C-09 (hook RN-SOB-04); reprogramación válida es atómica (libera origen + ocupa destino o nada).
- Página pública `/turnos/:token` (gestión sin login: ver estado + botones confirmar/cancelar/reprogramar) + acciones equivalentes en panel de recepcionista.
- Sync GCal del cambio declarado como seam hacia C-11 (evento emitido, no implementación).

## Capacidades

### Capacidades nuevas

- `gestion-turnos`: confirmar/cancelar/reprogramar con ventana 24h, máquina de estados del turno, página `/turnos/:token`, evento `HuecoLiberado` hacia lista de espera y seam GCal.

### Capacidades modificadas

- Ninguna (greenfield relativo: C-01…C-05 no implementados; este change introduce la capability; no hay spec existente que modificar).

## Impacto

- **Depende de**: C-05 (`Turno` con `estado`, `origen`, `token_publico`; concepto de turno reservable) y C-03 (`token_publico` único con expiración, RBAC recepcionista/dueño). Requiere anti-solapamiento transaccional de C-04 en reprogramación.
- **Desbloquea**: C-08 (confirmación WhatsApp manual opera sobre estados de C-06), C-09 (consume `HuecoLiberado`), C-11 (consume evento de cambio para sync GCal), C-12 (reportes leen estados `ausente`/`cancelado`/`atendido`).
- **APIs nuevas**: 3 endpoints públicos por token + 3 equivalentes autenticados; página `/turnos/:token`.
- **DB**: CHECK constraints de transición de estados + índice `(turno, estado)` (detalle en el diseño); sin cambios a `PagoSena` (C-07) salvo supuesto documentado sobre destino de la seña al reprogramar/cancelar.
