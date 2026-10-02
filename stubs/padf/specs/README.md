# specs/ — disposable UTVs

Active files: `UTV-NNN-*.md`. On accept they move to `_archive/` via `just utv-close` on that PR, before merge.

Template: `_template.md`. Validate: `just utv-validate padf/specs/UTV-NNN-*.md`. Do not start a worktree until `ready` and R2 has frozen any oracle. Do not run that loop on `main`.
