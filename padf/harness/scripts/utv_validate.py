#!/usr/bin/env python3
"""Definition-of-Ready check for a UTV markdown file. Exit 0 only if valid."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = (
    "## Intent",
    "## Challenges",
    "## HALT",
    "## Rules (blue)",
    "## I/O matrix (green — literal values only)",
    "## Open questions (red)",
    "## Always",
    "## Ask first",
    "## Never",
    "## Oracle",
    "## Review contract",
    "## Verification",
)

REQUIRED_FRONTMATTER = (
    "id",
    "slug",
    "title",
    "status",
    "level",
    "intent_trace",
    "oracle",
    "migration",
    "deps",
)

WEASEL = re.compile(
    r"\b(appropriately|correctly|properly|robust|handle|etc\.?|as needed|should work)\b",
    re.I,
)


def fail(msg: str) -> None:
    print(f"utv-validate: FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        fail("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        fail("unclosed YAML frontmatter")
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#") or line.startswith(" "):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"')
    return meta, body


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        fail("usage: utv_validate.py padf/specs/UTV-NNN-*.md")
    path = Path(argv[1])
    if not path.is_file():
        fail(f"not a file: {path}")
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    for key in REQUIRED_FRONTMATTER:
        if not meta.get(key):
            fail(f"frontmatter missing {key!r}")

    utv_id = meta["id"]
    if not re.fullmatch(r"UTV-\d{3}", utv_id):
        fail(f"id must look like UTV-001, got {utv_id!r}")
    if utv_id.lower() not in path.name.lower():
        fail(f"filename {path.name!r} must contain {utv_id}")

    if meta["level"] not in {"LIGHT", "STANDARD", "HEAVY"}:
        fail(f"level must be LIGHT|STANDARD|HEAVY, got {meta['level']!r}")
    if meta["status"] not in {"draft", "ready", "in-progress", "halted", "done", "archived"}:
        fail(f"unknown status {meta['status']!r}")

    migration = meta["migration"].split("#", 1)[0].strip()
    if migration != "none" and not re.fullmatch(r"\d{3}", migration):
        fail(f"migration must be 'none' or a 3-digit number, got {migration!r}")
    if migration != "none" and meta["level"] != "HEAVY":
        fail("migration != none auto-promotes the UTV to HEAVY — set level: HEAVY")

    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            fail(f"missing heading {heading!r}")

    red = body.split("## Open questions (red)", 1)[1].split("## Always", 1)[0]
    red_items = [ln for ln in red.splitlines() if re.match(r"^\d+\.", ln.strip())]
    if len(red_items) > 3:
        fail(f"at most 3 open questions, found {len(red_items)}")

    never = body.split("## Never", 1)[1].split("## Oracle", 1)[0]
    never_items = [
        ln
        for ln in never.splitlines()
        if ln.strip().startswith("-") and "forbidden APPROACH" not in ln
    ]
    if not never_items:
        fail("## Never must list at least one forbidden approach")

    if meta["level"] == "HEAVY":
        oracle_sec = body.split("## Oracle", 1)[1].split("## Review contract", 1)[0]
        if "Adapter witness" not in oracle_sec:
            fail(
                "HEAVY UTV: ## Oracle must carry an 'Adapter witness' line "
                "(integration-level witness per property — fake-only greens hide production no-ops)"
            )

    weasels = WEASEL.findall(body)
    if weasels:
        fail(f"weasel words in body: {sorted(set(weasels))}")

    print(f"utv-validate: OK {path}")


if __name__ == "__main__":
    main(sys.argv)
