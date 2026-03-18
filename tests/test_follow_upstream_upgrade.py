import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills" / "follow-upstream-upgrade"
SKILL_FILE = SKILL_ROOT / "SKILL.md"
REPO_RULES_FILE = SKILL_ROOT / "references" / "repo-rules.md"
PROFILE_PATCH_TEMPLATE = SKILL_ROOT / "templates" / "profile-patch.md.j2"
UPGRADE_REPORT_TEMPLATE = SKILL_ROOT / "templates" / "upgrade-report.md.j2"
DISCOVER_PROFILES_SCRIPT = SKILL_ROOT / "scripts" / "discover_profiles.sh"
INSPECT_GIT_STATE_SCRIPT = SKILL_ROOT / "scripts" / "inspect_git_state.sh"
COLLECT_UPSTREAM_DIFF_SCRIPT = SKILL_ROOT / "scripts" / "collect_upstream_diff.sh"
DETECT_IMPACTED_TOOLS_SCRIPT = SKILL_ROOT / "scripts" / "detect_impacted_tools.py"
SCAFFOLD_PROFILE_PATCHES_SCRIPT = SKILL_ROOT / "scripts" / "scaffold_profile_patches.py"
WRITE_UPGRADE_REPORT_SCRIPT = SKILL_ROOT / "scripts" / "write_upgrade_report.py"
CLAUDE_SKILLS_LINK = REPO_ROOT / ".claude" / "skills"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


class FollowUpstreamUpgradeSkillSkeletonTests(unittest.TestCase):
    def test_follow_upstream_upgrade_skill_files_exist(self) -> None:
        for path in [
            SKILL_FILE,
            REPO_RULES_FILE,
            PROFILE_PATCH_TEMPLATE,
            UPGRADE_REPORT_TEMPLATE,
        ]:
            self.assertTrue(path.exists(), msg=str(path))

    def test_skill_frontmatter_uses_expected_name_and_trigger_description(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")

        self.assertIn("name: follow-upstream-upgrade", text)
        self.assertIn(
            "description: Use when working in this repository and the user asks to sync upstream changes into private-config",
            text,
        )
        self.assertIn("## Hard Boundaries", text)


class FollowUpstreamUpgradeScriptTests(unittest.TestCase):
    def run_script(self, script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(script), *args],
            cwd=cwd or REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": "Test User",
                "GIT_AUTHOR_EMAIL": "test@example.com",
                "GIT_COMMITTER_NAME": "Test User",
                "GIT_COMMITTER_EMAIL": "test@example.com",
            }
        )
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def create_git_repo(self, root: Path) -> Path:
        repo = root / "repo"
        repo.mkdir()
        self.assertEqual(self.git(repo, "init", "-b", "private-config").returncode, 0)
        write_text(repo / "README.md", "# fixture\n")
        self.assertEqual(self.git(repo, "add", "README.md").returncode, 0)
        self.assertEqual(self.git(repo, "commit", "-m", "init").returncode, 0)
        self.assertEqual(self.git(repo, "remote", "add", "upstream", "https://example.invalid/upstream.git").returncode, 0)
        return repo

    def create_upgrade_fixture(self, root: Path, conflict: bool = False) -> Path:
        upstream_bare = root / "upstream.git"
        seed_repo = root / "seed"
        upstream_work = root / "upstream-work"
        repo = root / "repo"

        self.assertEqual(self.git(root, "init", "--bare", str(upstream_bare)).returncode, 0)

        seed_repo.mkdir()
        self.assertEqual(self.git(seed_repo, "init", "-b", "main").returncode, 0)
        write_text(seed_repo / "shared.txt", "base\n")
        self.assertEqual(self.git(seed_repo, "add", "shared.txt").returncode, 0)
        self.assertEqual(self.git(seed_repo, "commit", "-m", "base").returncode, 0)
        self.assertEqual(self.git(seed_repo, "remote", "add", "origin", str(upstream_bare)).returncode, 0)
        self.assertEqual(self.git(seed_repo, "push", "-u", "origin", "main").returncode, 0)

        self.assertEqual(self.git(root, "clone", str(upstream_bare), str(repo)).returncode, 0)
        self.assertEqual(self.git(repo, "checkout", "-B", "main", "origin/main").returncode, 0)
        self.assertEqual(self.git(repo, "checkout", "-b", "private-config").returncode, 0)
        self.assertEqual(self.git(repo, "remote", "rename", "origin", "upstream").returncode, 0)

        if conflict:
            write_text(repo / "shared.txt", "local change\n")
            self.assertEqual(self.git(repo, "add", "shared.txt").returncode, 0)
            self.assertEqual(self.git(repo, "commit", "-m", "local change").returncode, 0)

        self.assertEqual(self.git(root, "clone", str(upstream_bare), str(upstream_work)).returncode, 0)
        self.assertEqual(self.git(upstream_work, "checkout", "-B", "main", "origin/main").returncode, 0)
        if conflict:
            write_text(upstream_work / "shared.txt", "upstream change\n")
        else:
            write_text(upstream_work / "upstream.txt", "new file\n")
        self.assertEqual(self.git(upstream_work, "add", ".").returncode, 0)
        self.assertEqual(self.git(upstream_work, "commit", "-m", "upstream change").returncode, 0)
        self.assertEqual(self.git(upstream_work, "push", "origin", "main").returncode, 0)

        return repo

    def test_discover_profiles_excludes_default_and_returns_sorted_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            for profile in ["default", "work", "personal"]:
                write_text(root / "inventory" / profile / "inventory.yml", "all:\n  hosts: {}\n")

            result = self.run_script(DISCOVER_PROFILES_SCRIPT, str(root))

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["profiles"], ["personal", "work"])

    def test_inspect_git_state_reports_clean_repository_as_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = self.create_git_repo(Path(tmp_dir))

            result = self.run_script(
                INSPECT_GIT_STATE_SCRIPT,
                str(repo),
                "upstream",
                "private-config",
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["current_branch"], "private-config")

    def test_inspect_git_state_fails_on_dirty_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = self.create_git_repo(Path(tmp_dir))
            write_text(repo / "dirty.txt", "dirty\n")

            result = self.run_script(
                INSPECT_GIT_STATE_SCRIPT,
                str(repo),
                "upstream",
                "private-config",
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["reason"], "dirty_worktree")

    def test_inspect_git_state_fails_without_upstream_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = self.create_git_repo(Path(tmp_dir))
            self.assertEqual(self.git(repo, "remote", "remove", "upstream").returncode, 0)

            result = self.run_script(
                INSPECT_GIT_STATE_SCRIPT,
                str(repo),
                "upstream",
                "private-config",
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["reason"], "missing_remote")

    def test_inspect_git_state_fails_without_target_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = self.create_git_repo(Path(tmp_dir))
            self.assertEqual(self.git(repo, "branch", "-M", "other-branch").returncode, 0)

            result = self.run_script(
                INSPECT_GIT_STATE_SCRIPT,
                str(repo),
                "upstream",
                "private-config",
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["reason"], "missing_target_branch")

    def test_collect_upstream_diff_creates_upgrade_branch_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            repo = self.create_upgrade_fixture(root)
            output_dir = root / "out"

            result = self.run_script(
                COLLECT_UPSTREAM_DIFF_SCRIPT,
                str(repo),
                "upstream",
                "main",
                "private-config",
                "upgrade/2026-03-18-upstream-sync",
                str(output_dir),
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["upgrade_branch"], "upgrade/2026-03-18-upstream-sync")
            self.assertIn("upstream.txt", payload["changed_files"])
            self.assertTrue((output_dir / "git-summary.json").exists())
            self.assertEqual(payload["target_head_after"], payload["target_head"])
            current_branch = self.git(repo, "branch", "--show-current").stdout.strip()
            self.assertEqual(current_branch, "upgrade/2026-03-18-upstream-sync")
            self.assertEqual(
                self.git(repo, "rev-parse", "private-config").stdout.strip(),
                payload["target_head"],
            )

    def test_collect_upstream_diff_reports_merge_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            repo = self.create_upgrade_fixture(root, conflict=True)
            output_dir = root / "out"

            result = self.run_script(
                COLLECT_UPSTREAM_DIFF_SCRIPT,
                str(repo),
                "upstream",
                "main",
                "private-config",
                "upgrade/2026-03-18-upstream-sync",
                str(output_dir),
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["reason"], "merge_conflict")
            self.assertTrue((output_dir / "git-summary.json").exists())
            self.assertEqual(payload["target_head_after"], payload["target_head"])

    def test_detect_impacted_tools_marks_docs_only_changes(self) -> None:
        result = subprocess.run(
            [
                str(REPO_ROOT / ".venv" / "bin" / "python"),
                str(DETECT_IMPACTED_TOOLS_SCRIPT),
                "README.md",
                "AGENTS.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["documentation_only"])
        self.assertEqual(payload["impacted_tools"], [])

    def test_detect_impacted_tools_maps_playbook_role_shared_mcp_and_assets(self) -> None:
        result = subprocess.run(
            [
                str(REPO_ROOT / ".venv" / "bin" / "python"),
                str(DETECT_IMPACTED_TOOLS_SCRIPT),
                "playbooks/setup_codex.yml",
                "roles/agent_cursor/tasks/main.yml",
                "inventory/default/group_vars/all/agent_mcps/servers.yml",
                "inventory/default/codex_assets/AGENTS.md",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["documentation_only"])
        self.assertIn("codex", payload["impacted_tools"])
        self.assertIn("cursor", payload["impacted_tools"])
        self.assertIn("claude_code", payload["impacted_tools"])
        self.assertIn("gemini_cli", payload["impacted_tools"])
        self.assertIn("copilot_cli", payload["impacted_tools"])
        self.assertIn("playbooks/setup_codex.yml", payload["impacted_playbooks"])
        self.assertIn("playbooks/setup_cursor.yml", payload["impacted_playbooks"])

    def test_scaffold_profile_patches_creates_drafts_without_modifying_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            profile_file = root / "inventory" / "work" / "group_vars" / "all" / "codex" / "settings.yml"
            write_text(profile_file, "codex_settings:\n  sandbox_mode: read-only\n")
            output_dir = root / "out"
            payload_path = root / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "profiles": [
                            {
                                "name": "work",
                                "summary": "需要同步 codex 默认值",
                                "suggested_changes": "- 更新 `codex_settings`\n- 复核 `codex_assets/AGENTS.md`",
                                "notes": "先人工确认后再修改。",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            original_text = profile_file.read_text(encoding="utf-8")

            result = subprocess.run(
                [
                    str(REPO_ROOT / ".venv" / "bin" / "python"),
                    str(SCAFFOLD_PROFILE_PATCHES_SCRIPT),
                    str(output_dir),
                    str(payload_path),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            patch_draft = output_dir / "profiles" / "work" / "patch-draft.md"
            self.assertTrue(patch_draft.exists())
            self.assertIn("需要同步 codex 默认值", patch_draft.read_text(encoding="utf-8"))
            self.assertEqual(profile_file.read_text(encoding="utf-8"), original_text)
            self.assertEqual(payload["generated_profiles"], ["work"])

    def test_write_upgrade_report_renders_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            output_dir = root / "out"
            payload_path = root / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "summary": "已完成本地升级演练",
                        "impacted_tools": "codex, cursor",
                        "verification": "- syntax-check: passed\n- local apply: passed",
                        "next_steps": "- 审核 patch draft\n- 再决定是否扩大范围",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    str(REPO_ROOT / ".venv" / "bin" / "python"),
                    str(WRITE_UPGRADE_REPORT_SCRIPT),
                    str(output_dir),
                    str(payload_path),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            report_path = output_dir / "upgrade-report.md"
            self.assertTrue(report_path.exists())
            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("已完成本地升级演练", report_text)
            self.assertIn("## Impacted Tools", report_text)
            self.assertIn("## Next Steps", report_text)
            self.assertEqual(payload["report_path"], str(report_path))

    def test_claude_skills_symlink_points_to_agents_skills(self) -> None:
        self.assertTrue(CLAUDE_SKILLS_LINK.is_symlink(), msg=str(CLAUDE_SKILLS_LINK))
        self.assertEqual(os.readlink(CLAUDE_SKILLS_LINK), "../.agents/skills")

    def test_readme_mentions_project_skill_location_and_upgrade_skill(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(".agents/skills/", text)
        self.assertIn("follow-upstream-upgrade", text)

    def test_agents_md_mentions_follow_upstream_upgrade_guardrails(self) -> None:
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn(".agents/skills", text)
        self.assertIn("follow-upstream-upgrade", text)
        self.assertIn("不自动 `commit`", text)


if __name__ == "__main__":
    unittest.main()
