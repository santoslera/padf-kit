#!/usr/bin/env bash
# Install PADF skills on this machine. Re-run after pull.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.config/padf"
printf '%s\n' "$ROOT" > "$HOME/.config/padf/home"

copied=0
for dest in "$HOME/.claude/skills" "$HOME/.grok/skills"; do
  mkdir -p "$dest"
  for skill in "$ROOT/.claude/skills"/padf-* "$ROOT/.claude/skills"/utv-author "$ROOT/.claude/skills"/semaphore-triage; do
    [[ -d "$skill" ]] || continue
    name="$(basename "$skill")"
    rm -rf "$dest/$name"
    cp -R "$skill" "$dest/$name"
    copied=$((copied + 1))
  done
done

echo "PADF_HOME=$ROOT  (wrote ~/.config/padf/home)"
echo "Copied skills into ~/.claude/skills and ~/.grok/skills"
echo "Next: in an agent session, run padf-init against the target repo."
echo "Or: python3 \"$ROOT/scripts/apply.py\" --target /path/to/repo --answers $ROOT/examples/answers.thin.json"
