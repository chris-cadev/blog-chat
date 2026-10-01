# Spike: `:` sin comillas rompió el idioma de un post

| **Fecha:** 2026-10-01                                                              |
| --------------------------------------------------------------------------------- |
| **Tipo:** spike de investigación (sin código)                                     |
| **Pregunta:** ¿por qué `/es/terceros-espacios` mostraba contenido inglés?         |

## Resumen

El archivo ES estaba bien. El EN tenía un `description:` sin comillas con `:` dentro, YAML inválido que el parser silenció a `{}` (post sin `lang`, título = slug). `get_post` lo devolvía para cualquier idioma antes de llegar al ES correcto. Fix: entrecomillar `description` en EN/FR y match exacto de idioma primero en `get_post`.

## Hallazgos

### 1. `:` + espacio es sintaxis YAML, no texto
- `description: Ray Oldenburg's third place: why...` lanza `mapping values are not allowed here` (el `:` separa clave-valor).
- Medido en el repo (250 `.md`): 3 fallos — `content/en/terceros-espacios.md`, `content/fr/terceros-espacios.md`, draft `2026-09-30-rosacea-tratamiento.md` (`title: ...rosácea: doxiciclina...`). Solo el draft queda pendiente (dev-only).

### 2. El parser silencia el error y fabrica un post fantasma (`parser.py:64`)
- `except YAMLError: frontmatter = {}` → `title`/`slug` = stem del archivo, `lang` = `None`, `content` = cuerpo correcto.
- Síntoma visible: `<h1>` = slug (`terceros-espacios`) en vez del título. Si el H1 es el slug, el frontmatter no parseó.

### 3. `get_post` single-pass devolvía el fantasma para cualquier idioma (`services.py:47`)
- El fallback `if not post.get("lang"): return post` retornaba el EN roto al pedir `lang="es"`, según orden de `powerwalk` (order-dependent).
- Auditoría post-fix: 48 slugs publicados, los 48 en `en/es/fr`, 0 duplicados slug+idioma. El único `.md` sin `lang` es `content/blog-chat-idea.md` (legacy, slug `platform/first`, no indexa).

## Principios

1. **Si contiene `:` + espacio, va entrecomillado.** Sin excepciones en `title`/`description`.
2. **El error visible es el H1 = slug.** Diagnóstico en 5 segundos, sin logs.
3. **Match exacto antes que fallback.** Un post sin `lang` nunca debe tapar una traducción existente.

## Reglas de frontmatter

- `title` y `description` siempre con comillas dobles (no contienen `"` en este repo; si la tuvieran, escapar `\"` o usar bloque `>`).
- Continuación multilínea con indentación de 2 espacios, comilla de cierre al final (estilo del ES que sí parseaba).
- `lang ∈ {en,es,fr}` + `slug` + `lang_group` obligatorios en publicados. Traducciones del mismo tema comparten `lang_group`.
- `created`/`updated` formato `YYYY-MM-DD` entrecomillado.

## Verificación en 30 segundos

```bash
python3 -c "
import yaml, re
from pathlib import Path
for f in sorted(Path('content').rglob('*.md')):
    m = re.match(r'^---\n(.*?)\n---\n', f.read_text(encoding='utf-8'), re.DOTALL)
    if m:
        try: yaml.safe_load(m.group(1))
        except yaml.YAMLError as e: print('FAIL:', f, str(e).splitlines()[0])
"
```

Vacío = todo parsea. Cualquier `FAIL` es un post fantasma en producción.

## Checklist pre-publicar

- [ ] `title`/`description` entrecomillados si tienen `:` (o siempre)
- [ ] `lang`, `slug`, `lang_group` presentes; `lang_group` igual en las 3 traducciones
- [ ] Script de arriba sin `FAIL`
- [ ] `/en/`, `/es/`, `/fr/` del slug muestran el H1 correcto (no el slug)

## Qué omitir a propósito

Validación estricta que tire 500 ante YAML roto, linter de frontmatter en CI, y migrar a TOML/JSON. YAGNI: el fallo es raro (3/250), el síntoma es obvio (H1 = slug) y el script lo detecta. Solo si se repite por tercera vez.

## Fuentes

- YAML 1.2 spec, §7.3.3 Plain Style (`:␣` termina el scalar): https://yaml.org/spec/1.2/#style-flows/
- PyYAML `safe_load` — el error `mapping values are not allowed here` es suyo, no del contenido
- `src/blog_chat/features/posts/parser.py:56`, `services.py:47`, `content/es|en|fr/terceros-espacios.md`
