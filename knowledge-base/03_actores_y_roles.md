# Actores y Roles

## Actores del sistema

| Actor | Descripción | Cómo interactúa |
|-------|-------------|-----------------|
| Paciente | Persona que reserva atención odontológica; público general, sin cuenta pesada en v1 | Web pública 24/7: consulta disponibilidad, reserva, confirma/cancela/reprograma, paga seña |
| Recepcionista / secretaria | Gestiona la agenda diaria, confirma manualmente, cobra y concilia | Panel interno: agenda multi-profesional/sillón, sobreturnos, lista de espera, confirmación WhatsApp manual |
| Odontólogo / dueño | Configura agenda, prestaciones y reglas; supervisa ocupación y cobros | Panel interno: configuración (prestaciones, duraciones, bloqueos, topes, seña), reportes |

## RBAC — Matriz de permisos

| Rol | Turnos (propios) | Agenda (todos) | Configuración | Pagos / facturación | Reportes |
|-----|------------------|----------------|---------------|---------------------|----------|
| Paciente (no autenticado / identidad liviana) | R propia reserva, U/Cancelar-Reprogramar (ventana 24h) | R disponibilidad real | — | Pagar seña propia | — |
| Recepcionista | CRUD turnos, confirmar, sobreturnos, lista de espera | CRUD (bloqueos, reasignar) | R (sin editar reglas) | Cobrar, conciliar | R básicos |
| Odontólogo / dueño | CRUD total | CRUD total | CRUD (prestaciones, duraciones, topes, seña, sync GCal) | CRUD + facturar ARCA | R + exportar |

## Rutas públicas

- Catálogo de disponibilidad y reserva online (`/`, `/reservar`, `/disponibilidad`).
- Confirmación / cancelación / reprogramación con token de turno (`/turnos/:token/...`).
- Pago de seña (checkout Mercado Pago + retorno/webhook).
- Todo el panel interno (`/agenda`, `/configuracion`, `/reportes`, `/facturacion`) requiere autenticación con rol.
