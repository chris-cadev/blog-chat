# Spec Delta

## Purpose

Publishing a personal diary post on this blog means a markdown file with a complete frontmatter contract, scannable editorial structure, GEO diary signals, and the author's voice preserved.

## ADDED Requirements

### Requirement: Frontmatter contract for the nicknames post
The post SHALL ship with `title`, `slug`, `created`/`updated`, `description` of 40+ chars, `lang: es`, `lang_group`, and `tags`, and SHALL parse via `parse_markdown_file` with no missing-field findings.

#### Scenario: Draft passes frontmatter checks
- **WHEN** `scripts/geo_qa.py` runs on the draft
- **THEN** no `missing_title`, `missing_description`, `short_description`, or `empty_body` findings are reported

#### Scenario: Post publishes to the Spanish index
- **WHEN** the file is moved to `content/es/<slug>.md` via `set_slug.py`
- **THEN** it appears in the ES listing with its title and description

### Requirement: Canonical nickname chain is told completely
The body SHALL present the chain Kris7Pivot → Xentyo → Ricexen → RiceSeed(x), the Xentyo sub-chain Centello → Centeyo → Centyo → Xentyo, the Centello tutorial link, the Rosarito robbery as the practical reason for losing Xentyo, and the `x`-as-vestige closing thesis.

#### Scenario: Reader follows the lineage
- **WHEN** a reader scans only the H2 headings
- **THEN** the four nicknames and the vestige idea are visible in order

#### Scenario: K7P evidence is linked
- **WHEN** the post mentions Kris7Pivot
- **THEN** it links the existing `mis-creaciones-2011` K7P shield as proof

### Requirement: Editorial structure stays scannable
Each H2's first sentence SHALL carry its takeaway, paragraphs SHALL hold one idea in 2-4 sentences, and headings SHALL be sentence-case without skipping levels.

#### Scenario: Skim test
- **WHEN** a reader reads only first sentences of each section
- **THEN** the full story (origin, each rename, loss, thesis) is still understood

### Requirement: GEO diary signals without marketese
The post SHALL include a descriptive-text external link for the Centello effect, SHALL NOT force an FAQ or 1500-word padding, and SHALL keep `created`/`updated` accurate.

#### Scenario: QA accepts diary shape
- **WHEN** `scripts/geo_qa.py` runs on the draft
- **THEN** `no_external_links` is absent and `no_question_headings` at info level is acceptable for a diary post

### Requirement: Voice is contenido with crude islands
The prose SHALL read as cleaned-up narrative keeping 2-3 verbatim-flavored anchors from the audio (e.g. "mis dos manitas", "investigación mamalona"), with filler repetitions cut.

#### Scenario: Author voice check
- **WHEN** the author reads the draft aloud
- **THEN** it sounds like their published posts with recognizable oral anchors, not a raw transcript
