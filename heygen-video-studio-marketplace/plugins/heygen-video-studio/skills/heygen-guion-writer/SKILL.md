---
name: heygen-guion-writer
description: >-
  Escribe guiones cortos para videos de avatar (HeyGen) a partir de un tema,
  el contenido de un modulo/leccion, o un documento, y los deja listos en la
  hoja de produccion (Google Sheet) para generarlos en lote. Usa este skill
  siempre que alguien quiera redactar guiones de video, preparar los textos de
  un curso o entrenamiento, convertir material o notas en guiones hablados,
  "escribir los guiones del modulo", o llenar la hoja de guiones antes de
  producir los videos. Complementa al skill heygen-batch-video (ese produce los
  videos; este escribe lo que dice el avatar).
---

# HeyGen Guion Writer — Escribe los guiones

## Que hace

Convierte material de origen (un tema, el contenido de una leccion, notas,
un documento) en **guiones cortos y hablados**, listos para que un avatar los
diga. Luego los carga a la hoja de produccion para generar los videos.

Va antes de `heygen-batch-video`: primero escribes los guiones (este skill),
despues produces los videos (el otro skill).

## Flujo de trabajo

1. **Reune el material.** Pregunta al usuario de donde sale el guion: un tema,
   texto pegado, un archivo, o el temario de un curso. Si te da varios modulos
   o lecciones, trata cada uno como un guion aparte.

2. **Aclara el estilo una vez** (si no lo sabes ya): tono (cercano, formal,
   energico), duracion objetivo, y que avatar usar. No lo vuelvas a preguntar
   en cada guion.

3. **Escribe cada guion** siguiendo la estructura de abajo.

4. **Muestraselos al usuario para aprobacion.** Los guiones se cargan con
   `aprobado = no` por defecto: nadie produce un video hasta que un humano
   revise. Esto es intencional (control de costos y de marca).

5. **Cargalos a la hoja** con el script `scripts/add_guiones.py`, o entrega un
   CSV si el usuario aun no tiene la hoja lista.

## Estructura de un buen guion de video

Cada guion es corto: **30 a 90 segundos hablados ≈ 80 a 160 palabras**. Videos
mas largos cansan y cuestan mas creditos. Usa esta estructura:

1. **Gancho (1 frase):** capta la atencion o dice para que sirve la leccion.
2. **Contenido (2–4 frases):** la idea central, concreta y sin relleno.
3. **Cierre (1 frase):** un siguiente paso o una frase que refuerce.

Escribe para el **oido, no para el ojo**: frases cortas, lenguaje directo,
como si la persona hablara. Nada de listas con vinetas ni parrafos densos —
el avatar los lee en voz alta. Evita siglas sin explicar y numeros complejos.

**Ejemplo:**
Tema: "Como funciona la comision recurrente"
Guion: "Hola, en este video te explico como ganas dinero mes a mes con la
comision recurrente. Cada vez que un cliente que trajiste sigue activo, tu
recibes un porcentaje, sin volver a vender. Mientras el cliente se queda, tu
sigues cobrando. Por eso cuidar a tus clientes vale tanto como conseguir
nuevos. En el proximo video te muestro como construir tu pipeline."

## Reglas de contenido (importante)

- **Fidelidad:** no inventes datos, cifras, promesas ni politicas. Si el
  material no lo dice, no lo afirmes. Marca lo que asumiste.
- **Temas sensibles:** guiones sobre dinero, comisiones, resultados o rangos
  deben quedar SIEMPRE con `aprobado = no` para revision humana. Son riesgo de
  marca y de cumplimiento.
- **Consistencia:** mantén el mismo tono y estilo en todo el lote.

## Como cargar los guiones a la hoja

El script `scripts/add_guiones.py` agrega filas a la hoja de produccion con
`estado = pendiente` y `aprobado = no`. Recibe un archivo JSON con los guiones.

Formato del JSON de entrada:
```json
[
  {"id": "M1-L1", "titulo": "Bienvenida", "guion": "Hola, en este video...", "avatar": "Winston"},
  {"id": "M1-L2", "titulo": "La plataforma", "guion": "Ahora te muestro...", "avatar": "Wina"}
]
```

Ejecuta:
```bash
python scripts/add_guiones.py \
  --sheet-id "<ID_DEL_GOOGLE_SHEET>" \
  --worksheet "Hoja 1" \
  --input guiones.json
```

Usa las mismas variables de entorno y cuenta de servicio de Google que
`heygen-batch-video` (ver `../heygen-batch-video/references/setup.md`).

Si el usuario todavia no tiene la hoja configurada, ofrece entregar los
guiones como CSV con las mismas columnas y que él los pegue.

## Despues de escribir

Recuérdale al usuario el siguiente paso: revisar los guiones, cambiar
`aprobado` a `si` en los que apruebe, y correr `heygen-batch-video` para
producir los videos.
