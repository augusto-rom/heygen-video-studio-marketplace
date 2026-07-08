# HeyGen Video Studio

Plugin para producir videos de avatar con HeyGen en serie, de punta a punta:
**escribir los guiones** y **generar los videos** a partir de una hoja de
produccion (Google Sheet). Es genérico y portátil — no depende de ningún LMS,
sitio web ni CMS.

## Qué incluye

Dos skills que trabajan en cadena:

1. **heygen-guion-writer (El Guionista)**
   Convierte un tema, el contenido de una lección o un documento en guiones
   cortos y hablados, y los carga a la hoja de producción listos para revisar.

2. **heygen-batch-video (El Productor)**
   Toma los guiones aprobados de la hoja, genera los videos en HeyGen y escribe
   la URL de cada video de vuelta en la hoja.

## Cómo se usa (flujo completo)

1. "Escríbeme los guiones de estos módulos" → el Guionista los redacta y los
   carga a la hoja con `aprobado = no`.
2. Revisas los guiones y cambias `aprobado` a `si` en los que apruebes.
3. "Genera los videos pendientes del sheet" → el Productor los produce y
   completa la columna `video_url`.

## Setup (una sola vez por persona)

Cada colaborador necesita:

- **HEYGEN_API_KEY** — API key de HeyGen (plan con API).
- **GOOGLE_APPLICATION_CREDENTIALS** — ruta al JSON de una cuenta de servicio
  de Google, con la hoja compartida a ese email como Editor.
- **Una plantilla en HeyGen** por avatar, con una variable de texto llamada
  `guion`. El `template_id` va en la hoja, o en `HEYGEN_TEMPLATE_MAP`.

Guía detallada: `skills/heygen-batch-video/references/setup.md`.

Dependencias de Python:
```bash
pip install gspread google-auth requests
```

## Seguridad y control

- **Los secretos nunca viven en el plugin** — van en variables de entorno. Por
  eso es seguro compartirlo.
- **Freno de costos:** el Productor siempre corre con `--max` (tope de videos
  por corrida).
- **Aprobación humana:** los guiones entran con `aprobado = no`; nada se produce
  hasta que una persona lo aprueba. Los guiones sobre dinero, comisiones o
  rangos deben revisarse siempre.

## Versión

0.1.0 — primera versión.
