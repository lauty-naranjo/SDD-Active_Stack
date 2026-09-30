# Arquitectura Propuesta

> Stack sin imponer (proyecto académico, presupuesto cero). Propuesta best-effort mínima para que MP/ARCA/GCal sean viables en tier gratuito; a confirmar — ver `10_preguntas_abiertas.md` ([DISCOVERY] `stack`, `system_type`).

## Patrones aplicados

| Patrón | Dónde se usa | Por qué |
|--------|--------------|---------|
| Monolito web + API propia | Frontend público + panel + backend único | Presupuesto cero y equipo académico: una sola unidad desplegable |
| Transacción con lock / constraint de exclusión | Alta de turnos (profesional, sillón, intervalo) | Garantiza RN-AGEN-01 ante reservas concurrentes |
| Idempotencia por webhook | Webhooks MP y reintentos ARCA | Evita turnos/facturas duplicadas |
| Token público por turno | Enlaces paciente (gestionar, reclamar hueco) | Opera sin cuenta obligatoria en v1 |
| Deep-link `wa.me` + log | Confirmación manual WhatsApp | Costo cero, sin API Meta en v1 |

## Estructura de directorios

```
proyecto/
├── backend/
│   └── app/
│       ├── domain/            # turnos, agenda, pagos, facturacion, espera
│       ├── application/       # casos de uso: reservar, confirmar, sobreturno, conciliar, facturar
│       └── infrastructure/    # db, mercadopago, arca, gcal, webhooks
└── frontend/
    └── src/
        ├── features/          # reserva-publica, agenda, sobreturnos, pagos, reportes
        ├── shared/            # ui, formato fecha AR, validadores
        └── pages/             # /, /reservar, /turnos/:token, /agenda, /reportes
```

## Seguridad

- Autenticación: panel interno con usuario + contraseña (mínimo v1); enlaces paciente por token único e irrepetible, con expiración.
- Autorización: RBAC según `03_actores_y_roles.md` (paciente solo sus turnos; recepcionista sin configuración; dueño total).
- Validación de input: ventana 24h, anti-solapamiento y topes se validan en backend (nunca solo en frontend); webhooks MP verificados por firma.
- Secrets management: credenciales MP/ARCA y refresh tokens GCal en variables de entorno, nunca en repo; tokens OAuth cifrados en reposo.

## Variables de entorno

| Variable | Descripción | Ejemplo | Sensible |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Conexión DB relacional | `postgres://...` | Y |
| `MP_ACCESS_TOKEN` | Credencial Mercado Pago | `APP_USR-...` | Y |
| `MP_WEBHOOK_SECRET` | Firma de webhooks MP | `...` | Y |
| `ARCA_CUIT` / `ARCA_PTO_VTA` / `ARCA_CERT` / `ARCA_KEY` | Homologación y firma ARCA | `...` | Y |
| `GCAL_CLIENT_ID` / `GCAL_CLIENT_SECRET` | OAuth Google Calendar | `...` | Y |
| `APP_BASE_URL` | URL pública (enlaces y webhooks) | `https://...` | N |
| `SENA_TIMEOUT_MIN` | Liberación de `pendiente_sena` | `30` | N |
