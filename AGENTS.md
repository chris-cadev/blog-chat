# Project Commands

Run these through mise (e.g. `mise run test`):

- `mise run test` — run the test suite with coverage (`pytest -v --cov=blog_chat ...`)
- `mise run build` — build frontend assets into `static/` (`bun run build`)
- `mise run migrate` — apply pending DB migrations (uses `DATABASE_URL` from `.env`)
- `mise run dev` — run the dev server with hot reload (starts tmux session)
- `mise run deploy` — build frontend, migrate DB, then start the Docker Compose stack

# Contenido — `scripts/` → `content/`

## Flujo normal (borrador → publicado)

```bash
python scripts/new_post.py "Título del post"
# crea content/_drafts/YYYY-MM-DD-HHMM.md con frontmatter title/created/updated
# e intenta abrir nvim/code; si no, edita el .md a mano

python scripts/set_slug.py content/_drafts/2026-09-19-1848.md mi-slug-kebab en
# valida slug kebab-case y lang en {en,es,fr}, añade slug/lang/lang_group,
# mueve a content/<lang>/<slug>.md; falla si ya existe (no sobreescribe)
```

## Estructura y frontmatter

- `content/_drafts/*.md` — borradores (parser los incluye; `lang` ausente → cae en `mixed` en listados).
- `content/<lang>/<slug>.md` con `lang ∈ {en,es,fr}` — post publicado. Traducciones del mismo tema comparten `lang_group` (= `slug` base). Indefinidos van a `content/mixed/`.
- Frontmatter que entiende `src/blog_chat/features/posts/parser.py:7` y `services.py:8`: `title` (fallback: stem), `slug` (fallback: stem), `created`/`updated` (`YYYY-MM-DD`), `description`, `tags: []`, `lang`, `lang_group`, `content` (body). `created/updated` ordenan el índice (`services.py:15`, descendente).
- Assets: imágenes locales → `src/assets/posts/<nombre>` se publica en `/static/posts/` (lógica de `scripts/migrate_posts.py:293`). Audio de borradores → `content/_drafts/*.wav|mp3|opus` servido en `/drafts` (`src/blog_chat/app.py:100`).

## Scripts auxiliares

- `scripts/compress_audio.py input.wav [--bitrate 32k] [--format mp3|opus]` — requiere `ffmpeg`; genera `.mp3`/`.opus` mono 16kHz optimizado para voz (ej. draft con 3 `<source>` como en `content/_drafts/2026-09-19-1848.md:54`).
- `scripts/migrate_posts.py [--source /path] [--dry-run]` — solo migración histórica desde `chris-cadev/blog` (`content/logs|posts|pre` → `content/<lang>/`), resuelve shortcodes Hugo y copia imágenes. No usar para flujo diario.

# Estilo editorial — legibilidad y escaneo

Fuente: `docs/spikes/2026-09-20_blog-editorial-legibilidad.md` (síntesis de NNGroup Morkes & Nielsen + guías ES 2025-2026 + WCAG 1.4.3). Es el estándar para todo `.md` en `content/`.

Principios (medidos): **conciso +58%, escaneable +47%, objetivo +27% → combinado +124%** vs. marketese. Gente escanea (79%), lee 20-28% palabras, patrón en F.

Aplicar al escribir/editar borradores:

- **1 idea por párrafo, conclusión primero** (pirámide invertida). 1ª oración = takeaway; skimmers solo leen eso.
- **Párrafos 2-4 oraciones**, ≤20-25 palabras/oración, voz activa. Varía corto/medio/largo para ritmo; nunca dos muros de 6+ seguidos (en móvil llena pantalla). `line-height ≥1.5`.
- **Estructura:** 1× H1 (título), H2 secciones principales, H3 solo si subdivide. No saltar niveles. Headings en *sentence case* descriptivos; test: lee solo headings — si cuentan la historia, ok. Intro 2 párrafos cortos que prometen valor; cierre resume o siguiente paso.
- **Listas y énfasis:** viñetas para ≥3 ítems paralelos sin orden, numeradas para secuencias. Negrita con cuentagotas (1 frase clave cada pocos párrafos; si todo destaca nada destaca). Citas solo para idea que debe detenerse.
- **Tipografía/layout:** columna 600-750px, 50-75 caracteres/línea; cuerpo ≥16px (ideal 18-20px). Probar móvil y zoom 150% sin scroll horizontal.
- **Accesibilidad AA:** contraste normal ≥4.5:1, grande (18pt/14pt bold) ≥3:1 (`WCAG 1.4.3`). No comunicar solo con color (1.4.1); UI/gráficos ≥3:1 (1.4.11). Verificar con WebAIM Contrast Checker.
- **Links e imágenes:** texto descriptivo (`criterio de contraste AA` > `haz clic aquí`); enlaza conceptos no triviales a refs estables (WCAG, Wikipedia); imágenes junto al punto que ilustran con `alt` descriptivo; evita decorativas.

Checklist pre-publicar (2 min, del spike):

- [ ] Título único H1, headings cuentan historia solos
- [ ] Ningún párrafo >4 oraciones ni dos muros seguidos
- [ ] Cada sección abre con conclusión en 1ª oración
- [ ] 1-2 negritas por sección, listas solo donde aclaran
- [ ] Columna/tamaño probados en móvil
- [ ] Contraste verificado
- [ ] Links con texto descriptivo
- [ ] Lectura en voz alta sin tropiezos

Qué omitir a propósito (YAGNI para post personal): plantillas pesadas, H2/H3 por cada párrafo, negrita masiva, tablas para todo, reescritura para Flesch ciego. Solo si el post busca snippet/GEO o es guía larga.

# Spikes — cómo escribir uno como `2026-09-20_blog-editorial-legibilidad.md`

Ubicación: `docs/spikes/YYYY-MM-DD_<tema>-<subtema>.md`. Tipo: spike de investigación **sin código** (decisión/documentación).

Estructura a replicar:

1. **Cabecera tabla** `Fecha | Tipo: spike de investigación (sin código) | Pregunta: ¿...?` — una pregunta enfocada.
2. **Resumen** (3-5 líneas) con el insight más barato y el dato cuantitativo que lo sostiene.
3. **Hallazgos** numerados, cada uno con fuente y cifra: ej. NNGroup experimento controlado (5 versiones, +58/+47/+27/+124), guías ES 2025-2026, Baymard/Ruder layout, WCAG 1.4.3 con thresholds. Enlaza URLs canónicas.
4. **Principios** (3 máx., numerados, con % si hay).
5. **Secciones prescriptivas** derivadas de hallazgos: Estructura, Párrafos y frases, Listas y énfasis, Tipografía y layout, Accesibilidad mínima, Links — cada una con reglas accionables y límites numéricos (2-4 oraciones, 600-750px, 4.5:1, etc.).
6. **Checklist pre-publicar** copiable (checkboxes markdown).
7. **Qué omitir a propósito** — explicita YAGNI para evitar sobre-ingeniería.
8. **Fuentes** — lista de URLs consultadas (NNGroup, guías ES, WCAG, WebAIM, MDN).

Reglas de estilo del spike mismo: dogfooding del editorial — conciso/escaneable/objetivo, headings sentence case que cuentan la historia, front-load, negrita mínima, sin tablas pesadas. Si citas experimento, da n, condiciones y vigencia; si es guía fechada, marca año (2025-2026).
