# Proposal

## Why

The author's username history (Kris7Pivot → Xentyo → Ricexen → RiceSeed(x)) exists only as raw audio transcription. Publishing it as a Spanish diary post preserves that identity lineage on the blog and links the already-published K7P shield evidence to the full story.

## What Changes

- New Spanish post telling the nickname history in the author's voice (contenido con islas crudas, not full-transcription crude).
- Canonical chain fixed: Kris7Pivot → Xentyo → Ricexen → RiceSeed(x), with the Xentyo sub-chain Centello → Centeyo → Centyo → Xentyo and the Centello tutorial link.
- Frontmatter complete (`title`, `slug`, `created`/`updated`, `description` ≥40 chars, `lang: es`, `lang_group`, `tags`).
- Editorial + GEO diary rules applied: front-loaded H2s, 1 idea per paragraph, descriptive external link(s), no forced FAQ / no 1500-word padding.
- Draft validated with `mise run geo` (`scripts/geo_qa.py`) before `set_slug.py` publish.

## Capabilities

### New Capabilities

- `blog-post`: authoring and publishing a blog post (frontmatter contract, editorial structure, GEO diary signals, voice preservation).

### Modified Capabilities

None — no existing specs exist in this repo.

## Impact

- Content only: one new file under `content/_drafts/` → `content/es/<slug>.md` via the normal `new_post.py` / `set_slug.py` flow.
- No code changes, no new dependencies, no template/route changes. JSON-LD, `/llms.txt`, sitemap pick the post up automatically via `get_posts()`.
