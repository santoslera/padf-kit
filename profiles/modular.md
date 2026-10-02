**Modular monolith** — one deployable, modules with named I/O. Use for a real product that is not yet several bounded contexts.

Contracts on:

- C2 layer direction at module edges (callers do not reach past the module's API)
- C4 file size ≤ 300 lines on changed files

C1/C3 are off until a second context exists. Domain-purity theatre is not required. Agents still may not invent a new module boundary — that is an ADR.
