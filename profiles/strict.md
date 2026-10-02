**Strict** — domain-pure modular monolith. Use when the domain is the product: money, regulated records, tenancy, multi-module.

Contracts on (when `verify-arch` exists; until then they are ADR law):

- C1 domain purity — domain imports no framework/IO
- C2 layer direction — entry → service → domain
- C3 context independence — bounded contexts do not import each other
- C4 file size ≤ 300 lines on changed files
- C5 complexity / CRAP ceiling on changed files

Logic lives in the domain; persistence behind repositories; tests of domain/application use fakes, not a live DB.
