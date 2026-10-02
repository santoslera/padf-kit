---
name: padf-init
description: >
  Install PADF Stage 0 into a new or existing repo via an interview, then a
  copy of the kit, then human GitHub wizards. Use when starting a project under
  PADF, applying PADF to a brownfield repo, or the user says padf-init / export
  PADF / configuration wizard.
---

Do **not** copy another instance's oracles, `feature_list.json` items, or product ADRs. The kit is the PADF package (`PADF_HOME`, default `~/Development/padf`). Skills sequence this ritual; rules stay in verbs and ADR-000.

## 1. Interview (one question at a time; recommended answer each time)

Record answers in `padf/harness/init-answers.json` on the **target** (write the file after the copy if the target has no padf/ yet — keep them in the conversation until apply).

Required:

1. **Mode:** greenfield (empty/new repo) or brownfield (code exists). Brownfield never rearranges their app; `padf/` lands beside it.
2. **Project name** (kebab-ok slug) and **one-line problem**.
3. **Owner** name (R1/R2) and **GitHub handle** (CODEOWNERS) and **repo** `org/name`.
4. **Stack(s):** e.g. python, bun. This fills `harness.yaml` and the suite fallback — you propose the fallback command from what is already in the repo (brownfield) or the stack default (greenfield).
5. **Architecture profile** (ADR-000). Show all three, recommend one, owner picks:
   - **strict** — domain-pure modular monolith. Money, regulated records, multi-module.
   - **modular** — modules with named I/O; no domain-purity theatre yet.
   - **thin** — small tools; file-size + Ask-first deps only. HEAVY paths can still go Strict locally.
   Size is not the axis. A tiny money tool is Strict.
6. **Code philosophy (short):** where logic lives if it differs from the profile; unit tests fake-only or real-ok; anything that must be a Never.
7. **HEAVY zones** (criticality seed) and **kill criteria**.
8. **Agent map:** implementer family vs planner/R4 family — must differ.
9. **CI check names** for branch protection (or `[]` until CI exists).

Stop if a required answer is missing. Do not invent a profile.

## 2. Apply

`PADF_HOME` is `~/.config/padf/home` (written by `install.sh`) or `$HOME/Development/padf`.

```bash
PADF_HOME="${PADF_HOME:-$(cat "$HOME/.config/padf/home" 2>/dev/null || echo "$HOME/Development/padf")}"
python3 "$PADF_HOME/scripts/apply.py" --target /path/to/target --answers /path/to/answers.json
```

Greenfield + existing `target/padf/` → the command fails; that is correct. Brownfield skips existing `docs/charter.md` and ADRs. `--force` overwrites skips.

Confirm `docs/adr/000-architecture.md` matches the chosen profile. Confirm `just utv-validate` / `evidence-check` / `utv-close` recipes exist in the target.

## 3. Prove the verbs

In the target:

```bash
just evidence-check --selftest
python3 padf/harness/scripts/test_evidence_check.py
python3 padf/harness/scripts/test_utv_close.py
```

A gate that cannot go red does not exist. STOP if these fail.

## 4. Human wizards (you do not run these)

Tell the owner:

```bash
bash padf/harness/wizards/github-agent-identity-wizard.sh
bash padf/harness/wizards/github-protection-wizard.sh
```

Identity and branch protection are clicks only they can do. Edit required-check names in the protection wizard if CI jobs differ.

## 5. Stop at the oracle

You may draft properties into `padf/proposals/`. You **never** freeze `padf/oracle/` or write `oracle_sha256`. UTV-001 is the smallest real change under Stage 0, after R2 freezes. Brownfield: first UTV is “put Stage 0 around one existing change,” not a rewrite.

DONE = apply exit 0 + verb selftests red-capable + owner has the two wizard commands + charter/ADR-000 exist + first oracle is waiting on R2.
Anything less: name the blocked step.
