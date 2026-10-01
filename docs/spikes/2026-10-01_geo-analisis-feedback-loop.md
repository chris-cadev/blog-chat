# Spike: opciones GEO para un feedback loop cercano en blog-chat

| **Fecha:** 2026-10-01                                                               |
| ----------------------------------------------------------------------------------- |
| **Tipo:** spike de investigación (sin código)                                       |
| **Pregunta:** ¿qué implementaciones GEO (paquetes o propias) encajan en blog-chat y cuáles merecen entrar en el top 5? |

> **Estado:** top 5 propio implementado el 2026-10-01 (JSON-LD, about, `/llms.txt`, checklist, `geo_qa.py`) sin paquetes GEO nuevos. Evaluación independiente: `docs/spikes/2026-10-01_geo-analisis-feedback-loop_evaluacion-muse.md`. Qué se dejó fuera y por qué: sección "Estado de implementación" más abajo.

## Resumen

geo-score.online dio 45/100 a blog.chrislabs.net. Los puntos reales no son robots ni sitemap (ambos ya en 100), sino citabilidad del contenido, schema JSON-LD ausente, E-E-A-T débil y knowledge graph casi nulo. Un bucle cercano aquí no se logra con un SaaS que audita la URL viva: el blog ya guarda el contenido en `content/{en,es}/*.md`. La mejora más barata es código propio (JSON-LD + llms.txt + checklist) y, después, un QA delgado o un paquete maduro. Tras la evaluación, `geo-opt` sale del top por licencia no OSI y madurez baja; entra `geo-optimizer-skill` (MIT, 600+ estrellas) por generadores que pueden cubrir schema y llms.txt sin escribirlos a mano.

## Contexto del proyecto

- Contenido: markdown con frontmatter en `content/en`, `content/es` (48 posts por idioma) y `content/_drafts` (~10 borradores).
- Parser propio: `src/blog_chat/features/posts/parser.py` extrae `title`, `slug`, `description`, `tags`, `created`, `updated`, `lang`, `lang_group`, `content`.
- Ya existe: `/robots.txt` (Allow: * + sitemap), `/sitemap.xml` dinámico, OG/Twitter tags, canonical.
- Falta hoy: `application/ld+json`, `llms.txt`, RSS, página de autor, FAQ estructurada, densidad de citas/fuentes en cuerpo.
- Voz: spike editorial del 2026-09-20 (conciso, escaneable, objetivo). Recomendaciones tipo "expandir a 1000-1500 palabras + FAQ" del SaaS chocan con ese estándar en posts personales.

## Hallazgos

### 1. Qué midió geo-score y qué es atacable localmente

| Pilar geo-score | Score | Señal | Atacable sin SaaS |
| --- | --- | --- | --- |
| Content Quality | 23 | Citability 0, LSI 5, Answer completeness 5, Factual density 61 | Sí, parcial: estructura, citas, stats, headings |
| AI Readiness | 50 | AI optimization 17, Content structure 60, Semantic clarity 98 | Sí: schema, front-loading, FAQ en guías |
| Technical Basis | 70 | Schema validator 15, Freshness 15; bots 100, sitemap 100 | Sí: JSON-LD, lastmod, llms.txt |
| Authority & Trust | 30 | E-E-A-T 12, Knowledge graph 13, Citations 50 | Medio: about/autor y sameAs; poco paquete |

### 2. Investigación GEO (Princeton KDD 2024)

Paper: **Aggarwal et al.**, "GEO: Generative Engine Optimization", KDD 2024 (arXiv:2311.09735). No es Singh et al.

Métodos con mayor uplift de visibilidad en respuestas de GE (hasta +40% en GEO-bench; el abstract también cita hasta +37% en Perplexity):

- **Cite Sources**, **Quotation Addition**, **Statistics Addition**: entre los métodos con mejor mejora relativa en las métricas del paper (Position-Adjusted Word Count e impression subjetiva). El spike original redondeaba "+30-40%" sin citar tabla; tratarlos como rango del paper, no como cifra auditada línea a línea.
- **Fluency** y **Easy-to-Understand**: también suben visibilidad (~15-30% en las tablas del paper). Compatible con el estilo del blog.
- **Keyword stuffing**: no rinde como en SEO clásico.
- Efecto por dominio: law/gobierno se beneficia de estadísticas; people/society y history de citas textuales. Un blog personal de reflexión se parece más a lo segundo que a un hub de productos.

### 3. AutoGEO (ICLR 2026) y MAGEO (Findings ACL 2026)

- AutoGEO (repo `cxcscmu/AutoGEO`, MIT, ~223 estrellas) extrae preferencias de un motor generativo y reescribe documentos. El número "+50.99% sobre baseline de Princeton" aparece en materiales del proyecto; no se re-verificó contra el paper completo en la evaluación. Tratarlo como claim del repo, no como hecho auditado aquí.
- MAGEO (repo `Wu-beining/MAGEO`) es un loop multi-agente con fidelity gate. Cita correcta: **Findings** of ACL 2026, no track principal.
- Ambos son marcos de investigación con APIs de LLM y datasets. Coste de adopción alto para un blog personal; no son "un pip install y corre en draft".

### 4. Familia de paquetes locales 2026 (hechos corregidos)

| Paquete | Instalación correcta | Licencia real | Madurez | Qué aporta / notas |
| --- | --- | --- | --- | --- |
| `@ijonis/geo-lint` | `npm install -D @ijonis/geo-lint` | MIT | Baja (~38 estrellas) | **92 reglas** sobre `.md`, JSON con `suggestion`, loop de fix. El changelog crece; hay que recurar severidades |
| `geo-opt` | `npx geo-opt audit` (Node 22+) | Tooltician Community 1.0 (source-available, **no OSI**; MIT solo histórico hasta `67f18be`) | Baja (0 estrellas, 983 tests) | Audit de markdown KDD-grounded (structure, stats, quotes, citations, clarity). No es base de workflow aquí |
| `ai-visibility` | `pip install ai-visibility[fastapi,cli]` | MIT | Baja (v0.5.0, autor unico) | `score_page()` en 7 dimensiones; **también** `generate_llms_txt` y `article_schema`. Bus factor 1, ecosistema comercial CrawlPod |
| `geo-optimizer-skill` | `pip install geo-optimizer-skill` | MIT | **Alta** (~600+ estrellas, v4.x) | `geo audit`, `geo fix`, **`geo llms`**, **`geo schema`**, citability 47 métodos, MCP, CI. El más maduro del grupo |
| `geo-ai-search-optimization` | npm `geo-ai-search-optimization@2.8.2` | MIT | Baja (mantenedor único) | Superficie enorme; evitar como base |
| `llmscout-cli` | `npm install -g llmscout-cli` o `pip install llmscout-cli` | MIT | Baja (0 estrellas) | 21 checks PASS/WARN/FAIL, cero browser. Smoke de URL publicada, no gate de PRs personales |
| `@dariodario/geochecker` | `npx @dariodario/geochecker <url>` | Open source (ver LICENSE) | Baja | Score por URL + `--min-score` CI. Spot check del sitio publicado |
| `auto-geo` | `npm i -g auto-geo` | MIT | Media | doctor/write/fix/check/history. SOP comercial pisa voz si se impone en todos los posts |
| `geo-audit` (g-shevchenko) | `git clone` + `bash scripts/install.sh` (no pip simple) | MIT | Muy baja (1 estrella) | Multi-módulo. Instalación pesada; no loop diario |
| Canonry / GeoLook / zoomer-geo | Plataformas | Por verificar | Plataformas | YAGNI confirmado para este repo |
| ~~B3 `geo-toolkit`~~ | **No existe** | N/A | N/A | npm `Not found`, PyPI 404. Eliminado del análisis (evaluación independiente) |

### 5. Implementaciones propias (sin paquete)

El parser y las rutas ya exponen todo lo necesario para un score mínimo sin dependencias nuevas:

1. **JSON-LD Article** en `post.html` (headline, datePublished, dateModified, author, description, image, inLanguage).
2. **JSON-LD Organization/WebSite + Person** en home/about (sameAs a GitHub/LinkedIn).
3. **`/llms.txt`** generado desde `get_posts()` (mismo patrón que sitemap).
4. **Script de QA de contenido** que lea markdown, separe frontmatter y cuerpo, y mida: longitud, oraciones largas, headings, FAQs, enlaces externos, números/citas, alt de imágenes. Salida estilo linter.
5. **Checklist GEO** alineada al spike editorial, no a marketese: front-load, una idea por párrafo, fuentes cuando se afirman hechos, FAQ solo en guías.
6. **RSS/Atom** y `lastmod` más honesto en sitemap (freshness 15).
7. **Página about** con biografía corta, enlaces y datos de contacto (E-E-A-T).

**Opción omitida en la primera versión:** guías oficiales gratis (Google AI optimization guide, schema.org, llmstxt.org). No son un paquete, pero son la referencia autoritativa para E1/E2 y no cuestan mantenimiento.

### 6. Por qué un SaaS de URL viva es mal loop para este repo

- El feedback más barato ocurre en `content/_drafts/*.md` antes de `set_slug`.
- geo-score no ve drafts ni frontmatter; solo el HTML publicado.
- Su recomendación de longitud larga ignora el estándar editorial del propio repo.
- Authority/KG no se arreglan con un linter de posts; necesitan páginas y entidades del sitio.

## Principios de puntuación

Cada opción se puntúa 0-5 en siete ejes. Peso total = suma ponderada, convertida a /100.

| Eje | Peso | 5 significa |
| --- | --- | --- |
| Loop | 22% | Feedback en segundos sobre markdown local, sin deploy |
| Voz | 18% | No fuerza reescritura SEO que rompa el estilo editorial |
| Coste | 15% | Menos de ~2h de implementación o cero código nuevo |
| Cobertura | 15% | Ataca puntos débiles reales del reporte geo-score |
| Evidencia | 12% | Método anclado en investigación o reglas reproducibles |
| Mantenimiento | 10% | Casi nada que actualizar tras el primer día |
| Privacidad | 8% | Contenido no sale de la máquina; licencia clara |

Fórmula: `(loop*0.22 + voz*0.18 + coste*0.15 + cobertura*0.15 + evidencia*0.12 + mantenimiento*0.10 + privacidad*0.08) * 20`.

### Limitaciones del rubric (reconocidas en la evaluación)

1. **Sesgo a código propio.** Loop + Voz suman 40% y premian E1-E4 casi siempre.
2. **Doble conteo.** Coste y Midtenimiento miden casi lo mismo; Loop y Privacidad se solapan (local implica privado).
3. **Licencia solo implícita.** No hay eje propio; una licencia source-available puede quedar igual que MIT si no se penaliza Privacidad/Coste.
4. **Orden fino no es solo score.** El ranking final también considera dependencias (un generador que resuelve E1/E2 puede ir por delante de un script que aún no existe).

## Opciones evaluadas

### Grupo A. Linters y audits de markdown

#### A1. `@ijonis/geo-lint`

- **Qué es:** linter npm de contenido. Config con `contentPaths` sobre `content/en`, `content/es`, `content/_drafts`. JSON por violación con `suggestion` y `fixStrategy`. Instalar: `npm install -D @ijonis/geo-lint`.
- **Reglas útiles aquí:** word count, readability, question headings, citation density, E-E-A-T signals, technical (llms.txt, feeds). **92 reglas** (MIT, ~38 estrellas).
- **Riesgo:** muchas reglas SEO/guía larga; ruleset que crece y obliga a recurar severidades; mezcla SEO con GEO sin etiqueta por regla.
- **Puntuación (corregida):** Loop 5, Voz 3, Coste 4, Cobertura 4, Evidencia 3, Mantenimiento 3, Privacidad 5 → **78/100**.

#### A2. `geo-opt` audit de markdown

- **Qué es:** CLI local. Dimensiones Structure, Statistics, Quotations, Citations, Clarity. Thresholds para CI. Grounding KDD 2024 con etiquetas de evidencia. Requiere **Node 22+**.
- **Encaje:** alineado con citability 0 y factual density en posts técnicos o guías.
- **Riesgo (corregido):** licencia **Tooltician Community 1.0**, source-available, no OSI; MIT solo histórico. 0 estrellas. Privacidad original (5) era contradictoria con una licencia con branding Pro.
- **Puntuación (corregida):** Loop 4, Voz 3, Coste 3, Cobertura 4, Evidencia 4, Mantenimiento 3, Privacidad 2 → **68/100**. Fuera del top 5.

#### A3. `geo-ai-search-optimization`

- **Qué es:** CLI npm amplio v2.8.2, MIT, mantenedor único (citability, eeat, readability, schema, images...).
- **Riesgo:** superficie enorme y ecosistema frágil para un blog personal.
- **Puntuación:** Loop 4, Voz 2, Coste 2, Cobertura 4, Evidencia 3, Mantenimiento 1, Privacidad 4 → **58/100**.

#### A4. `llmscout-cli`

- **Qué es:** 21 checks PASS/WARN/FAIL. Paquetes reales: **`llmscout-cli`** en npm y PyPI (no "LLMScout" instalable a secas). MIT, 0 estrellas.
- **Riesgo:** más técnico-SEO que citabilidad de contenido; audita URL viva, no drafts.
- **Puntuación (Cobertura corregida a 4 por cubrir JSON-LD, llms.txt, Organization y FAQ):** Loop 4, Voz 3, Coste 4, Cobertura 4, Evidencia 3, Mantenimiento 4, Privacidad 5 → **76/100**. Smoke en modo WARN; nunca gate de PRs personales.

### Grupo B. Paquetes Python de scoring

#### B1. `ai-visibility` (PyPI)

- **Qué es:** `score_page()` en front-loading, E-E-A-T, headings, schema coverage, fact density, snippability, crawler access. También **`generate_llms_txt`** y **`article_schema`** (útiles para E1/E2). Encaja en FastAPI/pdm.
- **Riesgo:** v0.5.0, autor único, bus factor; menos "fix suggestions" que geo-lint.
- **Puntuación:** Loop 4, Voz 4, Coste 4, Cobertura 4, Evidencia 3, Mantenimiento 4, Privacidad 5 → **79/100**.

#### B2. `geo-optimizer-skill` (PyPI)

- **Qué es:** el paquete más maduro del set. MIT, ~600+ estrellas. `geo audit`, `geo fix`, **`geo llms`**, **`geo schema`**, citability 47 métodos, `geo citations` con API key, MCP, CI.
- **Por qué sube:** los generadores resuelven buena parte de E1/E2 sin programar la ruta a mano. Orientado a sitio, pero el loop local de audit/fix existe.
- **Puntuación (corregida):** Loop 4, Voz 3, Coste 4, Cobertura 5, Evidencia 4, Mantenimiento 4, Privacidad 4 → **79/100**. Entra al top 5.

#### B3. `geo-toolkit`

- **Eliminado.** npm `Not found`, PyPI 404. No instalable. Puntuar vapor invalida la tabla.

### Grupo C. Auditoría de URL viva

#### C1. `@dariodario/geochecker` (npx)

- **Qué es:** score 0-100 en structure, citability, crawlability, freshness, authority. Flag `--min-score` para CI. Comando real: `npx @dariodario/geochecker <url>` (scoped).
- **Encaje:** diagnóstico periódico del sitio publicado, no del draft.
- **Puntuación:** Loop 2, Voz 2, Coste 5, Cobertura 3, Evidencia 3, Mantenimiento 4, Privacidad 3 → **60/100**.

#### C2. `auto-geo doctor`

- **Qué es:** audit de citación readiness por URL con arquitectura estricta (TL;DR, H2 pregunta, FAQ, JSON-LD).
- **Riesgo:** la arquitectura SOP es estilo landing/contenido comercial. Pisa la voz del blog si se usa como mandato en todos los posts.
- **Puntuación:** Loop 2, Voz 1, Coste 4, Cobertura 4, Evidencia 4, Mantenimiento 3, Privacidad 3 → **57/100**.

#### C3. `geo-audit` (g-shevchenko)

- **Qué es:** toolkit MIT multi-módulo (crawl lite, schema, citability, content, brand mentions).
- **Riesgo (corregido):** no es `pip install` simple; es clone + install.sh, Node/Playwright opcionales. 1 estrella. Auditoría pesada.
- **Puntuación (Coste bajado):** Loop 2, Voz 2, Coste 2, Cobertura 4, Evidencia 4, Mantenimiento 2, Privacidad 3 → **52/100**.

#### C4. geo-score.online manual / de pago

- **Qué es:** el referente del reporte (€1.99 o trial).
- **Riesgo:** sin loop local, sin drafts, sin git. Sirve como baseline, no como workflow.
- **Puntuación:** Loop 1, Voz 2, Coste 5, Cobertura 4, Evidencia 2, Mantenimiento 5, Privacidad 1 → **55/100**.

### Grupo D. Citación real en motores

#### D1. `auto-geo check`

- **Qué es:** pregunta a Perplexity/OpenAI/Anthropic/Gemini y mide si citan el dominio. Guarda history.
- **Encaje:** ground truth de outcome, no de readiness. Caro en API keys y ruidoso para un blog en es.
- **Puntuación:** Loop 2, Voz 3, Coste 2, Cobertura 3, Evidencia 5, Mantenimiento 2, Privacidad 2 → **54/100**.

#### D2. `geo citations` (geo-optimizer-skill)

- **Qué es:** mismo problema que D1 vía Python.
- **Puntuación:** Loop 2, Voz 3, Coste 2, Cobertura 3, Evidencia 4, Mantenimiento 2, Privacidad 2 → **51/100**.

#### D3. Canonry / GeoLook / zoomer-geo

- **Qué es:** plataformas self-hosted de monitoring, tickets, KG, multi-engine. Repos Canonry y GeoLook existen en GitHub.
- **Riesgo:** YAGNI brutal para un blog-chat personal. Días de setup, no horas.
- **Puntuación:** Loop 1, Voz 1, Coste 0, Cobertura 5, Evidencia 3, Mantenimiento 0, Privacidad 3 → **35/100**.

### Grupo E. Implementación propia sobre el código existente

#### E1. JSON-LD Article + Organization/Person en templates

- **Qué es:** inyectar `application/ld+json` en `post.html` y en home/about usando datos del parser (title, description, dates, slug, lang, author). Alternativa: `article_schema` de ai-visibility o `geo schema` de geo-optimizer-skill.
- **Ataca:** Schema validator 15, parcialmente E-E-A-T y knowledge graph (si hay about + sameAs).
- **Coste:** 1-2h. Sin dependencias propias. Validable con test de que el template contiene JSON-LD.
- **Puntuación (Loop corregido a 3: es cambio de template, no loop de escritura):** Loop 3, Voz 5, Coste 5, Cobertura 5, Evidencia 4, Mantenimiento 5, Privacidad 5 → **89/100**.

#### E2. Ruta `/llms.txt` generada desde el índice de posts

- **Qué es:** endpoint FastAPI estilo sitemap: H1 del sitio, secciones por idioma, títulos + descriptions + URLs. Alternativa: `geo llms` (geo-optimizer-skill) o `generate_llms_txt` (ai-visibility) si el output encaja con `get_posts()`.
- **Ataca:** AI discovery, parcialmente platform specificity.
- **Coste:** &lt;1h copiando el patrón de `sitemap()`, o envolver un generador existente.
- **Puntuación:** Loop 3, Voz 5, Coste 5, Cobertura 4, Evidencia 3, Mantenimiento 5, Privacidad 5 → **83/100**.

#### E3. Script propio de QA de contenido con el parser

- **Qué es:** `scripts/geo_qa.py` (o similar) que usa `parse_markdown_file`, puntúa 5-8 señales KDD (stats, citas externas, headings, FAQ, longitud de oración, alt de imágenes) y imprime findings accionables.
- **Ventaja:** cero dependencias nuevas, mismo lenguaje del repo, umbral configurable por tipo de post (guía vs diario).
- **Riesgo:** hay que mantener las reglas; sin ecosistema de rulesets listos.
- **Puntuación:** Loop 5, Voz 5, Coste 4, Cobertura 4, Evidencia 4, Mantenimiento 3, Privacidad 5 → **88/100**.

#### E4. Checklist GEO en el flujo editorial (AGENTS.md / new_post / set_slug)

- **Qué es:** ampliar el checklist pre-publicar con 4-6 items GEO alineados a KDD y al spike editorial (front-load, fuente cuando hay dato, FAQ solo en guías, alt descriptivo, description frontmatter completa).
- **Coste:** &lt;30min.
- **Riesgo:** no es un score; depende de disciplina.
- **Puntuación:** Loop 4, Voz 5, Coste 5, Cobertura 3, Evidencia 3, Mantenimiento 5, Privacidad 5 → **85/100**.

#### E5. RSS/Atom + lastmod honesto

- **Qué es:** feed por idioma y `lastmod` preciso en sitemap.
- **Ataca:** Content freshness 15 y señales de syndication.
- **Puntuación:** Loop 2, Voz 5, Coste 4, Cobertura 2, Evidencia 3, Mantenimiento 5, Privacidad 5 → **70/100**.

#### E6. Página about/autor con sameAs

- **Qué es:** `/about` con bio, enlaces (GitHub, etc.), contacto; enlazar desde posts.
- **Ataca:** E-E-A-T 12 y Knowledge graph 13 (los que ningún linter de markdown arregla solo).
- **Puntuación:** Loop 2, Voz 5, Coste 4, Cobertura 4, Evidencia 3, Mantenimiento 5, Privacidad 5 → **76/100**.

#### E7. QA de contenido + agente (loop lint-fix)

- **Qué es:** E3 o geo-lint con salida JSON y una instrucción corta de agente: leer violaciones, editar el `.md` conservando voz, re-ejecutar hasta limpio.
- **Ataca:** el "close feedback loop" completo del usuario.
- **Puntuación:** Loop 5, Voz 4, Coste 3, Cobertura 4, Evidencia 4, Mantenimiento 3, Privacidad 4 → **79/100**.

### Grupo F. Investigación y reescritura automática

#### F1. AutoGEO API / Mini

- **Qué es:** rewriter entrenado/preferencias de GE con benchmark público. Repo MIT; requiere clonar, conda y API keys (GPU para Mini).
- **Riesgo:** adaptación por dominio, coste de API, reescritura que puede matar la voz. Fuera de scope para blog personal diario.
- **Puntuación:** Loop 3, Voz 0, Coste 1, Cobertura 4, Evidencia 5, Mantenimiento 1, Privacidad 1 → **44/100**.

#### F2. MAGEO

- **Qué es:** loop multi-agente con fidelity gate (Findings ACL 2026).
- **Riesgo:** framework de paper, no herramienta de authoring personal.
- **Puntuación:** Loop 2, Voz 1, Coste 0, Cobertura 4, Evidencia 5, Mantenimiento 0, Privacidad 1 → **38/100**.

#### F3. Rewrite asistido manual con LLM del propio agente

- **Qué es:** pedir al agente de coding que añada stats/citas/FAQ a un draft concreto, bajo supervisión.
- **Puntuación:** Loop 4, Voz 3, Coste 4, Cobertura 4, Evidencia 2, Mantenimiento 5, Privacidad 2 → **70/100**.

## Top 5 opciones (revisado)

Orden final: score + dependencias lógicas. No es solo la fórmula cruda.

### 1. JSON-LD en templates + signals del sitio (E1 + E6, score E1 89)

**Ataca lo que geo-score castiga con 15 (schema) y 12/13 (E-E-A-T, KG).**

`post.html` hoy tiene OG y canonical, pero cero `application/ld+json`. El parser ya expone title, description, dates, slug y lang. Organization/Person en home/about usa los mismos campos. O se escribe a mano o se usa un generador existente (`geo schema` o `article_schema`). Cero dependencias propias si se hace a mano.

**Hecho cuando:** cada post emite Article JSON-LD válido; home/about emite Organization/Person con `sameAs`; existe página about enlazada.

### 2. `geo-optimizer-skill` (B2, score 79)

**Sustituye a geo-opt como base de paquete.**

MIT, madurez alta, y `geo llms` / `geo schema` pueden resolver parte de E2/E1 sin reescribirlos desde cero. `geo audit` sirve como spot check de la URL publicada. El bucle de draft markdown sigue siendo más débil que un QA propio, pero el ecosistema es el único maduro del set.

**Hecho cuando:** `pip install geo-optimizer-skill` y al menos uno de `geo schema` o `geo llms` produce output que encaja con el blog (o un audit puntual contrasta el sitio).

### 3. Script propio de QA con el parser (E3, score 88)

**El close feedback loop puro: markdown local a findings en segundos.**

Usa `parse_markdown_file`, mide señales KDD (stats, citas, headings, FAQ, oraciones largas, alt) y sale por consola. Cero deps nuevas. Se puede combinar con E7 (instrucción de agente para arreglar violaciones conservando voz).

**Hecho cuando:** `python scripts/geo_qa.py content/_drafts/foo.md` responde en local antes de `set_slug`.

### 4. Checklist GEO en el flujo editorial (E4, score 85)

**Ancla los hallazgos al estándar editorial que el repo ya tiene.**

No es un score, pero es la capa más barata de adopción: 4-6 items medibles en el checklist pre-publicar. Evita que cualquier linter externo reescriba posts personales.

**Hecho cuando:** AGENTS.md o el flujo `new_post`/`set_slug` incluyen esos items y se usan de verdad.

### 5. Ruta `/llms.txt` generada desde el índice (E2, score 83)

**Discoverability técnica al estilo del sitemap que ya existe.**

robots y sitemap ya puntúan 100 en geo-score. llms.txt es el siguiente paso de AI discovery. Antes de programar la ruta, probar `geo llms` o `generate_llms_txt`; si el output no encaja, ruta manual de ~30 líneas copiando `sitemap()`. RSS/Atom y lastmod (E5) son el complemento natural.

**Hecho cuando:** `https://blog.chrislabs.net/llms.txt` responde y lista posts por idioma con title y description.

### Cercanos al top 5 (no entran ahora)

| Opción | Score | Por qué queda fuera del inmediato |
| --- | --- | --- |
| E7 lint-fix con agente | 79 | Depende de E3 o A1 primero. |
| B1 `ai-visibility` | 79 | Score Python útil y tiene generadores; bus factor y madurez bajas frente a geo-optimizer-skill. |
| A1 `@ijonis/geo-lint` | 78 | Buen paquete de fixes; 92 reglas, ruleset que crece. Candidato tras E1-E4. |
| A4 `llmscout-cli` | 76 | Smoke de URL publicada en modo WARN. |
| E6 about/autor | 76 | Se hace junto a E1 (Organization/Person), no como option independiente. |
| A2 `geo-opt` | 68 | Fuera: licencia no OSI, Node 22, 0 estrellas. Audit suelto como mucho. |
| F3 rewrite con agente | 70 | Útil puntual, no como sistema base. |

## Cuadro resumen (ranking completo, corregido)

| Opción | Score | Rol en el workflow |
| --- | --- | --- |
| E1 JSON-LD + Organization/Person | 89 | Señales del sitio (schema, E-E-A-T, KG) |
| E3 QA propio con parser | 88 | Loop de draft diario |
| E4 Checklist GEO editorial | 85 | Adopción barata sin reescritura |
| E2 `/llms.txt` | 83 | Discoverability AI |
| B2 geo-optimizer-skill | 79 | Paquete maduro + generadores schema/llms |
| E7 lint-fix con agente | 79 | Loop autónomo (tras E3/A1) |
| B1 ai-visibility | 79 | Score Python + generadores, madurez baja |
| A1 geo-lint | 78 | Linter con fixes para agentes |
| A4 llmscout-cli | 76 | Smoke técnico de URL |
| E6 about/autor | 76 | Junto a E1 |
| E5 RSS + lastmod | 70 | Freshness y syndication |
| F3 rewrite asistido | 70 | Puntual en drafts |
| A2 geo-opt | 68 | Descartado como base (licencia/madurez) |
| C1 @dariodario/geochecker | 60 | Spot-check de URL publicada |
| A3 geo-ai-search-optimization | 58 | Evitar por ahora (demasiado) |
| C2 auto-geo doctor | 57 | SOP comercial, pisa la voz |
| C4 geo-score.online | 55 | Baseline, no workflow |
| D1/D2 citation probes | 54 / 51 | Solo con API key y pregunta real |
| C3 geo-audit | 52 | Instalación pesada, madurez baja |
| ~~B3 geo-toolkit~~ | N/A | No existe en npm ni PyPI |
| F1 AutoGEO | 44 | Investigación, no productivo aquí |
| F2 MAGEO | 38 | Framework de paper |
| D3 plataformas self-hosted | 35 | YAGNI |

## Qué omitir a propósito

- Plataformas de monitoring multi-engine (Canonry, GeoLook, zoomer-geo) hasta que el blog tenga tráfico de AI search medible.
- Rewriters académicos (AutoGEO, MAGEO) como paso 1: matan voz y cuestan en APIs.
- Gate de CI que falle PRs personales por "word count < 1000": contradice el spike editorial.
- Copiar el rubric completo de geo-score.online dentro del repo. Nos quedamos con los 4-5 checks que el código puede sostener.
- Dependencias nuevas de scraping para "ver el HTML publicado" cuando el markdown fuente ya está en git.
- Paquetes no instalables o de madurez nula (geo-toolkit y similares) sin URL de registro verificada.

## Recomendación de implementación (orden perezoso, post-evaluación)

1. **Esta semana:** E1+E6 juntos (JSON-LD en `post.html` + Organization/Person + about). Un solo diff ataca schema, E-E-A-T y KG.
2. **E2 con generador si encaja:** probar `geo llms` o `generate_llms_txt` antes de programar la ruta. Si no encaja, endpoint manual copiando `sitemap()`.
3. **E4 checklist ya.** 30 minutos; protege la voz frente a cualquier linter.
4. **E3 después, delgado.** Script de 5-8 señales KDD con umbrales por tipo de post. Sin frameworks.
5. **Paquetes como complemento, no como base:** `geo-optimizer-skill` para spot check / generadores; `@ijonis/geo-lint` solo si se quiere ruleset externo en drafts; `llmscout-cli` como WARN en CI, nunca gate duro.
6. **No en el top 5 inmediato:** citation probes, AutoGEO/MAGEO, geo-opt como base, y plataformas self-hosted. Se reconsideran si "que ChatGPT cite el blog" pasa a ser objetivo medible.

## Estado de implementación (2026-10-01)

Hecho en el repo (sin paquetes nuevos de GEO):

| Qué | Dónde |
| --- | --- |
| JSON-LD WebSite+Organization en todas las páginas | `base.html` + `features/posts/schema.py` |
| JSON-LD Article en posts | `post.html` / `article_schema()` |
| Página `/{lang}/about` + Person schema + sameAs GitHub | `about.html`, `routes.py`, i18n |
| Footer y byline enlazan a about | `base.html`, `post.html` |
| `/llms.txt` desde `get_posts()` (EN/ES/FR) | `routes.py` / `build_llms_txt()` |
| Checklist GEO pre-publicar | `AGENTS.md` |
| QA local de drafts | `scripts/geo_qa.py`, `mise run geo` |
| Tests schema/endpoints/QA | `tests/test_features/test_posts/test_geo.py` |

### Omitido a propósito (no está en el código)

Nada de esto se instaló ni se cableó. Motivos y cuándo retomarlo:

| Opción | Score spike | Por qué se omitió | Cuándo retomar |
| --- | --- | --- | --- |
| `geo-optimizer-skill` (B2) | 79 | E1/E2 cubiertos a mano con el parser existente; un pip extra no era necesario para el loop de drafts | Si quieres `geo audit` de la URL publicada o reutilizar `geo schema`/`geo llms` sin mantener generadores propios |
| `@ijonis/geo-lint` (A1) | 78 | `geo_qa.py` ya da findings locales; ruleset de 92 reglas obliga a curar severidades contra la voz editorial | Si el QA casero se queda corto y quieres fixes JSON para agentes |
| `ai-visibility` (B1) | 79 | Mismo motivo; bus factor 1, madurez baja | Solo si prefieres score Python ya hecho al script propio |
| `llmscout-cli` (A4) | 76 | Smoke de URL viva, no de markdown | CI en modo WARN tras deploy, nunca gate de PRs personales |
| `geo-opt` (A2) | 68 | Licencia Tooltician no OSI, Node 22, 0 estrellas; evaluación Muse lo sacó del top | Audit puntual suelto si un día necesitas citability score comparable |
| `@dariodario/geochecker`, `auto-geo`, `geo-audit` | 60/57/52 | Auditan URL publicada; el loop barato es el draft en git | Spot check periódico del sitio, no el flujo de escritura |
| Citation probes (D1/D2) | 54/51 | Necesitan API keys y preguntas reales a motores | Cuando "que ChatGPT cite el blog" sea objetivo medible con presupuesto |
| RSS/Atom + lastmod fino (E5) | 70 | No ataca citability/schema; freshness ya parcial con `updated` | Si syndication o freshness puntúan bajo en un re-audit |
| E7 lint-fix autónomo con agente | 79 | Depende de un linter con JSON de fixes; hoy el loop es humano + `geo_qa.py` | Cuando quieras loop agent-in-the-loop sobre drafts |
| Rewriters académicos (F1/F2) | 44/38 | Matan voz, cuestan APIs/GPU, fuera de scope de blog personal | Investigación, no productivo |
| Plataformas self-hosted (D3) | 35 | YAGNI: días de setup para un blog-chat | Solo con tráfico de AI search medible |
| Gate de CI por word count / FAQ | N/A | Contradice el spike editorial del repo | No planificado |
| Generador de llms.txt de terceros | N/A | Ruta manual ~30 líneas copiando `sitemap()` con `get_posts()` | Solo si el índice crece y el format hand-rolled duele |

**Decisión de diseño:** cero dependencias nuevas de GEO en `pyproject.toml`/`package.json`. El close loop es markdown local + checklist + endpoints que ya usa el parser. Los paquetes del ranking son complemento opcional, no base.

## Checklist pre-publicar (ampliación GEO del spike editorial)

- [ ] Frontmatter `description` completa y autónoma (no corte a medias)
- [ ] Primera oración de cada H2 lleva el takeaway (front-load)
- [ ] Si se afirma un dato, hay fuente o número concreto
- [ ] Guías/tutoriales: 3-7 preguntas reales como H2 o FAQ final
- [ ] Imágenes con `alt` que nombre entidad + contexto
- [ ] Un enlace externo a referencia estable cuando se introduce concepto no trivial
- [ ] `created`/`updated` correctos (freshness)
- [ ] El post no fuerza FAQ ni 1500 palabras si es diario personal

## Fuentes

- GEO paper (Aggarwal et al., KDD 2024): https://arxiv.org/abs/2311.09735
- ACM DL KDD'24 GEO: https://dl.acm.org/doi/10.1145/3637528.3671900
- AutoGEO (ICLR 2026): https://github.com/cxcscmu/autogeo y paper https://arxiv.org/abs/2510.11438
- MAGEO (Findings ACL 2026): https://github.com/Wu-beining/MAGEO
- @ijonis/geo-lint: https://github.com/IJONIS/geo-lint
- geo-opt: https://github.com/cortega26/geo-opt y https://www.npmjs.com/package/geo-opt
- ai-visibility (PyPI): https://pypi.org/project/ai-visibility/
- geo-optimizer-skill: https://github.com/Auriti-Labs/geo-optimizer-skill
- geo-ai-search-optimization: https://registry.npmjs.org/geo-ai-search-optimization
- LLMScout / llmscout-cli: https://github.com/RudrenduPaul/LLMScout
- @dariodario/geochecker: https://github.com/dariodario-com/geochecker
- auto-geo: https://github.com/shadowresearch/auto-geo
- geo-audit: https://github.com/g-shevchenko/geo-audit
- Canonry: https://github.com/canonry/canonry
- GeoLook: https://github.com/aigclink/geolook
- llms.txt proposal: https://llmstxt.org/
- Evaluación independiente Muse Spark 1.3: docs/spikes/2026-10-01_geo-analisis-feedback-loop_evaluacion-muse.md
- Spike editorial del repo: docs/spikes/2026-09-20_blog-editorial-legibilidad.md
- Baseline geo-score de blog.chrislabs.net (reporte en sesión, 2026-10-01)
- Código del repo: `src/blog_chat/features/posts/parser.py`, `routes.py` (robots/sitemap), `templates/post.html`
