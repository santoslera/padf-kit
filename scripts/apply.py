#!/usr/bin/env python3
"""Copy the PADF Stage 0 kit into a target repo. Does not merge, freeze, or invent oracles."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

REQUIRED = (
    "mode",
    "project",
    "owner",
    "repo",
    "github_handle",
    "stacks",
    "profile",
    "problem",
)
PROFILES = ("strict", "modular", "thin")
MODES = ("greenfield", "brownfield")
PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")


class ApplyError(Exception):
    pass


def _stringify(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def _subst(text: str, mapping: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in mapping:
            raise ApplyError(f"unresolved placeholder {{{{{key}}}}}")
        return mapping[key]

    return PLACEHOLDER_RE.sub(repl, text)


def _mapping(answers: dict[str, object], profile_body: str) -> dict[str, str]:
    raw = dict(answers)
    raw.setdefault("metric", "(name the one number that would prove value)")
    raw.setdefault("heavy_zones", "(none listed yet)")
    raw.setdefault("kill_criteria", "(what observed result within N weeks means stop)")
    raw.setdefault("implementer_model", "(owner names the implementer family)")
    raw.setdefault("planner_model", "(owner names the planner/reviewer family)")
    raw.setdefault("suite_fallback", "# fill with this stack's unit + lint + typecheck")
    raw["profile_body"] = profile_body.strip() + "\n"
    raw["updated"] = date.today().isoformat()
    stacks = answers.get("stacks")
    if isinstance(stacks, list):
        raw["stacks_yaml"] = "\n".join(f"  - {s}" for s in stacks)
    else:
        raw["stacks_yaml"] = f"  - {stacks}"
    checks = answers.get("ci_checks") or []
    if isinstance(checks, list) and checks:
        raw["ci_checks_json"] = json.dumps(checks)
    else:
        raw["ci_checks_json"] = "[]"
    return {k: _stringify(v) for k, v in raw.items()}


def _src(entry: dict[str, object], kit_root: Path, source_root: Path) -> Path:
    rel = str(entry["from"])
    if rel.startswith("kit:"):
        return kit_root / rel[4:]
    return source_root / rel


def _patch_wizard(text: str, answers: dict[str, object]) -> str:
    repo = str(answers["repo"])
    text = re.sub(r'^REPO="[^"]*"', f'REPO="{repo}"', text, count=1, flags=re.M)
    checks = answers.get("ci_checks")
    if isinstance(checks, list) and checks:
        inner = ",\n      ".join(json.dumps(c) for c in checks)
        text = re.sub(
            r'"contexts": \[[^\]]*\]',
            f'"contexts": [\n      {inner}\n    ]',
            text,
            count=1,
            flags=re.S,
        )
    return text


def _merge_justfile(dest: Path, incoming: str) -> str:
    if not dest.is_file():
        return incoming
    existing = dest.read_text(encoding="utf-8")
    if "utv-validate file:" in existing:
        return existing
    return existing.rstrip() + "\n\n# PADF Contract verbs (appended by padf-init)\n" + incoming


def apply(
    target: Path,
    answers: dict[str, object],
    *,
    kit_root: Path,
    source_root: Path,
    force: bool = False,
) -> list[str]:
    for key in REQUIRED:
        if not answers.get(key):
            raise ApplyError(f"answers missing {key!r}")
    mode = str(answers["mode"])
    if mode not in MODES:
        raise ApplyError(f"mode must be greenfield|brownfield, got {mode!r}")
    profile = str(answers["profile"])
    if profile not in PROFILES:
        raise ApplyError(f"profile must be strict|modular|thin, got {profile!r}")

    target = target.resolve()
    if not target.is_dir():
        raise ApplyError(f"target is not a directory: {target}")
    if mode == "greenfield" and (target / "padf").exists() and not force:
        raise ApplyError("greenfield target already has padf/ — pass --force or use brownfield")

    profile_path = kit_root / "profiles" / f"{profile}.md"
    if not profile_path.is_file():
        raise ApplyError(f"missing profile file: {profile_path}")
    mapping = _mapping(answers, profile_path.read_text(encoding="utf-8"))

    manifest_path = kit_root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    written: list[str] = []
    for entry in manifest["copy"]:
        src = _src(entry, kit_root, source_root)
        if not src.is_file():
            raise ApplyError(f"source missing: {src}")
        dest = target / str(entry["to"])
        if entry.get("skip_if_exists") and dest.is_file() and not force:
            continue
        text = src.read_text(encoding="utf-8")
        if entry.get("wizard"):
            text = _patch_wizard(text, answers)
        if entry.get("subst"):
            text = _subst(text, mapping)
        if entry.get("merge_justfile"):
            text = _merge_justfile(dest, text)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        if dest.suffix == ".sh":
            dest.chmod(dest.stat().st_mode | 0o111)
        written.append(str(entry["to"]))

    for extra in (
        "padf/specs/_archive",
        "padf/oracle/.hidden",
        "padf/proposals",
        "padf/evidence",
    ):
        (target / extra).mkdir(parents=True, exist_ok=True)

    answers_out = target / "padf/harness/init-answers.json"
    answers_out.parent.mkdir(parents=True, exist_ok=True)
    answers_out.write_text(json.dumps(answers, indent=2) + "\n", encoding="utf-8")
    written.append("padf/harness/init-answers.json")
    return written


def _discover() -> tuple[Path, Path]:
    """Package root is the directory that contains scripts/ and MANIFEST.json."""
    kit_root = Path(__file__).resolve().parents[1]
    return kit_root, kit_root


def main(argv: list[str]) -> None:
    target: Path | None = None
    answers_path: Path | None = None
    force = False
    i = 1
    while i < len(argv):
        if argv[i] == "--force":
            force = True
            i += 1
        elif argv[i] == "--target" and i + 1 < len(argv):
            target = Path(argv[i + 1])
            i += 2
        elif argv[i] == "--answers" and i + 1 < len(argv):
            answers_path = Path(argv[i + 1])
            i += 2
        else:
            print(f"padf-init apply: FAIL: unknown arg {argv[i]!r}", file=sys.stderr)
            raise SystemExit(1)
    if target is None or answers_path is None:
        print(
            "padf-init apply: FAIL: usage: apply.py [--force] --target DIR --answers FILE.json",
            file=sys.stderr,
        )
        raise SystemExit(1)
    if not answers_path.is_file():
        print(f"padf-init apply: FAIL: not a file: {answers_path}", file=sys.stderr)
        raise SystemExit(1)
    try:
        answers = json.loads(answers_path.read_text(encoding="utf-8"))
        if not isinstance(answers, dict):
            raise ApplyError("answers must be a JSON object")
        kit_root, source_root = _discover()
        written = apply(
            target, answers, kit_root=kit_root, source_root=source_root, force=force
        )
    except (ApplyError, json.JSONDecodeError, OSError) as exc:
        print(f"padf-init apply: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"padf-init apply: OK {len(written)} files → {target}")
    for path in written:
        print(f"  {path}")


if __name__ == "__main__":
    main(sys.argv)
