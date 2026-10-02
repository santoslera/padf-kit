# PADF — portable Stage 0 kit

Install this on any machine, then apply PADF to a **new** or **existing** repo.

This directory is the pack. Every repo it is applied to becomes an *instance* with its own charter, oracles and queue.

## The workflow in one page

**Premise.** Agents generate; humans own what "correct" and "worth building" mean. Rules live in mechanisms (verbs with exit codes, CI, branch protection), not in prompts. A gate that cannot go red does not exist.

**Roles.** R1/R2 human owner: charter (intent) and frozen oracles (permanent spec). R3 implementer agent. Planner + R4 reviewer: a *different* model family from R3. R5 the harness itself.

**Artifacts.**

| Artifact | What it is |
|---|---|
| `docs/charter.md` | Problem, single value metric, kill criteria. Every UTV traces here. |
| `docs/criticality-map.md` | Which paths are born HEAVY. Ceremony follows irreversibility, not repo size. |
| UTV (`padf/specs/UTV-NNN-*.md`) | Disposable spec, about a week of work: rules, a literal-values I/O matrix, ≤3 open questions, Always / Ask first / Never, oracle properties, review contract. |
| Oracle (`padf/oracle/`) | Permanent spec. Only the owner freezes it, with a recorded sha256. Agents draft in `padf/proposals/`. |
| EVIDENCE | Per attempt: commands with exit codes, what changed, what would falsify it, **WHAT I HAVE NOT TESTED**, open HALTs. |
| REVIEW | R4's verdict at a recorded commit: GREEN-recommend / AMBER / ABSTAIN. |

**Loop.**

1. **Intake:** GitHub issues only.
2. **Author** (`utv-author`): confront the frame, run Example Mapping as devil's advocate, attack the draft oracle (EDFH pass), then `just utv-validate`. The owner freezes.
3. **Plan → implement → review**, in one worktree and one draft PR per UTV:
   - The implementer stops with one line under `## HALT` whenever it hits an Ask-first item.
   - It finishes with EVIDENCE plus `just evidence-check`.
   - The reviewer re-runs everything and never Approves as authority.
4. **Triage** (`semaphore-triage`, daily, ~20 minutes of owner attention):
   - GREEN → close-out on the same PR (`just utv-close`), then merge.
   - AMBER → the owner chooses merge / relaunch / split.
   - RED → touch nothing.
5. **Exploration:** `explore/*` branches allow vibe-coding but never merge. Survivors are re-specified as UTVs.

Details: `stubs/padf/README.md` (PR policy, review protocol), the five skills in `.claude/skills/`, and the role files in `stubs/padf/harness/fsm/roles/`.

## Install on another computer

```bash
git clone <this-repo-url> ~/Development/padf
cd ~/Development/padf
./install.sh
```

`install.sh` records `PADF_HOME` in `~/.config/padf/home` and copies the `padf-*` skills into `~/.claude/skills` and `~/.grok/skills`. Clone elsewhere? Set `PADF_HOME` or re-run `install.sh` from that path.

Needs: `python3`, `just`, `git`, `gh` (for the GitHub wizards).

## Use

In an agent session: **padf-init**. It interviews (architecture profile is required: `strict` / `modular` / `thin`), then copies the kit.

Or by hand:

```bash
# edit examples/answers.thin.json first
python3 ~/Development/padf/scripts/apply.py \
  --target /path/to/your/project \
  --answers ~/Development/padf/examples/answers.thin.json
```

Then, **in the target repo**:

```bash
just evidence-check --selftest
bash padf/harness/wizards/github-agent-identity-wizard.sh
bash padf/harness/wizards/github-protection-wizard.sh
```

You freeze the first oracle. Agents do not.

## What this is not

- Not any instance's product ADRs, oracles, or queue
- Not `verify-oracle` / `verify-suite` (those verbs do not exist yet — `fallbacks.suite` is yours)
- Not a prompt that *is* the methodology. Skills call the verbs; ADR-000 holds architecture

See `INVENTORY.md`.

## License

Proprietary, shared privately — see `LICENSE`. Do not redistribute or publish.
