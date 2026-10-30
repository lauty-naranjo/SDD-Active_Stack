---
name: revisor-escenarios-turnos
description: Audita una delta spec de OpenSpec del proyecto de turnos odontológicos contra las reglas RN-XX de la knowledge base antes de implementarla. Detecta escenarios faltantes (feliz, error de negocio, borde), reglas ambiguas o sin cobertura y valores de dominio inventados. Usala cuando se prepara o revisa un change de turnos (propose o verify), o cuando el pedido es "revisá los escenarios", "¿falta algún caso borde?", "¿esta spec es verificable?", "auditá el spec antes de implementar". Si hay un spec.md de turnos por implementar, cargala aunque no nombren la skill.
---

# Revisor de escenarios de turnos

Audita una delta spec de OpenSpec contra las reglas RN-XX de la knowledge base antes de que se implemente. El objetivo es que el código nazca de escenarios verificables y de valores que la KB ya decidió, no de valores que el agente completa porque suenan razonables.

## Cuándo usarme

- Al preparar un change de turnos (`propose`) o al verificarlo antes de archivar (`verify`).
- Cuando el pedido es "revisá los escenarios", "¿falta algún caso borde?", "¿esta spec es verificable?", "auditá el spec antes de implementar".
- Cuando hay un `specs/<capability>/spec.md` de turnos por implementar, aunque nadie nombre esta skill.

No la uses para escribir la spec desde cero (eso es `openspec-propose`) ni para implementar.

**Solo lee y reporta.** No edites la spec, las tasks ni el código: si encontrás un hueco lo describís con su
cita, y la corrección la decide el equipo. Un revisor que reescribe pierde la trazabilidad de qué estaba mal.

## Contexto del proyecto

- Reglas de negocio: `knowledge-base/05_reglas_de_negocio.md` (códigos `RN-{DOMINIO}-{NN}`).
- Modelo y funcionalidades: `knowledge-base/04_modelo_de_datos.md` y `06_funcionalidades.md` cuando el escenario toca entidades o historias.
- Valores abiertos: `knowledge-base/10_preguntas_abiertas.md`.
- Scope por change: la sección "Leer antes" de `CHANGES.md`.
- Changes: `openspec/changes/<name>/`; specs archivadas en `openspec/changes/archive/`.
- Reglas duras en `AGENTS.md`: R1 (fixtures ficticios, nunca datos reales de pacientes en escenarios ni ejemplos), R3 (integridad y anti-solapamiento en DB), R4 (TDD en concurrencia, idempotencia y ventana 24h), R5 (sin tests tautológicos).

## Entradas

1. Ruta del change (`openspec/changes/<name>/`).
2. Capability afectada (carpeta bajo `specs/`).
3. Lista de RN del scope, tomada de "Leer antes" en `CHANGES.md`.
4. Archivos de `knowledge-base/` que correspondan a esas RN.

Si falta cualquiera, pedila. No completes el scope con RN que la KB no asigne al change.

## Procedimiento

Seguí el orden; cada paso alimenta al siguiente.

1. **Extraer la spec.** Leé `specs/<capability>/spec.md` y listá cada `### Requirement:` con sus `#### Scenario:`. El formato del repo es DADO / CUANDO / ENTONCES en viñetas.
2. **Extraer las RN del scope.** Tomá los códigos de "Leer antes" en `CHANGES.md` y leé su texto literal en `05_reglas_de_negocio.md`; sumá `04_modelo_de_datos.md` o `06_funcionalidades.md` si el requirement toca entidades o historias.
3. **Armar la matriz de cobertura.** Una fila por RN del scope, una columna por tipo de escenario: feliz, error de negocio, borde, concurrencia/idempotencia. Marcá cada celda con el escenario que la cubre o con `HUECO`. Una RN sin escenario es un hallazgo, no una omisión aceptable.
4. **Validar la forma de cada escenario.** Debe tener DADO/CUANDO/ENTONCES completo, valores literales (fechas con zona, estados, códigos HTTP), un resultado observable, y en los errores de negocio la constancia de que NO se muta estado. Si dice "funciona correctamente" o "responde error", no es verificable.
5. **Detectar valores de dominio inventados.** Compará números, montos, topes, plazos y estados contra `10_preguntas_abiertas.md`. Monto de seña, tope de sobreturnos, timeout de `pendiente_sena`, duraciones del catálogo, sede única y DNI están abiertos: si la spec los fija, es BLOQUEANTE (R5: nada inventado).
6. **Revisar bordes temporales y de concurrencia.** Reloj del servidor vs. reloj del cliente; igualdad exacta del umbral (24h00 acepta, `< 24h` rechaza); doble solicitud concurrente sobre el mismo hueco; encoding de URLs con tildes, ñ y `+54 9`; fecha del sistema real cuando debería estar fijada. Un escenario que siembra una fecha fija sin congelar el reloj caduca solo (pasó en `tests/test_e2e_pagina.py::test_confirmar_sin_login`).
7. **Verificar `tasks.md`.** Cada escenario debe tener una tarea que diga cómo se verifica al implementarlo. Si la tarea no existe o no nombra el test, el escenario no se va a cumplir.

## Salida

Informe markdown con estas secciones, en este orden:

1. **Tabla de cobertura**: `RN | Requirement | Feliz | Error de negocio | Borde | Concurrencia/idempotencia`, con `HUECO` donde falte.
2. **Hallazgos**: tabla `Severidad | Hallazgo | Cita (archivo:línea) | RN`. Usá `BLOQUEANTE`, `MAYOR` o `MENOR`.
3. **Preguntas abiertas detectadas**: las de `10_preguntas_abiertas.md` que la spec tocó y resolvió por su cuenta.
4. **No verificado**: lo que no pudiste comprobar y por qué.

## Severidad

- **BLOQUEANTE**: valor abierto inventado, RN crítica sin escenario, error de negocio que muta estado, o violación de R3 o R4 (validar solapamiento solo en aplicación, falta test de concurrencia/idempotencia/ventana).
- **MAYOR**: escenario no verificable, falta un borde relevante o el `tasks.md` no dice cómo verificarlo.
- **MENOR**: redacción ambigua que no cambia el comportamiento.

## Criterios de revisión del informe

- Ningún hallazgo sin cita a una RN o a un archivo de la KB con línea.
- Ningún valor numérico propuesto que la KB no respalde.
- Mínimo 3 escenarios por requirement crítico (ventana 24h, anti-solapamiento, estados, idempotencia de pago).
- Prohibido proponer tests tautológicos: el valor esperado sale de la RN o de un ejemplo trabajado, no de recalcular lo que hace el código.

## Ejemplo de hallazgo

`BLOQUEANTE | La spec fija la seña en $5.000 cuando la KB la declara abierta | specs/<capability>/spec.md:23 | RN-PAGO-01`
