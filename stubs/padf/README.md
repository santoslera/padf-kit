# padf/ — this instance

Process machinery. Product intent stays in `docs/` (charter, ADRs, criticality, phase map).

| Path | Role |
|---|---|
| `harness/` | Contract verbs, FSM, `harness.yaml` |
| `specs/` | Active UTVs. On accept, before merge: `specs/_archive/` |
| `oracle/` | Permanent spec. R2 only |
| `proposals/` | Draft properties |
| `evidence/` | EVIDENCE + REVIEW per attempt |
| `work/feature_list.json` | Queue. `done` via `just utv-close` |
| `explore/` | Spikes. `explore/*` never merges to main |

`just utv-validate` · `just evidence-check` · `just utv-close`

Close-out lands on the accepted UTV PR before merge (PR policy).

## PR policy

- **Issues are the only intake** (`.github/ISSUE_TEMPLATE/`). Agent-filed issues start with `> *Filed by an AI agent.*` and carry an evidence label (CONFIRMED / PLAUSIBLE). Triage moves `needs-triage` → `ready-for-author` / `needs-info` / `wontfix`; `expedite` (production down, data at risk) skips the weekly batch but not the pipeline.
- `ready-for-author` feeds `utv-author`, never an implementer directly.
- **One UTV = one mirror issue (`utv` label) = one worktree = one branch `utv/NNN-slug` = one draft PR**, opened as soon as the worktree exists. Planning, implementation and review all happen there, never on `main`.
- Agents may push `utv/*` and `explore/*`; nobody pushes `main`. `explore/*` never merges (`Branch guard` check).
- The implementer flips the PR to ready when EVIDENCE passes `just evidence-check`; that triggers R4.
- **Close-out lands on the same PR, before merge**: `just utv-close` (archives the spec, marks the queue done, prints `Closes #n`), then merge. No follow-up hygiene PR.
- A bug found outside the UTV's `targets` becomes a new issue, never an inline fix.

## Review protocol

- R4 reviews exactly one attempt, anchored on its PR, with a model family different from the implementer's. It reads the UTV, EVIDENCE, the diff and the ADRs the UTV names — never the plan.
- **L1** CI checks (red = not reviewable) · **L2** re-run every command EVIDENCE quotes, re-hash the frozen oracle, treat I/O rows as binary criteria, check Always/Never · **L3** adversarial sweep (`harness/prompts/review-adversarial-sweep.md`; STANDARD one pass, HEAVY fan out, LIGHT skip).
- Output `evidence/REVIEW-UTV-NNN-attemptN.md` with the reviewed `**Head:**` and one verdict: `GREEN-recommend`, `AMBER` (Request Changes) or `ABSTAIN` (could not verify — treated as AMBER). R4 never Approves as authority.
- **Accept** = checks green, no changes requested, and the latest REVIEW says `GREEN-recommend` at a Head that still covers the PR's code. `just utv-close` enforces it. The owner decides every AMBER: merge (`--owner-override "reason"`, recorded), relaunch, or split.
