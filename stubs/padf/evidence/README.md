# padf/evidence/

One file per completed UTV attempt: `EVIDENCE-UTV-NNN.md`.

Finish = `just evidence-check padf/evidence/EVIDENCE-UTV-NNN.md` exit 0.

Required headings: (1) UTV id and attempt (2) Commands run, quoted, with `exit N` (3) What changed (4) Oracle / suite / static (5) What would falsify (6) WHAT I HAVE NOT TESTED (7) HALT lines.

R4 writes `REVIEW-UTV-NNN-attemptN.md`: a `**Head:** <sha>` line (the commit reviewed) and one `## VERDICT: GREEN-recommend|AMBER|ABSTAIN` line (`padf/harness/fsm/roles/reviewer.md`). `just utv-close` reads the latest one.
