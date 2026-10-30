# Evidencia 02 — La skill se descubre y se usa

**Fecha**: 29/10/2026
**Objetivo**: comprobar que un agente puede **encontrar** la skill propia con solo las referencias del
proyecto, y que puede **usarla**, sin que nadie le diga el nombre.

## 1. Qué se probó

| Prueba | Cómo | Resultado |
|---|---|---|
| Descubrimiento desde las instrucciones del proyecto | Un subagente nuevo leyó `AGENTS.md` y `.atl/skill-registry.md` y recibió el pedido "antes de implementar C-08, revisá los escenarios de la spec" | Encontró `revisor-escenarios-turnos` por `AGENTS.md` (tabla de skills, sección propia y paso 4 del flujo) y por `.atl/skill-registry.md` |
| Descubrimiento por el runtime (sesión en caliente) | `skill({ name: "revisor-escenarios-turnos" })` dentro de la misma sesión donde se creó la skill | ❌ `Skill "revisor-escenarios-turnos" not found` — el runtime lista las skills **al iniciar** la sesión |
| Descubrimiento por el runtime (sesión nueva) | `opencode run "<consulta>"` (sesión nueva, sin herramientas) | ✅ Respondió `SI, existe` y copió la descripción textual |

## 2. Salida cruda de la sesión nueva

```
> opencode run "Sin usar ninguna herramienta y sin leer archivos: mirando solo tu lista de skills
  disponibles, respondeme en 3 lineas. (1) Existe una skill llamada 'revisor-escenarios-turnos'? SI o NO.
  (2) Si existe, copia su descripcion tal cual aparece. (3) Cuantas skills del proyecto (las de
  .opencode/skills) ves listadas en total?"

1) SI, existe.
2) "Audita una delta spec de OpenSpec del proyecto de turnos odontológicos contra las reglas RN-XX de la
   knowledge base antes de implementarla. Detecta escenarios faltantes (feliz, error de negocio, borde),
   reglas ambiguas o sin cobertura y valores de dominio inventados. Usala cuando se prepara o revisa un
   change de turnos (propose o verify), o cuando el pedido es "revisá los escenarios", "¿falta algún caso
   borde?", "¿esta spec es verificable?", "auditá el spec antes de implementar". Si hay un spec.md de
   turnos por implementar, cargala aunque no nombren la skill."
3) 8 skills de `.opencode/skills` (7 openspec + revisor-escenarios-turnos).
```

## 3. Problema encontrado y cómo lo resolvimos

En la sesión donde creamos la skill, el runtime seguía mostrando 34 skills y **no** la nuestra: la lista de
skills se arma al iniciar la sesión y no se refresca en caliente. No era un problema de formato ni de
ubicación:

- `SKILL.md` válido (`Skill is valid!`, validador de `skill-creator`);
- nombre del directorio == `name` del frontmatter (`revisor-escenarios-turnos`);
- ruta correcta: `.opencode/skills/revisor-escenarios-turnos/SKILL.md`, la misma carpeta donde viven las 7
  skills de OpenSpec que sí aparecen.

Se verificó con una sesión realmente nueva (`opencode run`), tal como pide el TP. **Conclusión**: la skill se
descubre al iniciar sesión; para verla en caliente hay que reiniciar el agente.

## 4. Qué le faltó al agente nuevo

Al probar el pedido real ("revisá los escenarios de C-08") el subagente se topó con que **C-08 todavía no
estaba propuesto**: `openspec/changes/` solo tenía `archive/`. La propia skill lo resuelve: pide la spec en
vez de inventarla. Eso confirma que el orden del flujo es correcto (`propose` → revisar → implementar) y que
la skill no se inventa escenarios cuando el artefacto no existe.
