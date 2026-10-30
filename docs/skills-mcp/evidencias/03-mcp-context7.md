# Evidencia 03 — Uso real del MCP Context7

**Fecha**: 29/10/2026
**Servidor**: `context7` (remoto, `https://mcp.context7.com/mcp`)
**Herramientas usadas**: `resolve-library-id` y `query-docs`

## 1. Verificación de conexión

```
> opencode mcp list

•  ✓ context7 connected
   https://mcp.context7.com/mcp
•  ✓ engram connected
   engram mcp
—  2 server(s)
```

## 2. Solicitud 1 — `resolve-library-id`

**Pedido**: ubicar la librería SQLite, orientada a inserción idempotente con constraint `UNIQUE`,
`INSERT OR IGNORE`, transacciones y bloqueo de escritura en `sqlite3` de Python.

**Resultado (recortado)**:

| Library ID | Reputación | Snippets | Benchmark |
|---|---|---|---|
| `/websites/sqlite_docs` | High | 9384 | 76.7 |
| `/sqlite/sqlite` | Low | 1375 | 62.63 |
| `/dolthub/doltlite` | High | 1142 | 63.32 |
| `/websites/sqlite-utils_datasette_io_en_stable` | High | 2386 | 80.5 |

**Decisión**: usar `/websites/sqlite_docs` (documentación oficial con la mayor cantidad de fragmentos).

## 3. Solicitud 2 — `query-docs`

**Pedido**: `INSERT OR IGNORE` con constraint `UNIQUE` para evitar filas duplicadas de log, y comportamiento
de las transacciones con escritores concurrentes.

**Resultado (fragmentos textuales)**:

> **IGNORE** — When an applicable constraint violation occurs, the IGNORE resolution algorithm skips the one
> row that contains the constraint violation and continues processing subsequent rows of the SQL statement as
> if nothing went wrong. […] No error is returned for uniqueness, NOT NULL, and UNIQUE constraint errors when
> the IGNORE conflict resolution algorithm is used.
> — https://www.sqlite.org/lang_conflict.html

> **UPSERT** — UPSERT is a clause added to INSERT that causes the INSERT to behave as an UPDATE or a no-op if
> the INSERT would violate a uniqueness constraint. […] If the insert operation would cause the conflict
> target uniqueness constraint to fail, then the insert is omitted and the corresponding DO NOTHING or DO
> UPDATE operation is performed instead.
> — https://www.sqlite.org/lang_upsert.html

> **Isolation And Concurrency** — WAL mode permits simultaneous readers and writers. […] In WAL mode, SQLite
> exhibits "snapshot isolation". […] Any write transactions that commit while the read transaction is active
> are still invisible to the read transaction.
> — https://www.sqlite.org/isolation.html

## 4. Qué aportó al change C-08

Entró directo en el `design.md`:

1. **Idempotencia del log de WhatsApp sin lógica en la aplicación**: `UNIQUE (turno_id, tipo)` +
   `INSERT OR IGNORE` (o `ON CONFLICT DO NOTHING`), en vez de un `SELECT` previo seguido de `INSERT`. La
   fuente confirma que `IGNORE` no lanza error en violaciones de `UNIQUE` y sigue con el resto de la
   sentencia.
2. **Concurrencia**: confirma que en sqlite un escritor bloquea a los demás y que con WAL los lectores no se
   bloquean. Eso justifica dejar la carrera resuelta por la constraint (R3) y no por un chequeo previo.
3. **Consecuencia para los tests**: el escenario de doble `POST` concurrente tiene que ejecutarse con dos
   conexiones reales, no simulando el segundo insert.

## 5. Límites respetados

- Consultas solo sobre documentación pública: no se enviaron datos del proyecto, de pacientes ni
  credenciales.
- No se usó el MCP para escribir nada: el repo y la base los modificamos nosotros.
- La API key no se usó (acceso anónimo); si se usara, iría en `.env` (R2).

## 6. Problema encontrado

La documentación de opencode y la de Context7 **se contradicen** en cómo se manda la API key:

- opencode: `"headers": { "CONTEXT7_API_KEY": "{env:CONTEXT7_API_KEY}" }`
- Context7: `Authorization: Bearer <key>`

Se resolvió siguiendo la del servidor (el que valida el header es Context7, no opencode) y quedó anotado en
el `README.md` §MCP. Sin key no aplica: el servidor acepta acceso anónimo.
