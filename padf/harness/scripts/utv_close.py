#!/usr/bin/env python3
"""Close out a UTV on its accepted PR: archive spec, mark feature_list done.

Does not merge and does not close GitHub issues — those happen when the PR
merges, via Closes keywords this verb prints. Run on the UTV branch after
accept, before merge (padf/README.md § PR policy).

Review gate (runs first, changes nothing when it fails): the latest
REVIEW-UTV-NNN-attemptN.md must say GREEN-recommend (or the owner passes
--owner-override "reason" for an AMBER/ABSTAIN merge), and the PR's own files
must be unchanged since the commit R4 recorded under **Head:** — only close-out
paths may move after review. Silence is not a review; a stale review is not
a review of this code.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

FILENAME_RE = re.compile(r"^(UTV-\d{3})-.+\.md$")
ISSUE_NUM_RE = re.compile(r"#(\d+)")
REVIEW_RE = re.compile(r"^REVIEW-(UTV-\d{3})-attempt(\d+)\.md$")
# House variants: "## VERDICT: AMBER — …" and "## Verdict\n\n**GREEN-recommend.** …"
VERDICT_RE = re.compile(
    r"^## VERDICT\b[:\s]*\**\s*(GREEN-recommend|AMBER|ABSTAIN)\b", re.M | re.I
)
# "- **Head:** `sha`" and "… · head `sha` (= review worktree HEAD)"
HEAD_RE = re.compile(r"(?:\*\*Head:\*\*|\bhead)\s*`([0-9a-f]{7,40})`", re.I)
PASS = "GREEN-recommend"
CLOSEOUT_PATHS = ("padf/specs/", "padf/work/feature_list.json")


class UtvCloseError(Exception):
    pass


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise UtvCloseError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise UtvCloseError("unclosed YAML frontmatter")
    raw = text[4:end]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#") or line.startswith(" "):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"')
    return meta, raw


def _repo_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / "padf" / "work" / "feature_list.json").is_file():
            return parent
    raise UtvCloseError("cannot find padf/work/feature_list.json")


def _issue_numbers(issue_line: str, meta_issue: str) -> list[int]:
    found: list[int] = []
    raw = meta_issue.split("#", 1)[0].strip()
    if raw.isdigit():
        found.append(int(raw))
    for match in ISSUE_NUM_RE.finditer(issue_line):
        n = int(match.group(1))
        if n not in found:
            found.append(n)
    return found


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise UtvCloseError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _main_ref(root: Path) -> str:
    for ref in ("origin/main", "main"):
        probe = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref],
            cwd=root, capture_output=True, text=True, check=False,
        )
        if probe.returncode == 0:
            return ref
    raise UtvCloseError("cannot find origin/main or main to scope the PR diff")


def _pr_paths(root: Path, main: str, commit: str) -> set[str]:
    base = _git(root, "merge-base", main, commit)
    return set(_git(root, "diff", "--name-only", base, commit).splitlines())


def _is_closeout(path: str, utv_id: str) -> bool:
    return path.startswith(CLOSEOUT_PATHS) or Path(path).name.startswith(
        f"REVIEW-{utv_id}-"
    )


def check_review(root: Path, utv_id: str, owner_override: str | None) -> str:
    """Fail unless the latest R4 review passes and still covers this code. Returns a receipt."""
    reviews = sorted(
        (int(m.group(2)), p)
        for p in (root / "padf" / "evidence").glob(f"REVIEW-{utv_id}-attempt*.md")
        if (m := REVIEW_RE.fullmatch(p.name))
    )
    if not reviews:
        raise UtvCloseError(
            f"no padf/evidence/REVIEW-{utv_id}-attemptN.md — R4 has not reviewed; "
            "no review is not a pass"
        )
    review = reviews[-1][1]
    body = review.read_text(encoding="utf-8")
    verdict = VERDICT_RE.search(body)
    if verdict is None:
        raise UtvCloseError(
            f"{review.name}: no '## VERDICT: GREEN-recommend|AMBER|ABSTAIN' line"
        )
    found = {v.lower(): v for v in (PASS, "AMBER", "ABSTAIN")}[verdict.group(1).lower()]
    head = HEAD_RE.search(body)
    if head is None:
        raise UtvCloseError(
            f"{review.name}: no '**Head:** <sha>' line — R4 must record the commit it reviewed"
        )
    reviewed = _git(root, "rev-parse", "--verify", f"{head.group(1)}^{{commit}}")
    current = _git(root, "rev-parse", "HEAD")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", reviewed, current],
        cwd=root, capture_output=True, check=False,
    )
    if ancestor.returncode != 0:
        raise UtvCloseError(
            f"reviewed head {reviewed[:7]} is not in this branch's history "
            "(rewritten?) — re-dispatch R4"
        )
    main = _main_ref(root)
    paths = _pr_paths(root, main, reviewed) | _pr_paths(root, main, current)
    watched = sorted(p for p in paths if not _is_closeout(p, utv_id))
    moved = (
        _git(root, "diff", "--name-only", reviewed, current, "--", *watched).splitlines()
        if watched
        else []
    )
    if moved:
        raise UtvCloseError(
            f"changed since R4 reviewed {reviewed[:7]}: {', '.join(moved)} — "
            "re-dispatch R4 on the current head"
        )
    if found != PASS and not owner_override:
        raise UtvCloseError(
            f"{review.name} verdict is {found}; close-out needs "
            f"{PASS}, or the owner's --owner-override \"reason\" (AMBER → merge)"
        )
    receipt = (
        f"- review: `padf/evidence/{review.name}` · verdict {found} · "
        f"reviewed head `{reviewed[:7]}` · closed at `{current[:7]}`\n"
    )
    if owner_override:
        receipt += f"- owner override: {owner_override}\n"
    return receipt


def close(spec: Path, owner_override: str | None = None) -> list[int]:
    if not spec.is_file():
        raise UtvCloseError(f"not a file: {spec}")
    if spec.name == "_template.md":
        raise UtvCloseError("refusing to close the UTV template")

    resolved = spec.resolve()
    if "_archive" in resolved.parts:
        raise UtvCloseError(f"already archived: {spec}")

    name_match = FILENAME_RE.fullmatch(spec.name)
    if not name_match:
        raise UtvCloseError(
            f"filename must look like UTV-001-slug.md, got {spec.name!r}"
        )
    utv_id = name_match.group(1)

    text = spec.read_text(encoding="utf-8")
    meta, raw_fm = _frontmatter(text)
    if meta.get("id") != utv_id:
        raise UtvCloseError(
            f"frontmatter id {meta.get('id')!r} does not match filename {utv_id}"
        )

    issue_line = next(
        (ln for ln in raw_fm.splitlines() if ln.startswith("issue:")),
        "",
    )
    issues = _issue_numbers(issue_line, meta.get("issue", ""))

    root = _repo_root(spec)
    archive_dir = root / "padf" / "specs" / "_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    dest = archive_dir / spec.name
    if dest.exists():
        raise UtvCloseError(f"archive already has {dest.name}")
    plan = spec.with_name(f"{utv_id}.plan.md")
    plan_dest = archive_dir / plan.name
    if plan.is_file() and plan_dest.exists():
        raise UtvCloseError(f"archive already has {plan.name}")

    queue_path = root / "padf" / "work" / "feature_list.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    items = queue.get("items")
    if not isinstance(items, list):
        raise UtvCloseError("feature_list.json missing items array")
    item = next((it for it in items if it.get("id") == utv_id), None)
    if item is None:
        raise UtvCloseError(f"UTV {utv_id} not in feature_list.json")

    extra = item.get("issue")
    if isinstance(extra, int) and extra not in issues:
        issues.append(extra)

    receipt = check_review(root, utv_id, owner_override)
    new_text = re.sub(r"(?m)^status:\s*\S+", "status: done", text, count=1)
    new_text = new_text.rstrip() + "\n\n## Close-out\n\n" + receipt
    dest.write_text(new_text, encoding="utf-8")
    spec.unlink()

    if plan.is_file():
        plan_dest.write_text(plan.read_text(encoding="utf-8"), encoding="utf-8")
        plan.unlink()

    rel = dest.relative_to(root).as_posix()
    item["status"] = "done"
    item["spec"] = rel
    queue["updated"] = date.today().isoformat()
    queue_path.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    return issues


def main(argv: list[str]) -> None:
    override = None
    if len(argv) == 4 and argv[2] == "--owner-override" and argv[3].strip():
        override = argv[3].strip()
    elif len(argv) != 2:
        print(
            "utv-close: FAIL: usage: utv_close.py padf/specs/UTV-NNN-*.md "
            '[--owner-override "reason"]',
            file=sys.stderr,
        )
        raise SystemExit(1)
    try:
        spec = Path(argv[1])
        issues = close(spec, override)
    except UtvCloseError as exc:
        print(f"utv-close: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"utv-close: OK {spec.name}")
    if issues:
        print("Closes " + " ".join(f"#{n}" for n in issues))


if __name__ == "__main__":
    main(sys.argv)
