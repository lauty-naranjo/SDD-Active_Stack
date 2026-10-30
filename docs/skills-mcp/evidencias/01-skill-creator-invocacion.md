# Evidencia 01 — Uso de la skill creadora `skill-creator`

**Fecha**: 29/10/2026
**Skill creadora**: `skill-creator` (repositorio `anthropics/skills`), instalada en
`C:\Users\ramir\.config\opencode\skills\skill-creator\`
**Skill generada**: `.opencode/skills/revisor-escenarios-turnos/SKILL.md`

## 1. Cómo se invocó

Se cargó la skill con la herramienta `skill` del agente (`skill({ name: "skill-creator" })`) y se le pasó el
diseño ya cerrado de la skill propia (propósito, disparador, entradas, procedimiento, salida y criterios de
revisión), para saltear la entrevista inicial y trabajar en modo "draft + validación".

## 2. Qué pautas de `skill-creator` se aplicaron

| Pauta de `skill-creator` | Cómo se aplicó |
|---|---|
| El `description` del frontmatter es el disparador real, y conviene que sea explícito ("pushy") | La descripción nombra frases literales del usuario ("revisá los escenarios", "¿falta algún caso borde?") y aclara que se cargue aunque no se nombre la skill |
| Cuerpo conciso; progressive disclosure en vez de copiar el dominio | La skill **no** copia las RN: las busca en `knowledge-base/05_reglas_de_negocio.md` y `10_preguntas_abiertas.md` en tiempo de ejecución |
| Explicar el porqué de cada paso, no solo ordenar | Cada paso del procedimiento dice qué omisión detecta (por ejemplo, por qué hay que congelar el reloj) |
| Frontmatter mínimo: `name` + `description` | Se usó solo eso; `license`/`metadata` no aportaban |

## 3. Adaptaciones nuestras sobre lo generado

`skill-creator` produjo un borrador de 72 líneas. Lo revisamos y le agregamos:

1. **Alcance de solo lectura**: la skill no edita la spec ni el código, solo reporta con cita. Sin esto, el
   revisor reescribía la spec y se perdía la trazabilidad de qué estaba mal.
2. **R1 en el contexto**: los escenarios y ejemplos deben usar datos ficticios, nunca datos reales de
   pacientes (regla dura del repo).

Archivo final: **75 líneas**.

## 4. Validación (salida cruda)

Problema encontrado y resuelto: el validador de `skill-creator` necesita `pyyaml`, que no estaba instalado.

```
ModuleNotFoundError: No module named 'yaml'
```

Se instaló con `python -m pip install --user pyyaml` y se repitió la validación:

```
> python "C:\Users\ramir\.config\opencode\skills\skill-creator\scripts\quick_validate.py" ".opencode\skills\revisor-escenarios-turnos"
Skill is valid!
EXIT=0
```

## 5. Comprobación de disponibilidad

La skill aparece en la lista de skills disponibles del agente con su nombre y descripción, y se carga con
`skill({ name: "revisor-escenarios-turnos" })`. El nombre del directorio coincide con el `name` del
frontmatter, requisito de opencode (`^[a-z0-9]+(-[a-z0-9]+)*$`).
