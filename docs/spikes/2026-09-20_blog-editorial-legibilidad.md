# Spike: cómo escribir mejor blogs. Legibilidad y escaneo

| **Fecha:** 2026-09-20                                                               |
| ----------------------------------------------------------------------------------- |
| **Tipo:** spike de investigación (sin código)                                       |
| **Pregunta:** ¿qué técnicas editoriales sutiles mejoran un blog sin cambiar su voz? |

## Resumen

La mejora más barata no es "escribir más bonito", es hacer el texto escaneable. NNGroup midió +124% de usabilidad combinando tres cambios: conciso, escaneable y objetivo. El resto son detalles de estructura, ritmo y contraste que respetan cómo la gente realmente lee en web (escanea, lee 20-28% de palabras, patrón en F).

## Hallazgos

### 1. NNGroup — Concise, Scannable, Objective (Morkes & Nielsen, 1997, vigente)
- Usuarios escanean, no leen lineal; leen ~20-28% de palabras, patrón en F. 79% escanea antes de leer.
- Test controlado (5 versiones, mismo contenido): **conciso +58%**, **escaneable +47%**, **objetivo +27%**, **combinado +124%** vs control con marketese.
- Conciso = -50% palabras sin perder tareas; escaneable = listas, negritas clave, headings, bloques cortos; objetivo = hechos sin hipérbole.

### 2. Guías ES 2025-2026 (eesel.ai, butterflai.pro, getlinko, blogerhub, readings.space)
- Estructura: 1× H1, H2/H3 jerárquicos, sentence case más conversacional. Headings deben contar la historia solos.
- Párrafos 2-4 oraciones, 1 idea. Variar longitud para ritmo; evitar muros de 6+ (en móvil ocupan pantalla completa).
- Listas solo si ≥3 ítems paralelos o secuencia; negrita 1 frase cada pocos párrafos — si todo destaca, nada destaca.
- Front-load / pirámide invertida: primera oración = takeaway; skimmers solo leen eso.

### 3. Tipografía y layout (Baymard, Ruder)
- Columna 600-750px, 50-75 caracteres por línea; >80 fatiga y abandono.
- Cuerpo ≥16px (ideal 18-20px), line-height ≥1.5. Probar móvil y zoom 150%.

### 4. WCAG 1.4.3 Contrast (Minimum) — AA
- Texto normal ≥4.5:1, grande (18pt / 14pt bold) ≥3:1. Rationale: compensa 20/40 (~80 años). AAA: 7:1 / 4.5:1.

## Principios

1. **Conciso** — corta lo que no aporta (+58%).
2. **Escaneable** — anclas visuales: headings, negritas, listas (+47%).
3. **Objetivo** — hechos sobre hipérbole (+27%); juntos +124%.

Regla de oro: una idea por párrafo, conclusión primero (pirámide invertida), variar longitud para ritmo.

## Estructura

- **1× H1** (título), **H2** para secciones principales, **H3** solo si la sección necesita subdivisión. No saltar niveles por estética.
- Headings descriptivos en *sentence case* ("Cómo elegir verde para acentos" > "EL VERDE PERFECTO"). Test rápido: lee solo los headings — si cuentan la historia, están bien.
- Introducción de 2 párrafos cortos que prometen valor; cierre que resume o da siguiente paso, no relleno.
- Front-load: primera oración de cada sección/párrafo lleva el takeaway. Skimmers leen solo eso.

## Párrafos y frases

- **2-4 oraciones por párrafo**, 1 idea. Evitar muros de 6+ oraciones; en móvil un muro llena toda la pantalla.
- Alternar corto/medio/largo para ritmo. Una oración de 1 línea aislada es buen énfasis ocasional.
- Oraciones ≤20-25 palabras ideal. Voz activa, verbos concretos. Define jerga una vez, luego úsala consistente.
- Espacio en blanco es contenido: `line-height ≥1.5`, separación generosa entre secciones.

## Listas y énfasis

- **Viñetas** para ítems paralelos sin orden; **numeradas** para secuencias/pasos.
- No convertir todo en listas — fragmenta la narrativa. Úsalas cuando reducen esfuerzo (≥3 ítems paralelos).
- **Negrita** con cuentagotas: 1 frase clave cada pocos párrafos. Si todo está en negrita, nada destaca. Cursiva solo para matiz/títulos.
- Citas en bloque solo para idea que debe detenerse y leerse aparte.

## Tipografía y layout

- Columna de texto **600-750px** en desktop, **50-75 caracteres por línea** (Ruder/Baymard). Más de 80 fatiga.
- Cuerpo **≥16px**, ideal **18-20px**. Probar zoom 150% y móvil real — sin scroll horizontal.
- Imágenes pegadas al punto que ilustran, con `alt` descriptivo. Evitar decorativas sin aporte.

## Accesibilidad mínima (WCAG AA)

- **Contraste 1.4.3**: texto normal ≥4.5:1, texto grande (18pt / 14pt bold) ≥3:1 sobre fondo. Cubre ~20/40 de agudeza (típica a los 80 años). AAA sube a 7:1 / 4.5:1.
- **1.4.1 Uso de color**: no comunicar solo con color (ej. link sin subrayado necesita 3:1 vs cuerpo + subrayado en hover/focus).
- **1.4.11 No-text**: UI y gráficos esenciales ≥3:1 contra adyacentes.

## Links

- Texto descriptivo ("criterio de contraste AA" > "haz clic aquí").
- Para conceptos que no todo lector domina, enlaza a referencia estable: ej. [WCAG Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), [Número áureo](https://es.wikipedia.org/wiki/N%C3%BAmero_%C3%A1ureo).

## Checklist pre-publicar (2 min)

- [ ] Título = único H1, headings cuentan la historia solos
- [ ] Ningún párrafo >4 oraciones ni dos muros seguidos
- [ ] Cada sección abre con su conclusión en 1ª oración
- [ ] 1-2 negritas por sección, listas solo donde aclaran
- [ ] Columna y tamaño probados en móvil
- [ ] Contraste verificado (WebAIM Contrast Checker)
- [ ] Links con texto descriptivo
- [ ] Lectura en voz alta sin tropiezos

## Qué omitir a propósito

Plantillas pesadas, H2/H3 por cada párrafo, negrita masiva, tablas para todo, y reescrituras para "optimizar Flesch" ciego. Añadir solo si el post busca snippet/GEO o es guía larga — YAGNI para post personal.

## Fuentes

- NNGroup — Concise, SCANNABLE, and Objective: https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/
- eesel.ai — Cómo dar formato a una entrada de blog (2026): https://www.eesel.ai/es/blog/how-to-format-a-blog-post
- butterflai.pro — Formato de publicaciones de blog: https://butterflai.pro/es/blog/formato-publicaciones-blog
- getlinko — Listas y viñetas para GEO: https://getlinko.com/formato-de-contenido-seo-listas-vinetas/
- blogerhub — Improve Blog Readability Checklist: https://blogerhub.com/improve-blog-readability/
- W3C WCAG 2.2 — 1.4.3 Contrast (Minimum): https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- WebAIM — Contrast and Color: https://webaim.org/articles/contrast/
- MDN — Color contrast: https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Understanding_WCAG/Perceivable/Color_contrast
