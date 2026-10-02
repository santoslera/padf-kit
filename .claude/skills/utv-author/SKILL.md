---
name: utv-author
description: >
  Confront the frame, then run Example Mapping as devil's advocate and produce a
  validated UTV. Use when the user wants to specify work, write a UTV, prepare the
  Monday batch, or turn an EXPLORE report / triaged issue / wayfinder map into a spec.
  Spec quality is the binding constraint of the whole system.
---

PREFLIGHT — verify these exist; if any is missing, STOP, name it, and offer `padf-bootstrap` (the harness is not built yet): `padf/specs/_template.md` · `padf/harness/harness.yaml` · `docs/charter.md`.

Read fresh, every time (never from memory):
- `padf/specs/_template.md` — the current template, authoritative
- `docs/charter.md` — every intent must trace here
- `docs/criticality-map.md` — decides the UTV `level:` (born-HEAVY zones listed there)
- `docs/domain-vocabulary.md` — canonical UTV language (one canonical noun per concept; no synonyms)
- `padf/harness/harness.yaml` — declared signals + tracker labels decide what Verification/flow can promise
- `padf/proposals/` — pending agent-drafted properties relevant to this UTV

Inputs (PR policy): `ready-for-author` issues (`gh issue list --label ready-for-author`), EXPLORE reports, and closed wayfinder maps. Cluster coupled items into one UTV (~1 week of work); do not resurrect retired ids.

Default planner is the planner model in the AGENTS.md Default agent map. Owner may name another model to test.

PROCESS — one UTV at a time, 25-minute timebox each:

0. CONFRONT THE FRAME — before reading any draft rules the owner brings.
   a. **Blind pre-pass:** from the one-line intent ONLY, write down your own expected
      rules, risks, and nastiest examples. THEN read the owner's draft. Every divergence
      is agenda — anchored critique of a polished draft finds typos; independent
      derivation finds misconceptions.
   b. **Scoping interview** (invoke the `grilling` skill as the primitive): what outcome,
      who notices it, what is deliberately out, the riskiest assumption, what would make
      this UTV wrong to build at all, what adjacent thing will someone assume is included.
   c. Record every challenge + disposition in the UTV `## Challenges` block
      (accepted → which rule changed · rejected → one-line owner reason).
      Zero challenges surfaced on a HEAVY UTV is a smell — say it out loud.
   Route out instead of authoring when the interview shows it: don't-know-enough →
   EXPLORE; too big / fog across sessions → a `wayfinder` map. Not every item becomes a UTV.
1. INTENT. Write the intent block: what user-visible outcome changes, traced to the charter.
2. EXAMPLE MAPPING — you are the devil's advocate; your one job is finding the examples the user CANNOT find. Four card types:
   - BLUE rules the user states → challenge each: "give me a literal example where this rule produces a different output than the neighbouring rule."
   - GREEN examples with LITERAL values only (never formulas: "100 → withdraw 20 → 80"). Push the dimensions: boundary, empty, duplicate, ordering, concurrency, already-done, out-of-range, and the adversarial case an optimizer would exploit. GREENs become the I/O matrix.
   - RED unanswerable questions → open_questions verbatim. NEVER answer them yourself; flag-don't-fill is the whole point.
   - Table full of REDs = the user doesn't know enough yet → suggest EXPLORATION mode. Table full of BLUEs = story too big → propose the split along failure-independence.
3. LEVEL. Set `level:` from the criticality map. Any UTV touching schema or stored data auto-promotes to HEAVY (`migration:` field ≠ none — the validator enforces it) — say so out loud when it happens. Declare `deps:` honestly; new dependencies also go under `ask_first`.
4. ORACLE SECTION. Propose oracle kind + 3 independent properties minimum. For HEAVY, name the **Adapter witness** per property (integration-level; fake-only greens are how silent production no-ops merge). Then attack your own draft:
   - **EDFH pass** — run `padf/harness/prompts/edfh-pass.md`; every surviving cheat becomes a property amendment or hidden-split nominee.
   - HEAVY or auth/data-touching: **premortem** (`premortem` skill — "this shipped a disaster, what happened") and **threat model** (`security-threat-model` skill — source → boundary → sink for every new surface; feeds `Never` and the negative-surface line in `Always`).
   Drafts go in `padf/proposals/`; you never write into `padf/oracle/`; the USER approves and freezes.
5. GUARDRAILS. always / ask_first (HALT) / never — `never` must include at least one forbidden APPROACH, not just scope. Auth/data UTVs: `Always` names the negative surface (what this UTV does NOT change, regression-asserted). **Decision-budget:** close this step by listing remaining implementer freedoms (internal structure, naming, reversible cosmetics). Each freedom is a bullet under Ask first or Never. An unlisted freedom is a red card — the implementer will invent it unsupervised.
6. REVIEW CONTRACT. Fill `## Review contract`: the commands R4 must re-run, the I/O rows to reproduce, the ADRs to re-verify against the diff, the journeys most likely to hide an unconsidered path (review protocol).
7. VALIDATE. Fill remaining template fields (budget, targets, Contract-verb Verification lines). Run `just utv-validate padf/specs/UTV-NNN-*.md`. Non-zero → fix and re-run; never present an invalid UTV as done. After the owner freezes: create the mirror issue (`gh issue create --label utv`, linking consumed intake issues) and record its number in the UTV frontmatter `issue:` and `feature_list.json`.

RED CARDS > 0 at timebox end = the UTV is NOT ready. Say so plainly; it is countable.
DONE = `just utv-validate` exit 0 and the user told the UTV awaits their freeze.
