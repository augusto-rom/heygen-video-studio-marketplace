# Augusto Romano — Claude Plugin Marketplace

Marketplace de plugins para **Claude Cowork** y **Claude Code**.

## Plugins disponibles

### 🎬 HeyGen Video Studio
Produce videos de avatar con HeyGen en serie, de punta a punta:
escribe los guiones y genera los videos a partir de una hoja de producción
(Google Sheet). Genérico y portátil — no depende de ningún LMS ni CMS.

Incluye dos skills:
- **Guionista** — convierte un tema o material en guiones cortos y hablados.
- **Productor** — genera los videos en HeyGen y devuelve las URLs.

## Cómo instalar

### En Claude Code

```bash
# 1. Agrega este marketplace (una sola vez)
/plugin marketplace add TU_USUARIO/heygen-video-studio-marketplace

# 2. Instala el plugin
/plugin install heygen-video-studio
```

> Reemplaza `TU_USUARIO/heygen-video-studio-marketplace` por la ruta real de tu
> repositorio en GitHub (formato `usuario/repo`).

### En Cowork

Agrega el marketplace desde la configuración de plugins usando la URL del
repositorio, y luego instala **HeyGen Video Studio** desde la lista.

## Configuración (una sola vez por usuario)

Cada persona necesita, en su propio entorno:

- `HEYGEN_API_KEY` — API key de HeyGen (plan con API).
- `GOOGLE_APPLICATION_CREDENTIALS` — ruta al JSON de una cuenta de servicio de
  Google, con el Sheet compartido a ese email como Editor.
- Una plantilla en HeyGen por avatar, con una variable de texto llamada `guion`.

Guía detallada dentro del plugin: `plugins/heygen-video-studio/README.md` y
`plugins/heygen-video-studio/skills/heygen-batch-video/references/setup.md`.

Dependencias de Python:
```bash
pip install gspread google-auth requests
```

## Seguridad

Los secretos (API keys, credenciales) **nunca viven en el plugin**. Cada usuario
usa los suyos vía variables de entorno. El marketplace es seguro de compartir
públicamente.

## Licencia

Define aquí tu licencia (por ejemplo MIT) antes de publicar.
