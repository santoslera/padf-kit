# ADR-000: Architecture profile

**Status:** accepted
**Date:** {{updated}}
**Profile:** {{profile}}

---

## Context

PADF requires an architecture decision on Day 1, override by ADR, never by drift. A DDD / Cosmic Python layout is one possible profile, not the kit. This project's profile was chosen in `padf-init`.

## Decision

{{profile_body}}

## Consequences

- `verify-arch` (when it exists) enforces only the contracts this profile turns on.
- HEAVY paths on the criticality map may tighten locally; they do not silently rewrite this ADR.
- Changing profile is a new ADR, not an agent edit.

## Implementation files

- `padf/harness/init-answers.json` — interview record
- `AGENTS.md` — agent-facing restatement
- `padf/harness/harness.yaml` — stage and stacks
