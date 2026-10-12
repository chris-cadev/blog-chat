# Proposal

## Why

Readers have no signal for how long a post takes to read. Listing and article views show date and tags but no duration. Adding a standard reading-time estimate next to the date helps scanning and sets expectations, while caching avoids recomputing on every request.

## What Changes

- Compute reading time from post markdown body (stripped of frontmatter, code fences, images, HTML) as word count / WPM → total seconds, rounded to nearest 5 seconds, displayed as `Xs` (<60s) or `Xm Ys` (e.g., `2m 15s`, `10s`).
- Use a documented standard: **200 WPM** (widely used blog default; alternatives citable: Medium 265 WPM, IReST study 228±30 wpm EN — referenced in design). WPM is a single constant for en/es/fr.
- Show the estimate next to the date in the article header (`post.html`) and in each post card on the index/tags listing (`_posts_page.html`), with accessible label and translated surrounding text for en/es/fr.
- Cache both parse and reading-time results keyed by `(resolved_path, mtime_ns)` so edits to a `.md` file invalidate only that entry; no recomputation when unchanged.
- Include TDD: failing tests for the pure calculation/formatting function before implementation.

## Capabilities

### New Capabilities
- `reading-time`: Standard reading-time calculation, formatting, localization, and display for every blog post with cache-backed parse.

### Modified Capabilities
- (none — no existing spec's requirements change; `content-puzzle` unaffected)

## Impact

- Code: `features/posts/parser.py` (parse + cache), new helper `features/posts/reading_time.py` (pure calc/format), `core/i18n.py` (labels), `features/posts/templates/post.html` + `templates/_posts_page.html` (UI), `features/posts/schema.py` optional `timeRequired` JSON-LD.
- Tests: `tests/test_features/test_posts/test_reading_time.py` (new), extensions to `test_parser.py`/`test_services.py` for cache.
- No DB migration, no API breaking change, no new dependency. Performance: avoids repeat word counting; correctness of word stripping (code fences/images) is the main risk.
