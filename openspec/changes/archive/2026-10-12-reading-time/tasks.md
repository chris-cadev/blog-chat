# Tasks

## 1. Pure reading-time helper (TDD — tests first)

- [x] 1.1 Create failing tests for `reading_time_for` in `tests/test_features/test_posts/test_reading_time.py` covering: empty/whitespace → 5s, stripping of `![img]`, ``` fences ```, `inline`, `<html>`, `[text](url)`, word counts 29→10s, 392→2m 0s, 621→3m 5s, rounding boundaries 12s→10s/13s→15s/58s→1m 0s, and iso `PT2M15S`; verify `pytest tests/test_features/test_posts/test_reading_time.py` fails
- [x] 1.2 Implement `src/blog_chat/features/posts/reading_time.py` with `WPM=200`, `strip_for_count()`, `reading_time_for(text, wpm=200)` (ceil → half-up round to 5, min 5, split m/s, label `Xs`/`Xm`/`Xm Ys`, `iso_duration`), and `format_aria(m,s,lang)`; verify the tests from 1.1 now pass
- [x] 1.3 Add i18n keys for reading time in `src/blog_chat/core/i18n.py` for en/es/fr (compact label stays `Xm Ys`/`Xs`, aria strings parameterised); verify `pytest tests/test_core/test_i18n.py` still passes and new keys resolve for each lang

## 2. Parse cache and wiring

- [x] 2.1 Add `_PARSE_CACHE` and `clear_cache()` to `features/posts/parser.py`, keyed by `(resolved_path, mtime_ns)`, calling `reading_time_for` on the body and storing `post["reading_time"] = {words, total_seconds, minutes, seconds, label, iso_duration}`; verify existing `tests/test_features/test_posts/test_parser.py` still passes and new cache tests for hit/miss/invalidation after mtime bump pass
- [x] 2.2 Ensure `features/posts/services.py` benefits from cache (no logic change, just reuses `parse_markdown_file`); verify `pytest tests/test_features/test_posts/test_services.py` passes with cache cleared between tests
- [x] 2.3 Optionally expose reading time in `features/posts/schema.py:article_schema` as `timeRequired` (ISO 8601) using `post["reading_time"]["iso_duration"]`; verify unit test for `article_schema` includes `timeRequired` when reading_time present

## 3. UI display next to date

- [x] 3.1 Update `features/posts/templates/post.html` article meta to render `post.reading_time.label` next to `<time>` with `aria-label` from i18n and `timeRequired` already via schema; verify manual check: `/{lang}/{slug}` shows `· 2m 15s` (example) and a11y label in each language
- [x] 3.2 Update `features/posts/templates/_posts_page.html` post cards to render reading time next to card date (both pinned and regular lists); verify `/{lang}/` and `/{lang}/tags/{tag}` list shows times and no layout break at 320px
- [x] 3.3 Add a small integration test or e2e snapshot covering article and listing rendering with reading time present; verify `mise run test` (or `pytest -k reading`) passes

## 4. Verification and polish

- [x] 4.1 Run full suite `mise run test` and verify no regressions; check that `geo_qa` not broken by new content
- [x] 4.2 Manual QA: confirm long-form post vs tiny 29-word post formatting, language switch preserves times, and editing a `.md` file invalidates cache without restart (dev `APP_ENV=development`)
