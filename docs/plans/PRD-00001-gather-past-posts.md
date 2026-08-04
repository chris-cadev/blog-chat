# PRD-00001: Gather Posts from Past Blog Attempts

**Status:** Draft
**Scope:** Intention / Vision + migration mechanics (resolved in this PRD)

---

## 1. Product Overview

**Product Name:** blog-chat

**Intention (from repository metadata):**
> The idea is to connect website of logs with a live chat in a single page. This to generate interaction between people and content.

This PRD captures the intention to **gather the blog posts written across past attempts at creating a blog** and bring them into blog-chat as seed content. The goal is to rescue already-written material, preserve it, and feed it into the blog + live chat interaction model the product is built around.

## 2. Problem Statement

- Past blog content is scattered across abandoned or separate projects/sites.
- Posts that took effort to write risk being lost or forgotten.
- blog-chat needs seed content to demonstrate and exercise its core loop (read a post, discuss it live) — empty content makes the product hard to evaluate.

## 3. Intention of Relevant Docs in This Repo

| Doc                            | Intention                                                                                     | Relevance to this PRD                                                                |
| ------------------------------ | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `docs/PRD.md`                  | Product specification: blog layer + chat layer, voting, threading, roles, persistent history. | Gathered posts become the blog-layer topics that anchor live chat.                   |
| `docs/design.md`               | HCI philosophy: anchored, evolving knowledge discussions with low cognitive load.             | Past posts are natural anchors; their content stays the fixed knowledge layer.       |
| `docs/architecture.md`         | Feature-based architecture (accounts / chat / posts, planned voting).                         | Posts come from the `content/` directory; gathered posts plug into `features/posts`. |
| `docs/todos.md`                | Prioritized roadmap aligned to the PRD.                                                       | Content-related tasks (e.g., Content File System Router) depend on having content.   |
| `docs/setup.md`                | How to run the project locally.                                                               | No changes expected; gathered posts are data, not setup.                             |
| `docs/library/blog-writter.md` | LLM prompt template for writing new blog posts.                                               | Suggests a future pipeline for normalizing/adapting past posts.                      |
| `docs/library/humanizer.md`    | LLM prompt template for making text sound human.                                              | Future quality pass on imported posts if needed.                                     |

## 4. Past Blog Attempts (Inventory via `gh`)

Identified while researching this PRD:

- **chris-cadev/blog** (private, "debugchris blog")
  - Hugo-based, Obsidian-powered, trilingual (en/es/fr), deployed on Vercel.
  - ~45 logs, ~20 posts, ~2 drafts (`content/pre/`).
  - Last pushed 2026-01-06; considered a past attempt no longer actively maintained here.

> **Excluded:** `chris-cadev/knowledge` (Quartz/Hugo digital garden) was evaluated and dropped — those files are reference notes with no solid purpose, not suitable as seed blog content.

## 5. Vision

A future state where past posts live in blog-chat's `content/` directory as standard markdown posts, each capable of hosting a live chat room — without rewriting or losing the original material. Old content becomes the seed library that demonstrates the product and starts the community conversation.

## 6. Target Location

- **Target:** `content/` in this repository (existing markdown post location consumed by `features/posts`).
- **Scope of sources:** `chris-cadev/blog` is in scope. Other sites (`aloaloart/www`, `taponit-now/www`) are out of scope unless explicitly added.

## 7. Migration Mechanics

How gathered posts are moved from past repos into blog-chat's `content/`, with concrete decisions resolving the format gaps:

### 7.1 File Copy / Placement

- **From `chris-cadev/blog`:** copy `content/logs/*.md`, `content/posts/**/*.md`, and `content/pre/*.md` into `content/` as flat files (keep source subfolder only as a comment prefix if needed).
- Do not modify the source repo; this is a copy operation only.

### 7.2 Front-Matter Conversion

Map Hugo front matter to blog-chat's parser fields (`parser.py` reads `title`, `slug`, `tags`, `created`, `updated`, `description`):

| Source field | Target field | Rule |
| --- | --- | --- |
| `title` | `title` | Pass through |
| `tags` | `tags` | Pass through |
| `date` | `created` | Pass through (YAML date → blog-chat date format) |
| `updated` | `updated` | Pass through if present, else `created` |
| `more` / `draft` / `hour` | (dropped) | Not needed by blog-chat parser |
| `translated-from` | (dropped) | Language handled separately (see 7.3) |
| (none) | `slug` | Derive from filename stem; add `slug` explicitly to avoid collisions |

### 7.3 Multilingual Handling (blog repo)

- Each trilingual post (`.en.md`, `.es.md`, `.fr.md`) becomes **one blog-chat post per language** with a language-suffixed slug (`<stem>-en`, `<stem>-es`, `<stem>-fr`).
- Migrated files are organized into per-language subdirectories: `content/en/`, `content/es/`, `content/fr/` (undetermined-language drafts go to `content/mixed/`).
- Add a `lang` field in front matter (`en`/`es`/`fr`) and a shared `lang_group` value so future UI can group translations.
- Default blog-chat shows all posts; no automatic language routing in this PRD.

### 7.4 Shortcode Resolution (blog repo)

Replace Hugo shortcodes in bodies with plain markdown/HTML:

- `{{< meaning word="X" >}}` → inline **X** or a small definition line.
- `{{< yt-video ID="..." >}}` → embed iframe or linked thumbnail.
- `{{< external-url URL="..." >}}` → markdown link.
- `{{< frame ... >}}` → inline image or iframe as appropriate.
- Any unknown shortcode → best-effort plain text, flag for manual review.

### 7.5 Verification

- Run `pdm test` to confirm existing parser tests still pass.
- Manually visit each migrated post route and confirm the post renders and chat room loads.
- Run a scripted parse of every migrated file with `parse_markdown_file` to confirm front matter parses and no shortcodes remain.

## 8. Success Criteria

- All in-scope posts are accessible in blog-chat's `content/`.
- Original content is preserved (not destroyed or rewritten in transit).
- Imported posts render as topics with live chat attached.
- No unresolved shortcodes remain (flagged ones resolved or documented).
- `pdm test` passes after migration.

## 9. Risks / Open Questions

| Risk / Question | Decision / Notes |
| --- | --- |
| Bilingual/trilingual source material | Each language becomes its own post with `lang` + `lang_group`; no auto-routing in this PRD. |
| Format mismatch (front matter) | Resolved via mapping in 7.2. |
| Shortcodes | Resolved via 7.4; unknown constructs flagged for manual review. |
| Drafts (`content/pre/`) | Included, with empty-front-matter drafts flagged for review. |
| Scope of sources | `blog` only; other sites out of scope. |
| Content ownership/quality | Unfinished drafts preserved as-is; no rewriting in this PRD. |

## 10. Next Steps

- Execute the migration mechanics in 7.1–7.5.
- Follow-up PRDs may add translation grouping UI, draft filtering, and routing.

## 11. Implementation Status

- [x] Migration script: `scripts/migrate_posts.py` (front-matter conversion, language-suffixed slugs, shortcode + cross-link + image resolution).
- [x] Images copied to `src/assets/posts/`; `vite.config.js` publishes them under `/static/posts/`.
- [x] Migrated posts committed to `content/` (68 posts from `chris-cadev/blog`), organized into `content/en/`, `content/es/`, `content/fr/`, `content/mixed/`.
- [x] Language-prefixed routes: `/en/`, `/es/`, `/fr/` indexes and `/en/<slug>` post pages; header language switcher links to the same post in other languages.
- [x] Verified: all files parse with `parse_markdown_file`, no shortcodes/relative images remain, `pdm test` passes.
- [ ] Translation grouping UI (future PRD).
