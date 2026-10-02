---
name: padf-bootstrap
description: >
  Bootstrap or audit the PADF harness in this repo: environment checks, canonical
  layout, harness.yaml, Contract verbs, protections, first oracle, UTV-001 baseline.
  Use when building the Stage 0/1 harness, starting harness work, or auditing an
  existing instance for missing setup.
---

Authoritative source: the PADF kit (`PADF_HOME`) and the instance's `padf/README.md`. **New or empty repo, or first PADF install on brownfield → `padf-init`, not this skill.** This skill **audits** an instance that already has `padf/`. Follow the checklist order strictly; each step gates the next; never mark a step done without its named verification passing.

1. ENVIRONMENT (skip only if this machine was bootstrapped before)
   - `docker info || podman info` → must exit 0. If not, STOP and tell the user what to install. Do not continue degraded.
   - Verify `just`, `git`, and the stack toolchains exist; record versions in `docs/environment.md`.
   - Confirm the agent forge identity is separate from the human's (Contents+Issues+PRs only). If you cannot verify, HALT and ask.
   - Grep agent CLI configs for skip-permissions defaults and plaintext secrets; report findings; fix only with explicit approval.

2. LAYOUT + CONTRACT
   - Create the missing pieces of the canonical layout (this repo: under `padf/`): `padf/specs/` + `_template.md` + `_archive/`, `padf/oracle/`, `padf/proposals/`, `padf/harness/` (harness.yaml, budget.yaml, models.yaml, adapters/, scripts/, fsm/), `padf/work/feature_list.json`, `padf/evidence/`, `padf/explore/README.md`. Root `justfile` points at `padf/harness/scripts/`.
   - Fill `padf/harness/harness.yaml` interactively with the user: stacks, declared signals for the current Stage, fallbacks, protected paths.
   - Implement the stack adapter(s) for the Contract verbs. Seed from the Pre-Commit Gate in `CLAUDE.md` — its pytest/ruff/mypy/bun commands become `verify-suite` / `verify-static`.

3. PROVE THE HARNESS
   - `just bootstrap` → exit 0.
   - `just harness-selftest` → every declared signal provably RED on injected failure (delete a test: suite gate red? touch the oracle hash: gate red?). Paste the selftest output into the conversation. A gate that cannot fail does not exist; if any signal cannot be forced RED, STOP and fix before proceeding.

4. PROTECTIONS
   - Write CODEOWNERS from the roles in AGENTS.md. Branch protection: no bypass, empty bypass list, `explore/*` cannot merge to main, the agent App cannot approve PRs. Verify by attempting a forbidden action and showing the rejection.

5. FIRST ORACLE + BASELINE
   - Help the user write the first oracle for the criticality map's top invariant (`docs/criticality-map.md` — its first Born-HEAVY path). You may DRAFT properties into `padf/proposals/`; the user approves and freezes. You never freeze.
   - `just baseline` → coverage/mutation floors recorded (measured, rounded down, ratchet-only).
   - Guide UTV-001 (smallest real change) through the pipeline; collect the five baseline numbers into `docs/baseline.md`.

DONE = `just harness-selftest` all-RED-capable + UTV-001 merged + baseline recorded.
Anything less: report exactly which step is blocked and why.
