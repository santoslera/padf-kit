---
name: semaphore-triage
description: >
  Run the daily PADF triage: intake prep, semaphore per UTV, GREEN/AMBER/RED actions,
  HALT answers, archive hygiene. Use when the user says triage, daily review, check the
  queue, or equivalent. Keep the user's total attention under ~20 minutes.
---

PREFLIGHT — verify `padf/work/feature_list.json` exists; if not, STOP and offer `padf-bootstrap`. If `just semaphore` is not a recipe (`just --list`), do NOT stop: run degraded mode — build the per-UTV picture from `feature_list.json`, `padf/evidence/`, PR checks (`gh pr checks`), and the `harness.yaml` fallback suite, and say once that the semaphore verb is still missing (Stage 0).

0. INTAKE PREP (PR policy, tier 1). `gh issue list --label needs-triage` (plus unlabeled issues). For each unprepped issue, dispatch a prep agent in parallel: reproduce the claim, run the redundancy check (already implemented?), check prior rejections, then post ONE comment — AI disclaimer line, evidence label (CONFIRMED/PLAUSIBLE/insufficient), recommended disposition. **Never apply state transitions yourself** — present the prepared issues in the table and apply only the labels the user decides (`ready-for-author` / `needs-info` / `wontfix`). Anything that smells production-down: surface it FIRST and propose `expedite` (immediate UTV, still through the pipeline).
1. Read `padf/work/feature_list.json` (+ `just semaphore --all` when it exists). Present ONE compact table: UTV · state · semaphore/PR checks · failing signals · cost so far · attempts — then the prepared intake issues.
2. Apply the rules mechanically:
   - GREEN (checks green + no changes requested + the latest `REVIEW-UTV-NNN-attemptN.md` says `## VERDICT: GREEN-recommend` with **Head** = the PR's current code) → **close-out on that PR, then merge**. No REVIEW is not GREEN: dispatch R4. Product commits after **Head** are not GREEN: re-dispatch R4 on the new head. Do NOT open or summarize the product diff. Do NOT open a second PR.
   - AMBER (R4 Requested Changes or `## VERDICT: ABSTAIN`, or signal 5/6/7 red; for ABSTAIN show what R4 could not verify) → present ONLY the EVIDENCE.md (highlight blocks 5–7, especially block 6) and the REVIEW verdict + blocking findings, plus whether mutation was below the mutant-count floor (then it is informational — say so). Ask the user for one of: merge / relaunch / split. If merge: same close-out with `--owner-override "<the owner's one-line reason>"`, then merge. Relaunch/split: no close-out.
   - RED → touch nothing. Tag spec-suspect if attempts are exhausted; queue for Monday.

   **Close-out** (PR policy; orchestrator / this skill, never R3/R4), on the UTV worktree:
   1. `just utv-close padf/specs/UTV-NNN-*.md` exit 0. Commit only what it changed (`padf/specs/`, `padf/work/feature_list.json`). It refuses — changing nothing — when the review is missing, not GREEN-recommend without an owner override, or stale (non-close-out files changed since **Head**). Stale → re-dispatch R4; never edit the REVIEW's Head yourself.
   2. Ensure the PR body contains every `Closes #n` the verb printed (`gh pr edit` if missing). Adjacent-bug issues filed during the UTV stay open unless they were in the consumed set.
   3. Push the same `utv/NNN-*` branch. If CI retriggers, wait for green. Do not re-dispatch R4 for process-only close-out.
   4. Merge this PR (`gh pr merge --squash`, or the owner merges). Never push `main`.
3. HALTs: list every open `## HALT` line across `padf/specs/`. Collect the user's one-line answers and write them INTO the UTV files (never leave answers in chat), then re-queue those UTVs.
4. Housekeeping: flag any in-progress UTV with no live agent (orphan → requeue per plan), any UTV over 80% of budget, any review_loop_iteration > 2 (the spec is wrong — say it plainly), any draft PR older than its UTV budget. **Throttle:** if two or more UTVs are AMBER awaiting owner decision, or `just --list` still lacks `verify-oracle` / `verify-suite`, do not launch additional implementers this triage. Finish in-flight work or the missing verbs first — do not add generation when verification is the bottleneck.
5. Close with one line: N merged, N awaiting decision, N halted, N issues prepped/routed, spend today vs ceiling. If Friday: also run the report generator and read back the value line (deployed? used? broke anything?) — the weekly report carries the charter's kill numbers.

DONE = the close line printed and every decision the user made executed (merges done, HALT answers written into the files, labels applied, feature_list.json updated).
