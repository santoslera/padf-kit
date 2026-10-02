# AGENTS.md — {{project}}

This repo runs under **PADF**. Rules live in mechanisms (gates, hooks, CI); this file points at them.

## Read first, in order

1. `docs/charter.md` · `docs/criticality-map.md` · `docs/phase-map.md`
2. `docs/adr/000-architecture.md` — profile **{{profile}}**
3. `padf/README.md` — instance layout and lifecycle

## Architecture (ADR-000)

{{profile_body}}

Agent-audience, always: files ≤ 300 lines; strict types; no `# noqa` / `# type: ignore` / new skips to get green; comments are context anchors.

## Commands

Suite fallback until `just verify-suite` exists:

```
{{suite_fallback}}
```

PADF verbs: `just utv-validate` · `just evidence-check` · `just utv-close`

## Ways of working

- Test-first. Fail visibly. No spec drift: if implementation needs a design change, STOP and propose.
- Migrations append-only. No new dependencies without UTV `Ask first`.
- Agents may push `utv/*` and `explore/*`. Never push `main`.
- Adjacent bug outside `targets` → GitHub Issue, never inline.
- Finish = EVIDENCE + `just evidence-check` exit 0. Close-out (`just utv-close`) is on the accepted PR before merge.

## Default agent map

Implementer (R3) = **{{implementer_model}}**. Planner + R4 = **{{planner_model}}**. Do not use the same model family as both planner/R4 and R3 on one attempt. Do not plan, implement, or review a UTV on `main`.

## PADF

- Intent: `docs/charter.md`. Permanent spec: `padf/oracle/**` (R2 only). Disposable specs: `padf/specs/*.md`.
- VERIFIED vs EXPLORATION (`explore/*` never merges to main).
- Roles: R1/R2 human ({{owner}}) · R3 agents · R4 gates + human on AMBER · R5 harness.
- Non-negotiables: never edit `padf/oracle/**`; `ask_first` → one line under `## HALT` and stop.

## Most important rule

The oracle and the charter are human-owned. Agents generate and propose; they do not redefine "correct" or "worth building."
