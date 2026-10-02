# L3 adversarial sweep — diff-scoped (review protocol)

Method for the R4 reviewer's third layer. A repo-wide adversarial audit, rescoped: the UTV is your expectation baseline and the PR diff + its blast radius is your search space. Do not audit the whole repo — cross-reference instead ("pre-existing, file an issue").

Work each dimension. For every area: state how it SHOULD behave per the UTV/ADRs, then read/execute to confirm or refute. Disprove-first; report only survivors, each with evidence label + concrete failure scenario.

## Dimensions

1. **Corner cases & re-entry.** On every changed surface: second call, out-of-order call, empty/null/huge input, partial failure mid-operation, concurrent invocation (the two-tabs test), already-done/already-deleted state. The UTV's I/O matrix covers the specified cases — you hunt the unspecified neighbours.
2. **Unconsidered journeys.** Enumerate the real user/agent paths that traverse the changed code (routes in, events out, CLI, webhooks). Which journeys does the I/O matrix never mention? Walk the two most plausible ones end-to-end.
3. **Security.** Any changed auth, input-parsing, URL/file/query construction, or permission surface: trace source → trust boundary → sink and try to break it (privilege escalation, tenant / cross-account leak, injection, SSRF, path traversal, unsigned/expired-token acceptance). No generic concerns — a finding needs the full chain. Probe the negative surface: endpoints/roles the UTV claims NOT to change must provably behave as before.
4. **Fake-vs-real drift.** For every invariant a unit test asserts through a fake: does the real adapter enforce it too? Read the real repository/service methods the diff touches; any column-list `update`, partial write, or divergent fake behavior is a finding even while all tests are green. Integration witnesses beat reading — run them when Docker allows, else BLOCKED with the exact command.
5. **Doc/ADR deviation.** For each ADR the UTV names: does it still tell the truth after this diff (schema blocks, file paths, `## Implementation files`, invariants)? A diff that silently falsifies an ADR is a finding; the fix is an ADR amendment task, not silence. Same for module READMEs the diff makes stale.
6. **Latent debt with teeth.** Unbounded growth, missing timeout/cancellation on new I/O, resource leaks, events fired without idempotent consumers — only where the diff introduced or touched it, and only with a concrete triggering scenario.

## Scope discipline

- Pre-existing defects you trip over → GitHub Issue (evidence label + repro), one line in the REVIEW's "out of scope" list. Never expand the review to fix or fully chase them.
- HEAVY: after the sweep, adversarially verify each finding (attempt to refute it; drop what dies).
- Time-box to the UTV's `level:`; report coverage honestly — dimensions not run are listed as not run, never implied as clean.
