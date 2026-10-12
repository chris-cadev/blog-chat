# content-puzzle Specification

## Purpose
Generic client-side puzzle gate for article content that hides a block until the reader answers a question, with forgiving input and forever persistence per puzzle identity.

## Requirements

### Requirement: Gated reveal for TL;DR block
The system SHALL hide the TL;DR block for the usernames post until the reader submits the correct answer to the question "what is the username of the NT's crew member that likes a lot Pokemon videogames?".

#### Scenario: TL;DR hidden by default
- **WHEN** a visitor loads any of `content/{en,es,fr}/kris7pivot-xentyo-ricexen-riceseed-historia-usernames.md` without a solved flag
- **THEN** the TL;DR content is not visible and a gate showing the question, input, and unlock button is visible

#### Scenario: Correct answer reveals TL;DR
- **WHEN** the visitor enters a correct answer and activates Unlock (click or Enter)
- **THEN** the gate hides, the TL;DR content becomes visible without page reload, and focus/reading order moves to the revealed content

### Requirement: Text answer matching is forgiving
The system SHALL compare answers case-insensitively, trim surrounding whitespace, and accept comma-separated aliases defined in markup (e.g., `Endaa,Endaa3132,3132`).

#### Scenario: Case-insensitive match
- **WHEN** the visitor types `endaa` (lowercase) and the expected is `Endaa`
- **THEN** the system treats it as correct

#### Scenario: Trim and alias match
- **WHEN** the visitor types ` 3132 ` with spaces and the gate defines `data-expected="Endaa,Endaa3132,3132"`
- **THEN** the system treats it as correct

#### Scenario: Incorrect answer feedback
- **WHEN** the visitor submits a non-matching answer
- **THEN** the system keeps the gate visible, shows an inline error message via `aria-live`, keeps focus in the input, and does not reveal content

### Requirement: Persistence mirrors audio puzzle
The system SHALL persist solved state in `localStorage` per puzzle identity (derived from puzzle element id + normalized expected value) so a returning visitor does not need to re-solve; it SHALL handle unavailable storage without breaking the page.

#### Scenario: Solved state restored on reload
- **WHEN** a visitor solves a puzzle and later reloads the same page (same puzzle id)
- **THEN** the gate is hidden and content is visible immediately on load

#### Scenario: Storage unavailable degrades gracefully
- **WHEN** `localStorage` throws (private mode, quota)
- **THEN** the gate still validates and reveals content for the current session without persisting

### Requirement: Generic multi-instance puzzle gate
The system SHALL support N puzzle gates per page via a single generic client chunk loaded only when `[data-puzzle]` or legacy `#audio-puzzle` markup exists; the legacy audio gate SHALL continue to work via the same chunk.

#### Scenario: Multiple gates coexist
- **WHEN** a page contains two `[data-puzzle]` blocks and one legacy `#audio-puzzle`
- **THEN** each gate validates independently, persists under its own key, and the chunk is loaded only once

#### Scenario: No puzzle markup means no extra JS
- **WHEN** a page contains no `[data-puzzle]` and no `#audio-puzzle`
- **THEN** the generic puzzle chunk is not fetched or executed

### Requirement: HCI — affordance, feedback, and accessibility
The system SHALL follow HCI principles for the gate: visible lock/question affordance, immediate inline feedback, error prevention (Enter to submit, no silent failure), focus management, `aria-live` for messages, keyboard operability, and minimal layout shift.

#### Scenario: Keyboard-only unlock
- **WHEN** a keyboard user focuses the input and presses Enter
- **THEN** the answer is validated and the same reveal/error behavior occurs as with a click

#### Scenario: Screen reader announces result
- **WHEN** the visitor submits an answer (correct or incorrect)
- **THEN** the message area with `aria-live="polite"` announces the result text

#### Scenario: No disruptive layout shift
- **WHEN** the gate transitions to revealed content
- **THEN** content appears in-flow without moving unrelated page elements off-screen and the revealed block receives logical reading order
