---
name: padf-implement
description: >
  Implement exactly one UTV under PADF discipline. Use when assigned a UTV file
  (padf/specs/UTV-NNN-*.md). Deliberately thin: the authoritative role instructions live
  in padf/harness/fsm/ and the assigned UTV — read those, not this summary.
---

PREFLIGHT — verify the assigned `padf/specs/UTV-NNN-*.md` and `padf/harness/fsm/roles/implementer.md` exist. If the UTV is missing, report the missing path and STOP. If the FSM role file is missing, write one line under `## HALT` in the UTV and STOP.

Orchestrator: after a UTV is `ready`, open **one child worktree** of the repo checkout (e.g. `git worktree add ../<repo>-utv-NNN -b utv/NNN-slug`). Push the branch as `utv/NNN-slug` and open a **draft PR** immediately, body linking the UTV (PR policy). PLAN + IMPLEMENT + REVIEW all happen there, in that worktree (never on `main`). Three dispatches, two model families (AGENTS.md Default agent map): the planner model writes `padf/specs/UTV-NNN.plan.md` (`planner.md`); the implementer model implements (`implementer.md`); the planner family reviews per `reviewer.md`, triggered when the PR flips to ready at EVIDENCE (review protocol). On AMBER, PLAN again in the same worktree, then IMPLEMENT attempt N+1. On GREEN (or AMBER + owner chose merge): close-out on **this** PR (`just utv-close`, `Closes` in the body, push, merge) — never a follow-up hygiene PR (PR policy). Do not hand a ready UTV to R3 without a plan unless the UTV HALT says `plan: skip`. Do not implement on `main`.

1. Read, in order: the assigned UTV, `UTV-NNN.plan.md` if present, then `padf/harness/fsm/roles/implementer.md`, then only the ADRs the UTV's targets reference. Nothing else preloaded. If the plan is required and missing, STOP — that is a planner job, not yours.
2. Follow the FSM states as defined in `padf/harness/fsm/` (ANALYZE → PLAN → IMPLEMENT → HARDEN → EVIDENCE). PLAN is the planner role; you start at IMPLEMENT. State transitions happen ONLY via Contract verbs exiting 0 (when those verbs exist).
3. Non-negotiables (mechanisms enforce them; listed so you don't waste turns discovering them): protected paths are read-only to you; any ask_first condition → write one line under `## HALT` in the UTV file and STOP the turn; do only the assigned task; no scope growth; no spawning agents; never wait on an interactive approval prompt — record blocked and stop. The R3 model comes from the AGENTS.md Default agent map; the orchestrator launches you — do not pick your own reviewer or write the plan yourself.
4. Finish = `padf/evidence/EVIDENCE-UTV-NNN.md` written per the format of an existing padf/evidence/ file, with block 6 (WHAT I HAVE NOT TESTED) filled honestly, and `just evidence-check` exiting 0. Completion claims without that exit code are void. Do not archive the spec, do not mark `feature_list.json` done, do not merge — that is close-out after accept (PR policy), run by the orchestrator / `semaphore-triage` on this same PR.
