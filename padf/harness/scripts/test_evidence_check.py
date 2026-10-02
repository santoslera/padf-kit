#!/usr/bin/env python3
"""Tests for the evidence-check Contract verb. Run: python3 padf/harness/scripts/test_evidence_check.py"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evidence_check import EvidenceCheckError, check


def house_evidence(*, block6: str | None = None, commands: str | None = None) -> str:
    b6 = block6 if block6 is not None else (
        "- Concurrent callers of the new endpoint.\n"
        "- Production deploy and the hidden oracle split (none frozen).\n"
    )
    cmds = commands if commands is not None else (
        "```bash\n"
        "just utv-validate padf/specs/UTV-001-example.md\n"
        "```\n"
        "exit `0` — utv-validate: OK\n"
    )
    return (
        "# EVIDENCE-UTV-001\n\n"
        "## 1. UTV id and attempt\n\n"
        "- **UTV:** UTV-001 `example`\n"
        "- **Attempt:** 1\n\n"
        "## 2. Commands run (quoted) and exit codes\n\n"
        f"{cmds}\n"
        "## 3. What changed (paths only)\n\n"
        "- `backend/app/foo.py`\n\n"
        "## 4. Oracle / suite / static results\n\n"
        "Oracle none. Unit suite green.\n\n"
        "## 5. What would falsify this change\n\n"
        "A regression in foo that still reports success.\n\n"
        "## 6. WHAT I HAVE NOT TESTED\n\n"
        f"{b6}\n"
        "## 7. HALT lines left open\n\n"
        "None.\n"
    )


def write_evidence(dir_path: Path, body: str, name: str = "EVIDENCE-UTV-001.md") -> Path:
    path = dir_path / name
    path.write_text(body, encoding="utf-8")
    return path


class EvidenceCheckTests(unittest.TestCase):
    def test_house_format_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_evidence(Path(tmp), house_evidence())
            check(path)

    def test_missing_file_fails(self) -> None:
        with self.assertRaises(EvidenceCheckError) as ctx:
            check(Path("/no/such/EVIDENCE-UTV-001.md"))
        self.assertIn("not a file", str(ctx.exception))

    def test_wrong_filename_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_evidence(Path(tmp), house_evidence(), name="notes.md")
            with self.assertRaises(EvidenceCheckError) as ctx:
                check(path)
            self.assertIn("filename", str(ctx.exception))

    def test_missing_block_6_heading_fails(self) -> None:
        body = house_evidence().replace(
            "## 6. WHAT I HAVE NOT TESTED", "## 6. Notes"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = write_evidence(Path(tmp), body)
            with self.assertRaises(EvidenceCheckError) as ctx:
                check(path)
            self.assertIn("block 6", str(ctx.exception).lower())

    def test_empty_block_6_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_evidence(Path(tmp), house_evidence(block6="\n"))
            with self.assertRaises(EvidenceCheckError) as ctx:
                check(path)
            self.assertIn("block 6", str(ctx.exception).lower())

    def test_placeholder_block_6_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_evidence(Path(tmp), house_evidence(block6="TBD\n"))
            with self.assertRaises(EvidenceCheckError) as ctx:
                check(path)
            self.assertIn("placeholder", str(ctx.exception).lower())

    def test_missing_quoted_commands_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_evidence(
                Path(tmp), house_evidence(commands="ran the tests, they passed\n")
            )
            with self.assertRaises(EvidenceCheckError) as ctx:
                check(path)
            self.assertIn("quoted", str(ctx.exception).lower())

    def test_quoted_command_without_exit_code_fails(self) -> None:
        cmds = (
            "```bash\n"
            "just utv-validate padf/specs/UTV-001-example.md\n"
            "```\n"
            "looked green\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = write_evidence(Path(tmp), house_evidence(commands=cmds))
            with self.assertRaises(EvidenceCheckError) as ctx:
                check(path)
            self.assertIn("exit", str(ctx.exception).lower())

    def test_missing_falsify_block_fails(self) -> None:
        body = house_evidence().replace(
            "## 5. What would falsify this change", "## 5. Extra notes"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = write_evidence(Path(tmp), body)
            with self.assertRaises(EvidenceCheckError) as ctx:
                check(path)
            self.assertIn("block 5", str(ctx.exception).lower())

    def test_utv_id_must_appear_in_body(self) -> None:
        body = house_evidence().replace("UTV-001", "UTV-099")
        with tempfile.TemporaryDirectory() as tmp:
            path = write_evidence(Path(tmp), body, name="EVIDENCE-UTV-001.md")
            with self.assertRaises(EvidenceCheckError) as ctx:
                check(path)
            self.assertIn("UTV-001", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
