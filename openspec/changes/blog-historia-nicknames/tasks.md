# Tasks

## 1. Draft scaffold

- [x] 1.1 Create the draft via `python scripts/new_post.py` with the working title and verify the new file exists under `content/_drafts/`
- [x] 1.2 Fill frontmatter (`title`, `slug`, `created`/`updated`, `description` 40+ chars, `lang: es`, `lang_group`, `tags`) and verify `python scripts/geo_qa.py <draft>` reports no `missing_*` or `short_description` findings

## 2. Body writing

- [x] 2.1 Write the body with front-loaded H2s covering Kris7Pivot → Xentyo → Ricexen → RiceSeed(x) plus the Centello sub-chain, and verify the headings alone retell the chain in order
- [x] 2.2 Add the Centello tutorial link with descriptive text and the `mis-creaciones-2011` K7P link, and verify `geo_qa.py` reports no `no_external_links`
- [x] 2.3 Read the draft aloud for voice (contenido with 2-3 crude islands) and verify no paragraph exceeds 4 sentences and no two wall paragraphs sit together

## 3. QA and publish

- [x] 3.1 Run `mise run geo -- <draft>` and verify zero error-level findings (info-level `no_question_headings` acceptable for a diary post)
- [x] 3.2 Publish via `python scripts/set_slug.py <draft> <slug> es` and verify the post renders at `content/es/<slug>.md` and appears in the ES index
