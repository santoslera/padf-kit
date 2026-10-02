#!/usr/bin/env python3
"""Tests for padf-init apply. Run: python3 padf/kit/scripts/test_apply.py"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from apply import ApplyError, apply


ANSWERS = {
    "mode": "greenfield",
    "project": "demo",
    "owner": "Ada",
    "repo": "ada/demo",
    "github_handle": "ada",
    "stacks": ["python"],
    "profile": "thin",
    "problem": "Track widgets.",
    "metric": "Widgets logged.",
    "heavy_zones": "none yet",
    "kill_criteria": "No widgets in 4 weeks.",
    "implementer_model": "Grok",
    "planner_model": "Fable",
    "suite_fallback": "pytest -q",
    "ci_checks": ["Lint"],
}


def seed_source(root: Path) -> None:
    (root / "padf/harness/scripts").mkdir(parents=True)
    (root / "padf/harness/scripts/utv_validate.py").write_text("# validate\n")
    kit = root / "padf/kit"
    (kit / "stubs/docs").mkdir(parents=True)
    (kit / "stubs/docs/charter.md").write_text("# {{project}}\n{{problem}}\n")
    (kit / "stubs/docs/adr").mkdir(parents=True)
    (kit / "profiles").mkdir(parents=True)
    (kit / "profiles/thin.md").write_text("Thin profile body.\n")
    (kit / "MANIFEST.json").write_text(
        json.dumps(
            {
                "copy": [
                    {
                        "from": "padf/harness/scripts/utv_validate.py",
                        "to": "padf/harness/scripts/utv_validate.py",
                    },
                    {
                        "from": "kit:stubs/docs/charter.md",
                        "to": "docs/charter.md",
                        "subst": True,
                        "skip_if_exists": True,
                    },
                    {
                        "from": "kit:stubs/docs/adr/000-architecture.md",
                        "to": "docs/adr/000-architecture.md",
                        "subst": True,
                    },
                ]
            }
        )
    )
    (kit / "stubs/docs/adr/000-architecture.md").write_text(
        "profile: {{profile}}\n{{profile_body}}\n"
    )


class ApplyTests(unittest.TestCase):
    def test_greenfield_writes_and_substitutes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            dst.mkdir()
            seed_source(src)
            written = apply(
                dst,
                ANSWERS,
                kit_root=src / "padf/kit",
                source_root=src,
            )
            self.assertIn("docs/charter.md", written)
            charter = (dst / "docs/charter.md").read_text()
            self.assertIn("Track widgets.", charter)
            self.assertIn("# demo", charter)
            adr = (dst / "docs/adr/000-architecture.md").read_text()
            self.assertIn("profile: thin", adr)
            self.assertIn("Thin profile body.", adr)
            self.assertTrue((dst / "padf/harness/scripts/utv_validate.py").is_file())

    def test_brownfield_skips_existing_charter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            dst.mkdir()
            seed_source(src)
            (dst / "docs").mkdir()
            (dst / "docs/charter.md").write_text("EXISTING\n")
            answers = dict(ANSWERS, mode="brownfield")
            apply(dst, answers, kit_root=src / "padf/kit", source_root=src)
            self.assertEqual((dst / "docs/charter.md").read_text(), "EXISTING\n")

    def test_greenfield_refuses_existing_padf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            dst.mkdir()
            seed_source(src)
            (dst / "padf").mkdir()
            with self.assertRaises(ApplyError) as ctx:
                apply(dst, ANSWERS, kit_root=src / "padf/kit", source_root=src)
            self.assertIn("already has padf/", str(ctx.exception))

    def test_unknown_profile_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dst = Path(tmp) / "dst"
            src.mkdir()
            dst.mkdir()
            seed_source(src)
            bad = dict(ANSWERS, profile="ddd")
            with self.assertRaises(ApplyError) as ctx:
                apply(dst, bad, kit_root=src / "padf/kit", source_root=src)
            self.assertIn("profile", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
