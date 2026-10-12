# Design

## Context

See `proposal.md` for motivation. Current state: `features/posts/parser.py:58` `parse_markdown_file()` returns `{title,slug,tags,created,updated,description,lang,lang_group,content}` with no duration; `features/posts/services.py:24` re-walks `content/` via `powerwalk` and re-parses every `.md` on each request. `core/filters.py:265` `plain_excerpt` shows how to strip markdown/HTML for word counting. Templates `posts/templates/post.html:52` and `templates/_posts_page.html:5` render date but no time; `core/i18n.py:10` has en/es/fr tables with no time strings.

Constraints: keep the diff minimal (ponytail), single WPM constant, no new dependency, no DB migration, no API break, and respect that `content/` mtime changes in dev but is frozen in Docker image.

## Goals / Non-Goals

**Goals:**
- Pure function `reading_time_for(text) -> {words, total_seconds, minutes, seconds, label, iso_duration}` with half-up rounding to 5s and min 5s.
- Cache parse + reading time keyed by `(resolved_path, mtime_ns)` so unchanged files are not re-read/recounted.
- Show `Xs` / `Xm` / `Xm Ys` next to date in both article header and listing cards, translated for en/es/fr, with `aria-label` and `timeRequired` JSON-LD.
- TDD: tests for the pure function before implementation.

**Non-Goals:**
- Per-language WPM tuning, image-adjusted time, per-user preferences, client-side JS calculation.
- Caching the whole `get_posts()` result set or adding a watcher/Redis — deferred unless walk proves slow (p95 >50ms).
- Changing sort order, pagination, or existing spec `content-puzzle`.

## Decisions

**1. WPM = 200, cited against standards**
- Chose 200 as single constant. Rationale: most-cited blog default (Hugo/DEV), conservative for technical prose; citable anchors are Medium 265 WPM (`help.medium.com/hc/en-us/articles/214991667-Read-time`) and Wikipedia/IReST 228±30 EN, 184±29 multilingual. 200 is not over-optimistic and is one-line to change to 265 if desired.
- Alternative: 265 (Medium explicit) — faster estimates, would understate time for this audience. Rejected for now, but document the alternative.

**2. Word counting via stripping like `plain_excerpt`**
- Strip ` ```fences``` `, `` `inline` ``, `![img](url)`, `<tags>`, and `[text](url)->text` before `re.findall(r"\w+", cleaned)`. Rationale: reuses proven logic, avoids counting code as prose, matches excerpt philosophy.
- Alternative: `markdown` render then HTML text extraction — heavier, still counts code content. Rejected.

**3. Rounding: half-up to 5s, carry into minutes**
- `total = ceil(words / WPM * 60)` → `rounded = max(5, ((total + 2) // 5) * 5)` (half-up, integer). Then `m, s = divmod(rounded, 60)`. Format: `s==0 and m==0 -> "5s"`, `m==0 -> f"{s}s"`, `s==0 -> f"{m}m"`, else `f"{m}m {s}s"`. Rationale: matches "1m 20s better, rounding to 5" — simple deterministic display.
- Alternative: nearest 10s or showing decimals — rejected per request.

**4. Module placement**
- New `features/posts/reading_time.py` with pure `reading_time_for(text, wpm=200)` and `format_label(m,s,lang)` plus `iso_duration`. Called from `parser.py` so `parse_markdown_file()` returns `reading_time` alongside `content`. Rationale: single responsibility, testable in isolation; parser stays thin.
- Alternative: do it all in `parser.py` or as a Jinja filter — parser is the natural cache site, filter would still need data; new module is minimal and discoverable.

**5. Cache: module dict `_PARSE_CACHE: dict[Path, (mtime_ns, dict)]`**
- On `parse_markdown_file(path)`: `stat = path.stat(); key=(resolved, stat.st_mtime_ns)`; hit → return copy; miss → read, parse, call `reading_time_for(body)`, store. Add `clear_cache()` for tests (like `core/static.py:35`). Bounded to ~256 entries via simple `if len>256: pop oldest` or `functools.lru_cache`.
- Rationale: avoids file IO + YAML + regex when unchanged; invalidation is exactly file edit; no background thread. Powerwalk still walks dir — acceptable until measured slow.
- Alternative: `lru_cache` on `get_posts(lang)` — caches walk but complicates lang filtering and mtime. Defer.

**6. i18n + a11y**
- Add keys `reading_time` composite or `reading_time_min`/`reading_time_sec` + `reading_time_aria` with parameterised strings per language. Template uses `t('reading_time')` style or direct formatted label with `aria-label`.
- JSON-LD: `features/posts/schema.py:52` `article_schema()` adds `timeRequired` as `PT#M#S`.

## Risks / Trade-offs

- Strip failure inflates count (code fences not matched) → Mitigation: unit tests for fences/images/links; reuse `plain_excerpt` regex suite.
- Half-up rounding shows "1m 0s" for 58s (carry) — may surprise → Mitigation: documented behaviour, tested boundary; acceptable per spec.
- Cache grows without bound if many drafts → Mitigation: cap at 256, oldest eviction correctness preserved.
- File replaced with same mtime (rare, sub-second editors) → miss doesn't fire → Mitigation: also check `stat.st_size` or file hash on miss doubt; not needed for this blog (mtime_ns granularity suffices).
- Translators may want different spacing (`2 min` vs `2m`) → Mitigation: keep numeric `Xm Ys` stable, translate only aria/label prefix.

## Migration Plan

- Deploy backward compatible: new field `post["reading_time"]` optional in templates (`{{ post.reading_time.label if post.reading_time }}`) so rollback just hides badge.
- No migration steps; cache is in-memory and cold-starts empty.
- Rollback: revert templates + keep helper unused, or clear cache.

## Open Questions

- Final copy for es/fr compact label: is `2m 15s` acceptable or should it be `2 min 15 s`? Defer to review of `core/i18n.py` during implementation — does not change spec's requirement to translate.
