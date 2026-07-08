---
name: heygen-batch-video
description: >-
  Genera videos con avatar de HeyGen en serie (en lote) a partir de una lista
  de guiones en un Google Sheet. Usa este skill siempre que alguien quiera
  producir varios videos de HeyGen de una vez, crear videos de entrenamiento o
  cursos por lotes, "generar los videos del sheet", automatizar la creacion de
  videos con avatar, o convertir una lista/hoja de guiones en videos —
  aunque no mencione la palabra "HeyGen" explicitamente. No publica en ningun
  LMS ni CMS: solo produce los videos y devuelve las URLs.
---

# HeyGen Batch Video — Generador de videos en serie

## Que hace este skill

Convierte una hoja de guiones (Google Sheet) en videos de HeyGen, uno por fila,
sin trabajo manual. Toma cada guion aprobado, lo envia a HeyGen con el avatar
indicado, espera a que el video se genere y escribe la URL del video de vuelta
en la misma hoja.

Es **genérico y portátil**: cualquier colaborador con la API key de HeyGen y
acceso a la hoja puede correrlo. No depende de ningun sitio web, LMS ni CMS.

## Cuando usarlo

- "Genera los videos que estan pendientes en el sheet"
- "Necesito 20 videos de entrenamiento, ya tengo los guiones"
- "Corre el lote de videos de HeyGen"
- Cualquier produccion de varios videos de avatar a partir de una lista.

## Requisitos previos

El colaborador necesita tener, una sola vez:

1. **API key de HeyGen** (plan pago con API) en la variable de entorno
   `HEYGEN_API_KEY`.
2. **Una plantilla (Template) en HeyGen** por cada avatar, con una variable de
   texto llamada `guion`. El `template_id` va en la hoja o en el mapa de
   avatares (ver `references/setup.md`).
3. **Acceso a Google Sheets** mediante una cuenta de servicio. La ruta al JSON
   de credenciales va en `GOOGLE_APPLICATION_CREDENTIALS`.

Si falta alguno de estos, **detente y pideselo al usuario** antes de correr
nada. No inventes valores ni claves.

## Estructura de la hoja (Google Sheet)

La primera fila son los encabezados. Cada fila siguiente es un video:

| Columna       | Obligatoria | Que es |
|---------------|-------------|--------|
| `id`          | si          | Identificador unico del video (ej. M1-L1) |
| `titulo`      | si          | Titulo del video en HeyGen |
| `guion`       | si          | El texto que habla el avatar |
| `template_id` | si*         | Plantilla de HeyGen a usar (*o se resuelve por `avatar`) |
| `avatar`      | no          | Nombre logico del avatar (se mapea a un template_id) |
| `aprobado`    | si          | `si` para permitir generar. Freno de costos. |
| `estado`      | auto        | pendiente / en_proceso / listo / error |
| `video_url`   | auto        | La llena el script cuando el video esta listo |
| `video_id`    | auto        | ID de HeyGen, para rastreo |

Regla clave: el humano solo llena `guion`, `template_id`/`avatar` y pone
`aprobado = si` + `estado = pendiente`. El resto lo escribe el script.

## Como ejecutarlo

El trabajo pesado lo hace `scripts/generate_batch.py`. **Preferí usar ese
script en vez de escribir codigo nuevo** — ya maneja reintentos, el freno de
costos y la escritura de vuelta a la hoja.

```bash
python scripts/generate_batch.py \
  --sheet-id "<ID_DEL_GOOGLE_SHEET>" \
  --worksheet "Hoja 1" \
  --max 10
```

Que hace el script, paso a paso:

1. Lee la hoja y filtra filas con `estado = pendiente` **y** `aprobado = si`.
2. Aplica el limite `--max` (freno de costos): nunca genera mas de N por corrida.
3. Por cada fila, llama a HeyGen (`POST /v2/template/{template_id}/generate`),
   guarda el `video_id` y marca `estado = en_proceso`.
4. Consulta el estado hasta que el video termina, y entonces escribe
   `video_url` y `estado = listo`. Si falla, marca `estado = error`.

## Reglas de seguridad (importante al compartir)

- **Freno de costos:** siempre corre con `--max`. Sin limite, un error en la
  hoja (filas duplicadas) podria generar cientos de videos y quemar creditos.
- **Aprobacion previa:** el script ignora filas sin `aprobado = si`. Esto evita
  producir guiones a medio escribir.
- **Secretos fuera del codigo:** la API key y las credenciales viven en
  variables de entorno, nunca dentro del skill ni de la hoja. Asi es seguro
  compartir el skill sin exponer claves.
- **Dry-run:** para ver que se enviaria sin generar nada, corre con `--dry-run`.

## Antes de una corrida grande

Calcula el costo: (numero de filas aprobadas) x (creditos por minuto de tu plan)
x (minutos promedio por video). Confirmalo con el usuario antes de producir todo
el lote. Sugerí siempre una corrida piloto de 1–2 videos primero.

## Archivos de referencia

- `references/setup.md` — como crear la plantilla en HeyGen, la cuenta de
  servicio de Google, y configurar las variables de entorno. Leelo cuando el
  usuario no tenga el setup listo.
- `assets/hoja-ejemplo.csv` — ejemplo de la estructura de la hoja para copiar.
