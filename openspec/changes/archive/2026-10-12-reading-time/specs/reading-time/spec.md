# Spec Delta

## Purpose

Provides a standard, cached reading-time estimate for every blog post so readers can gauge length at a glance in any language.

## ADDED Requirements

### Requirement: Standard reading-time calculation

The system SHALL calculate reading time for each post from its markdown body (after frontmatter) stripped of code fences, inline code, images, HTML tags, and link URLs, by counting words (`\w+`) and dividing by 200 WPM: `total_seconds = ceil(words / 200 * 60)` with a minimum of 5 seconds and splitting into minutes and seconds without additional rounding.

#### Scenario: Short post shows seconds only

- **WHEN** a post has 29 words (stripped) and WPM is 200
- **THEN** total is 9s and the system reports 9s

#### Scenario: Medium post shows minutes and seconds

- **WHEN** a post has 392 words (stripped) at 200 WPM
- **THEN** total is 118s and the system reports 1m 58s

#### Scenario: Stripping excludes non-readable tokens

- **WHEN** body contains `![alt](url)`, ```` ```code``` ````, `` `inline` ``, `<div>`, and `[text](https://example.com)`
- **THEN** those tokens are excluded from word count before calculation

#### Scenario: Empty or whitespace-only body

- **WHEN** stripped body has 0 words
- **THEN** the system reports 5s (minimum) and does not error

### Requirement: Reading time is shown next to date in article and listing

The system SHALL display the reading-time label next to the date in the article header and below the date in each post card on the listing/tags pages for every post, in the current language context, using the format `Xs` when minutes are 0 and `Xm Ys` (or `Xm` when seconds are 0) otherwise.

#### Scenario: Article header shows reading time

- **WHEN** a visitor opens `/{lang}/{slug}`
- **THEN** the article meta line shows the reading time adjacent to the published date with an accessible label

#### Scenario: Listing cards show reading time

- **WHEN** a visitor views `/{lang}/` or `/{lang}/tags/{tag}`
- **THEN** each visible post card shows its reading time below the card date

#### Scenario: Labels are translated for en/es/fr

- **WHEN** language is `en`, `es`, or `fr`
- **THEN** the surrounding label uses the translated strings (e.g., `en: "2m 15s"` / `es: "2 min 15 s"` / `fr: "2 min 15 s"` as defined in `core/i18n`) and the numeric format remains `Xm Ys`/`Xs`

### Requirement: Reading time and parse results are cached with mtime invalidation

The system SHALL cache parsed post data including the computed reading time keyed by `(resolved_file_path, mtime_ns)` so that repeated requests reuse the cached result without re-reading or recomputing, and SHALL invalidate the entry when the file's mtime changes.

#### Scenario: Cache hit avoids recomputation

- **WHEN** two consecutive requests need the same post and the file has not changed
- **THEN** the second request returns reading time from cache without re-parsing or recounting words

#### Scenario: File edit invalidates cache

- **WHEN** a markdown file is edited and its mtime increases
- **THEN** the next request recomputes parsing and reading time and stores the new entry

#### Scenario: Cache is bounded

- **WHEN** more distinct files are cached than the configured limit
- **THEN** the oldest entries may be evicted but correctness is preserved (miss recomputes)

### Requirement: Reading time is exposed for SEO and accessibility

The system SHALL expose reading time in a machine-readable way via JSON-LD `timeRequired` (ISO 8601 duration, e.g., `PT2M15S`) on article pages and SHALL render the visible label with an `aria-label` that describes the duration in the current language.

#### Scenario: Article JSON-LD includes timeRequired

- **WHEN** a visitor loads an article page
- **THEN** the `Article` JSON-LD includes `timeRequired` matching the computed minutes and seconds

#### Scenario: Visible label has accessible name

- **WHEN** a screen reader encounters the reading-time badge
- **THEN** its accessible name conveys the duration (e.g., `aria-label="2 minutes 15 seconds"` in English)
