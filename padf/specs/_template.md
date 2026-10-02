---
id: UTV-NNN
slug: short-kebab-name
title: One-line outcome
status: draft
level: LIGHT | STANDARD | HEAVY
intent_trace: docs/charter.md § …
oracle: none | path/to/file
oracle_sha256: ""
migration: none   # or the next free number — any value but `none` auto-promotes to HEAVY (tested rollback, human-read)
deps: none        # new dependencies must be declared here AND appear under ## Ask first
issue: null       # GitHub mirror issue number (PR policy), filled when created
budget:
  attempts: 3
  notes: ""
targets: []
---

# UTV-NNN — <title>

## Intent

What user-visible outcome changes, and how it traces to the charter. One short paragraph.

## Challenges

<!-- Authoring confrontation record (utv-author). Every challenge the devil's advocate raised
     against the FRAME (scope, goal, assumptions), with its disposition:
     accepted → which rule/section changed · rejected → one-line reason.
     "None surfaced" on a HEAVY UTV is a smell — say it out loud. -->

- …

## HALT

<!-- Implementer writes one line here and stops. Owner answers in this file, not in chat. -->

## Rules (blue)

- …

## I/O matrix (green — literal values only)

| Given | When | Then |
|---|---|---|
| | | |

## Open questions (red)

<!-- At most 3. Unanswered at timebox = not ready. Do not fill these as the author. -->

1.

## Always

- …
- <!-- auth/data-touching UTVs: name the negative surface — the endpoints/roles this UTV does NOT change, asserted unchanged by a regression row -->

## Ask first

- …

## Never

- <!-- at least one forbidden APPROACH, not just out-of-scope -->

## Oracle

Kind + at least three independent properties (drafts go in `padf/proposals/`; R2 freezes into `padf/oracle/`).
Run the EDFH pass (`padf/harness/prompts/edfh-pass.md`) against the draft before freeze.

1.
2.
3.

Adapter witness: <!-- HEAVY: for each property, name at least one integration-level witness
(real DB, migration-built schema) — fake-only properties are how silent production no-ops merge. -->

Hidden-split nominees: …

## Review contract

<!-- What R4 must independently re-run for this UTV (review protocol), beyond the standard layers:
     the exact commands, the I/O rows that must be reproduced (not trusted), the ADRs to
     re-verify against the diff, and the journeys most likely to hide an unconsidered path. -->

- Re-run: …
- ADRs to re-verify: …
- Journey hunting grounds: …

## Verification

<!-- Contract verbs that exist: utv-validate, evidence-check. verify-oracle / verify-suite: quote AGENTS.md pre-commit commands until those verbs exist. -->

```bash
just utv-validate padf/specs/UTV-NNN-*.md
just evidence-check padf/evidence/EVIDENCE-UTV-NNN.md
```
