#!/usr/bin/env python3
"""Tests for the utv-close Contract verb. Run: python3 padf/harness/scripts/test_utv_close.py"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from utv_close import UtvCloseError, close


SPEC = """---
id: UTV-001
slug: example
title: Example
status: ready
level: LIGHT
intent_trace: docs/charter.md
oracle: none
migration: none
deps: none
issue: 68       # GitHub mirror; consumes intake #34, #35, #52
---

# UTV-001 — Example
"""

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
}


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, env=GIT_ENV, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def commit_all(root: Path, msg: str) -> str:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)
    return git(root, "rev-parse", "HEAD")


def write_review(root: Path, verdict: str, head: str | None, attempt: int = 1) -> None:
    head_line = f"- **Head:** `{head}`\n" if head else ""
    (root / f"padf/evidence/REVIEW-UTV-001-attempt{attempt}.md").write_text(
        f"# REVIEW-UTV-001 — attempt {attempt}\n\n{head_line}\n## VERDICT: {verdict}\n",
        encoding="utf-8",
    )


def make_tree(
    tmp: Path, *, spec: str = SPEC, with_plan: bool = True, verdict: str | None = "GREEN-recommend"
) -> Path:
    """main has the spec + queue; utv/001 adds product code; R4 reviewed that commit."""
    specs = tmp / "padf" / "specs"
    work = tmp / "padf" / "work"
    (specs / "_archive").mkdir(parents=True)
    work.mkdir(parents=True)
    (tmp / "padf" / "evidence").mkdir(parents=True)
    spec_path = specs / "UTV-001-example.md"
    spec_path.write_text(spec, encoding="utf-8")
    if with_plan:
        (specs / "UTV-001.plan.md").write_text("# plan\n", encoding="utf-8")
    (work / "feature_list.json").write_text(
        json.dumps(
            {
                "updated": "2026-01-01",
                "items": [
                    {
                        "id": "UTV-001",
                        "status": "ready",
                        "spec": "padf/specs/UTV-001-example.md",
                        "issue": 68,
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp / "README.md").write_text("base\n", encoding="utf-8")
    git(tmp, "init", "-q", "-b", "main")
    commit_all(tmp, "base")
    git(tmp, "checkout", "-q", "-b", "utv/001-example")
    (tmp / "app.py").write_text("x = 1\n", encoding="utf-8")
    product = commit_all(tmp, "product")
    if verdict is not None:
        write_review(tmp, verdict, product)
        commit_all(tmp, "review")
    return spec_path


class UtvCloseTests(unittest.TestCase):
    def test_happy_path_archives_and_marks_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root)
            issues = close(spec)
            archived = root / "padf/specs/_archive/UTV-001-example.md"
            self.assertTrue(archived.is_file())
            self.assertFalse(spec.exists())
            self.assertTrue((root / "padf/specs/_archive/UTV-001.plan.md").is_file())
            self.assertFalse((root / "padf/specs/UTV-001.plan.md").exists())
            body = archived.read_text(encoding="utf-8")
            self.assertRegex(body, r"(?m)^status: done$")
            self.assertIn("## Close-out", body)
            self.assertIn("verdict GREEN-recommend", body)
            queue = json.loads((root / "padf/work/feature_list.json").read_text())
            item = queue["items"][0]
            self.assertEqual(item["status"], "done")
            self.assertEqual(item["spec"], "padf/specs/_archive/UTV-001-example.md")
            self.assertEqual(issues, [68, 34, 35, 52])

    def test_missing_file_fails(self) -> None:
        with self.assertRaises(UtvCloseError) as ctx:
            close(Path("/no/such/UTV-001-example.md"))
        self.assertIn("not a file", str(ctx.exception))

    def test_already_archived_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root)
            dest = root / "padf/specs/_archive/UTV-001-example.md"
            spec.rename(dest)
            with self.assertRaises(UtvCloseError) as ctx:
                close(dest)
            self.assertIn("archive", str(ctx.exception).lower())

    def test_missing_queue_item_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root)
            (root / "padf/work/feature_list.json").write_text(
                json.dumps({"updated": "2026-01-01", "items": []}) + "\n"
            )
            with self.assertRaises(UtvCloseError) as ctx:
                close(spec)
            self.assertIn("feature_list", str(ctx.exception))

    def test_refuses_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = make_tree(Path(tmp))
            template = spec.with_name("_template.md")
            spec.rename(template)
            with self.assertRaises(UtvCloseError) as ctx:
                close(template)
            self.assertIn("template", str(ctx.exception).lower())


class ReviewGateTests(unittest.TestCase):
    def assert_refused(self, spec: Path, needle: str, override: str | None = None) -> None:
        with self.assertRaises(UtvCloseError) as ctx:
            close(spec, override)
        self.assertIn(needle, str(ctx.exception))
        self.assertTrue(spec.exists(), "a refused close-out must change nothing")

    def test_no_review_is_not_a_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = make_tree(Path(tmp), verdict=None)
            self.assert_refused(spec, "R4 has not reviewed")

    def test_amber_needs_owner_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root, verdict="AMBER")
            self.assert_refused(spec, "verdict is AMBER")
            close(spec, "owner accepts REV-2 as follow-up issue #99")
            body = (root / "padf/specs/_archive/UTV-001-example.md").read_text()
            self.assertIn("owner override: owner accepts REV-2", body)

    def test_abstain_blocks_green(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec = make_tree(Path(tmp), verdict="ABSTAIN")
            self.assert_refused(spec, "verdict is ABSTAIN")

    def test_latest_attempt_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root)
            write_review(root, "AMBER", git(root, "rev-parse", "HEAD"), attempt=2)
            commit_all(root, "review 2")
            self.assert_refused(spec, "REVIEW-UTV-001-attempt2.md verdict is AMBER")

    def test_review_without_head_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root)
            write_review(root, "GREEN-recommend", None)
            commit_all(root, "review without head")
            self.assert_refused(spec, "must record the commit it reviewed")

    def test_product_change_after_review_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root)
            (root / "app.py").write_text("x = 2  # 'fix lint'\n", encoding="utf-8")
            commit_all(root, "post-review change")
            self.assert_refused(spec, "changed since R4 reviewed")
            # the owner cannot wave a stale review through either
            self.assert_refused(spec, "changed since R4 reviewed", "looks fine")

    def test_new_file_after_review_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root)
            (root / "extra.py").write_text("y = 1\n", encoding="utf-8")
            commit_all(root, "sneaky new file")
            self.assert_refused(spec, "extra.py")

    def test_closeout_paths_may_move_after_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root)
            spec.write_text(SPEC + "\nHALT answer written by owner.\n", encoding="utf-8")
            commit_all(root, "owner answers HALT in spec")
            close(spec)

    def test_main_merged_in_after_review_is_fine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root)
            git(root, "checkout", "-q", "main")
            (root / "other.py").write_text("z = 1\n", encoding="utf-8")
            commit_all(root, "unrelated work on main")
            git(root, "checkout", "-q", "utv/001-example")
            git(root, "merge", "-q", "--no-edit", "main")
            close(spec)

    def test_house_format_variants_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root, verdict=None)
            head = git(root, "rev-parse", "HEAD")
            (root / "padf/evidence/REVIEW-UTV-001-attempt1.md").write_text(
                "# REVIEW-UTV-001 — attempt 1\n\n"
                f"- **PR:** https://x/pull/1 · branch `utv/001` · head `{head}` (= worktree HEAD)\n\n"
                "## Verdict\n\n**GREEN-recommend.** Nothing blocking found.\n",
                encoding="utf-8",
            )
            commit_all(root, "house-format review")
            close(spec)

    def test_rewritten_history_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = make_tree(root)
            write_review(root, "GREEN-recommend", "0" * 40)
            commit_all(root, "review of a commit that is not here")
            self.assert_refused(spec, "failed")


if __name__ == "__main__":
    unittest.main()
