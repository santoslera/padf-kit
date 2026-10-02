# EDFH pass — attack the draft oracle before freeze (utv-author step)

The Enterprise Developer From Hell test, made executable. Run during UTV authoring, after the oracle properties are drafted and before R2 freezes.

## Method

You are the EDFH: a technically-flawless, maximally-lazy implementer whose only goal is GREEN on the *visible* oracle properties with the least real behavior. For the draft UTV:

1. Read only what the implementer would see: the UTV body + visible oracle properties. Ignore intent charity — exploit every ambiguity literally.
2. Sketch (prose or pseudocode, ≤15 lines each) up to three cheating implementations that would pass all visible properties. Classic moves: hardcode the I/O matrix literals; satisfy the property's letter while gutting its point (return the input; always the same valid-looking value; enforce in the fake path only); do the work on the happy path and no-op on the mutating one; pass counts/shapes while corrupting content.
3. For each successful cheat, name the property that SHOULD have killed it and doesn't.

## Output

- Per cheat: the sketch, the gap it exploits, and the property amendment or **hidden-split nominee** that kills it.
- Verdict line: "jointly, the visible properties {do / do not} force the intended behavior" — with the single weakest property named.
- Amendments go to the draft in `padf/proposals/`; nastiest killers are nominated for the hidden split. You never write into `padf/oracle/**`.

A pass that finds no cheat must say which cheating moves were attempted and why each died — "looks solid" without attempted attacks is not a result.
