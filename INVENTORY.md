# Kit inventory — generic vs instance

Copy **generic**. Never copy **instance**.

| Path | Kind |
|---|---|
| `padf/harness/scripts/utv_validate.py` | generic |
| `padf/harness/scripts/evidence_check.py` | generic |
| `padf/harness/scripts/utv_close.py` | generic |
| `padf/specs/_template.md` | generic |
| `padf/harness/prompts/edfh-pass.md` | generic |
| `padf/harness/prompts/review-adversarial-sweep.md` | generic |
| `padf/harness/wizards/*.sh` | generic (repo/CI names patched at apply) |
| `.github/ISSUE_TEMPLATE/*` | generic |
| `.github/pull_request_template.md` | generic |
| `.github/workflows/branch-guard.yml` | generic |
| `.claude/skills/padf-{init,bootstrap,implement}` | generic ritual |
| `.claude/skills/utv-author` | generic ritual |
| `.claude/skills/semaphore-triage` | generic ritual |
| `stubs/**` | generic (placeholders) |
| `profiles/{strict,modular,thin}.md` | generic |
| `padf/harness/harness.yaml` | **instance** (name, stacks, tracker.repo, fallbacks) — kit has a stub |
| `padf/work/feature_list.json` | **instance** queue |
| `padf/oracle/UTV-*.md` | **instance** |
| `padf/evidence/**` | **instance** |
| `padf/specs/UTV-*.md` + `_archive/` | **instance** |
| `padf/explore/EXPLORE-*` | **instance** |
| `docs/charter.md` | **instance** |
| `docs/adr/001-*.md` … product ADRs | **instance** (ADR-000 is kit) |
| `docs/plans/notes/STATE.md` | **instance** |
| `AGENTS.md` architecture / commands | **instance** (kit writes a stub from profile) |
| `.github/CODEOWNERS` | **instance** handle (kit stubs `{{github_handle}}`) |
