#!/usr/bin/env python3
"""Deterministic Stage 0 checker for an EVIDENCE file. Exit 0 only if valid.

Does not re-run quoted commands — that is R4 L2 / verify-suite.
Checks: house-format blocks exist, block-2 commands are fenced with recorded
exit codes, block 6 (WHAT I HAVE NOT TESTED) is filled, filename matches.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

HEADING_RE = re.compile(r"^## .+$", re.M)
FENCE_RE = re.compile(r"```(?:bash|sh|shell|zsh)?[ \t]*\n(.*?)```", re.S | re.I)
EXIT_RE = re.compile(r"\bexit\s*`?(\d+)`?", re.I)
PLACEHOLDER_RE = re.compile(
    r"^(tbd|todo|\.\.\.|n/?a|none\.?|not applicable|lorem ipsum)$",
    re.I,
)
FILENAME_RE = re.compile(r"^EVIDENCE-(UTV-\d{3})\.md$")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)

REQUIRED = (
    (r"UTV id", "block 1: UTV id and attempt"),
    (r"Commands run", "block 2: Commands run (quoted) and their exit codes"),
    (r"What changed", "block 3: What changed (paths only)"),
    (r"Oracle", "block 4: Oracle / suite / static results"),
    (r"falsify", "block 5: What would falsify this change"),
    (r"NOT TESTED|have not tested", "block 6: WHAT I HAVE NOT TESTED"),
    (r"HALT", "block 7: HALT lines left open"),
)


class EvidenceCheckError(Exception):
    pass


def _sections(text: str) -> list[tuple[str, str]]:
    matches = list(HEADING_RE.finditer(text))
    out: list[tuple[str, str]] = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((match.group(0), text[match.end() : end]))
    return out


def _find_section(
    sections: list[tuple[str, str]], pattern: str
) -> tuple[str, str] | None:
    cre = re.compile(pattern, re.I)
    for heading, body in sections:
        if cre.search(heading):
            return heading, body
    return None


def _strip_body(body: str) -> str:
    return HTML_COMMENT_RE.sub("", body).strip()


def check(path: Path) -> None:
    errors: list[str] = []
    if not path.is_file():
        raise EvidenceCheckError(f"not a file: {path}")

    name_match = FILENAME_RE.fullmatch(path.name)
    if not name_match:
        errors.append(
            f"filename must look like EVIDENCE-UTV-001.md, got {path.name!r}"
        )
        utv_id = ""
    else:
        utv_id = name_match.group(1)

    text = path.read_text(encoding="utf-8")
    if utv_id and utv_id not in text:
        errors.append(f"{utv_id} must appear in the evidence body")

    sections = _sections(text)
    headings = [h for h, _ in sections]
    for pattern, label in REQUIRED:
        if not any(re.search(pattern, h, re.I) for h in headings):
            errors.append(f"missing {label}")

    commands = _find_section(sections, r"Commands run")
    if commands is not None:
        body = commands[1]
        fences = list(FENCE_RE.finditer(body))
        if not fences:
            errors.append(
                "block 2: quoted commands must be in fenced code blocks, not paraphrased"
            )
        else:
            for i, fence in enumerate(fences):
                following = (
                    body[fence.end() : fences[i + 1].start()]
                    if i + 1 < len(fences)
                    else body[fence.end() :]
                )
                recorded = fence.group(0) + following
                if not EXIT_RE.search(recorded):
                    snippet = fence.group(1).strip().splitlines()[0] if fence.group(1).strip() else "(empty)"
                    errors.append(
                        f"block 2: quoted command has no recorded exit code: {snippet[:80]}"
                    )

    block6 = _find_section(sections, r"NOT TESTED|have not tested")
    if block6 is not None:
        filled = _strip_body(block6[1])
        if not filled:
            errors.append("block 6: WHAT I HAVE NOT TESTED is empty")
        elif PLACEHOLDER_RE.fullmatch(filled):
            errors.append("block 6: WHAT I HAVE NOT TESTED is a placeholder")
        elif len(re.sub(r"\s+", "", filled)) < 20:
            errors.append("block 6: WHAT I HAVE NOT TESTED is too thin to be honest")

    if errors:
        raise EvidenceCheckError("; ".join(errors))


def _golden() -> str:
    return (
        "# EVIDENCE-UTV-001\n\n"
        "## 1. UTV id and attempt\n\n"
        "- **UTV:** UTV-001 `selftest`\n"
        "- **Attempt:** 1\n\n"
        "## 2. Commands run (quoted) and exit codes\n\n"
        "```bash\njust utv-validate padf/specs/UTV-001-example.md\n```\n"
        "exit `0`\n\n"
        "## 3. What changed (paths only)\n\n"
        "- `padf/harness/scripts/evidence_check.py`\n\n"
        "## 4. Oracle / suite / static results\n\n"
        "No oracle. Checker selftest only.\n\n"
        "## 5. What would falsify this change\n\n"
        "A missing block 6 that still exits 0.\n\n"
        "## 6. WHAT I HAVE NOT TESTED\n\n"
        "- Re-running quoted commands (R4's job).\n"
        "- verify-oracle / verify-suite (not implemented).\n\n"
        "## 7. HALT lines left open\n\n"
        "None.\n"
    )


def selftest() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        good = Path(tmp) / "EVIDENCE-UTV-001.md"
        good.write_text(_golden(), encoding="utf-8")
        check(good)
        bad = Path(tmp) / "EVIDENCE-UTV-001.md"
        bad.write_text(
            _golden().replace("## 6. WHAT I HAVE NOT TESTED", "## 6. Notes"),
            encoding="utf-8",
        )
        try:
            check(bad)
        except EvidenceCheckError:
            print("evidence-check: selftest OK (good passes; missing block 6 is red)")
            return
        raise EvidenceCheckError("selftest: missing block 6 did not fail")


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        print(
            "evidence-check: FAIL: usage: evidence_check.py "
            "padf/evidence/EVIDENCE-UTV-NNN.md | --selftest",
            file=sys.stderr,
        )
        raise SystemExit(1)
    try:
        if argv[1] == "--selftest":
            selftest()
            return
        check(Path(argv[1]))
    except EvidenceCheckError as exc:
        print(f"evidence-check: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"evidence-check: OK {argv[1]}")


if __name__ == "__main__":
    main(sys.argv)
