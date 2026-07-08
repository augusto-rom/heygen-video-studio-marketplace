# Setup (una sola vez por colaborador)

Guía para dejar el generador listo. Hazlo una vez; después solo llenas guiones.

## 1. HeyGen: API key

1. Entra a HeyGen con un plan que incluya API.
2. Ve a Settings → API y copia tu API key.
3. Guárdala como variable de entorno (no la pongas en la hoja ni en el código):

```bash
export HEYGEN_API_KEY="tu_api_key_aqui"
```

## 2. HeyGen: plantilla (Template) por avatar

El script usa plantillas para que todos los videos salgan con la misma marca.

1. En HeyGen crea un video con tu avatar, fondo y logo, y guárdalo como **Template**.
2. Dentro de la plantilla, define un **campo de texto variable llamado exactamente `guion`**. Ese es el texto que cambiará en cada video.
3. Copia el `template_id` (aparece en la URL de la plantilla o vía el endpoint List Templates).
4. Repite para cada avatar que quieras usar.

Tienes dos formas de decirle al script qué plantilla usar:

- **Por fila:** pon el `template_id` en la columna `template_id` de la hoja.
- **Por avatar:** deja la columna `avatar` (ej. "Winston") y define un mapa:

```bash
export HEYGEN_TEMPLATE_MAP='{"Winston":"tmpl_abc123","Wina":"tmpl_def456"}'
```

## 3. Google Sheets: cuenta de servicio

El script lee y escribe la hoja con una "cuenta de servicio" (un robot de Google).

1. En Google Cloud Console, crea un proyecto (o usa uno existente).
2. Habilita **Google Sheets API** y **Google Drive API**.
3. Crea una **Service Account** y genera una llave en formato **JSON**. Descárgala.
4. Guarda la ruta del JSON como variable de entorno:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/ruta/a/credenciales.json"
```

5. Abre tu Google Sheet y **compártelo** con el email de la cuenta de servicio
   (algo como `mi-robot@proyecto.iam.gserviceaccount.com`) con permiso de **Editor**.

## 4. Dependencias de Python

```bash
pip install gspread google-auth requests
```

## 5. Prueba en seco (dry-run)

Antes de gastar créditos, confirma que lee bien la hoja:

```bash
python scripts/generate_batch.py --sheet-id "<ID_DE_TU_SHEET>" --dry-run
```

El `<ID_DE_TU_SHEET>` es la parte de la URL entre `/d/` y `/edit`:
`https://docs.google.com/spreadsheets/d/`**`ESTE_ES_EL_ID`**`/edit`

## 6. Corrida real (con freno de costos)

```bash
python scripts/generate_batch.py --sheet-id "<ID>" --worksheet "Hoja 1" --max 3
```

Empieza con `--max 3` para validar calidad. Súbelo cuando estés seguro.

## Solución de problemas

- **403 / no puede abrir la hoja:** no compartiste la hoja con el email de la
  cuenta de servicio, o falta habilitar las APIs.
- **HeyGen no devuelve video_id:** revisa que el `template_id` sea correcto y que
  la variable dentro de la plantilla se llame exactamente `guion`.
- **Timeout esperando el video:** videos largos tardan; sube el timeout en el
  código o revisa el estado directo en HeyGen.
