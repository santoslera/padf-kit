<!-- UTV PRs only (PR policy). Draft from worktree creation; flip to ready when EVIDENCE lands. -->

**UTV:** `padf/specs/UTV-NNN-<slug>.md` · mirror issue: #
**EVIDENCE:** `padf/evidence/EVIDENCE-UTV-NNN.md` (block 6 filled honestly)
**Closes:** #<mirror> #<intake issues this UTV consumes>
<!-- Close-out (PR policy) lands on THIS PR before merge: `just utv-close`, then merge. No follow-up hygiene PR. GitHub closes these issues on merge. -->

## Review contract (from the UTV — R4 re-runs these independently, review protocol)

- [ ] Every EVIDENCE-quoted command re-runnable as written
- [ ] I/O matrix rows reproducible as binary criteria
- [ ] `Never` / `Always` compliance visible in the diff
- [ ] Migration (if `migration:` ≠ none): up-down-up tested, additive-only, human-read
- [ ] Negative surface unchanged (auth/data UTVs)

<!-- R4: Request Changes = AMBER (+ `amber` label). Comment = GREEN-recommend, or ABSTAIN (+ `amber`) when something could not be verified. REVIEW records **Head:** <sha>; `just utv-close` refuses a missing, non-GREEN or stale review. Never Approve-as-authority; owner decides every AMBER. -->
