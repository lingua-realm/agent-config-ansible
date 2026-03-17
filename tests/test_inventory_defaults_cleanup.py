import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ANSIBLE_PLAYBOOK = REPO_ROOT / ".venv" / "bin" / "ansible-playbook"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


class InventoryDefaultsStructureTests(unittest.TestCase):
    def test_backup_example_files_are_removed(self) -> None:
        for relative_path in [
            "inventory/default/group_vars/all/claude_code/backup.yml",
            "inventory/default/group_vars/all/codex/backup.yml",
            "inventory/default/group_vars/all/gemini_cli/backup.yml",
            "inventory/default/group_vars/all/copilot_cli/backup.yml",
            "inventory/default/group_vars/all/cursor/backup.yml",
        ]:
            self.assertFalse((REPO_ROOT / relative_path).exists(), msg=relative_path)

    def test_codex_settings_only_contains_payload_fields(self) -> None:
        text = (REPO_ROOT / "inventory/default/group_vars/all/codex/settings.yml").read_text(encoding="utf-8")

        self.assertNotIn("confirm_codex_config_update", text)
        self.assertNotIn("confirm_codex_env_update", text)

    def test_claude_payload_files_do_not_mix_confirm_controls(self) -> None:
        settings_text = (REPO_ROOT / "inventory/default/group_vars/all/claude_code/settings.yml").read_text(encoding="utf-8")
        user_json_text = (REPO_ROOT / "inventory/default/group_vars/all/claude_code/mcp_servers.yml").read_text(encoding="utf-8")

        self.assertNotIn("confirm_settings_update", settings_text)
        self.assertNotIn("confirm_claude_json_update", user_json_text)

    def test_gemini_settings_do_not_repeat_runtime_control_vars(self) -> None:
        text = (REPO_ROOT / "inventory/default/group_vars/all/gemini_cli/settings.yml").read_text(encoding="utf-8")

        for needle in [
            "gemini_confirm_settings_update",
            "gemini_confirm_env_update",
            "gemini_require_cli",
            "gemini_auto_install_npm",
            "gemini_manage_settings",
            "gemini_manage_env",
            "gemini_manage_gemini_md",
            "gemini_run_verify",
        ]:
            self.assertNotIn(needle, text, msg=needle)

    def test_copilot_settings_do_not_repeat_runtime_control_vars(self) -> None:
        text = (REPO_ROOT / "inventory/default/group_vars/all/copilot_cli/settings.yml").read_text(encoding="utf-8")

        for needle in [
            "copilot_cli_confirm_mcp_config_update",
            "copilot_cli_require_cli",
            "copilot_cli_auto_install_npm",
            "copilot_cli_manage_mcp_config",
            "copilot_cli_run_verify",
        ]:
            self.assertNotIn(needle, text, msg=needle)

    def test_cursor_settings_do_not_repeat_runtime_control_vars(self) -> None:
        text = (REPO_ROOT / "inventory/default/group_vars/all/cursor/settings.yml").read_text(encoding="utf-8")

        for needle in [
            "cursor_confirm_mcp_config_update",
            "cursor_require_agent_cli",
            "cursor_manage_mcp_config",
            "cursor_run_verify",
        ]:
            self.assertNotIn(needle, text, msg=needle)


class MinimalInventoryPlaybookTests(unittest.TestCase):
    maxDiff = None

    def run_playbook(
        self,
        inventory_dir: Path,
        playbook: str,
        extra_args: list[str] | None = None,
        home_dir: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if home_dir is not None:
            env["HOME"] = str(home_dir)
        env["ANSIBLE_FORKS"] = "1"

        return subprocess.run(
            [
                str(ANSIBLE_PLAYBOOK),
                "-i",
                str(inventory_dir / "inventory.yml"),
                "--syntax-check",
                playbook,
                *(extra_args or []),
            ],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
        )

    def create_inventory(self, root: Path) -> Path:
        inventory_dir = root / "inventory" / "minimal"
        write_text(
            inventory_dir / "inventory.yml",
            f"""
            all:
              hosts:
                localhost:
                  ansible_connection: local
                  ansible_python_interpreter: "{REPO_ROOT}/.venv/bin/python3"
            """,
        )
        return inventory_dir

    def test_codex_playbook_runs_with_minimal_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            home_dir = root / "home"
            inventory_dir = self.create_inventory(root)

            write_text(
                inventory_dir / "group_vars/all/codex/settings.yml",
                """
                codex_settings:
                  sandbox_mode: "read-only"
                """,
            )
            write_text(
                inventory_dir / "group_vars/all/codex/models.yml",
                """
                codex_model_configs:
                  test_model:
                    model_provider: "dummy"
                    model: "dummy-model"
                    providers: {}
                    env: {}
                codex_use_model: "test_model"
                """,
            )

            result = self.run_playbook(
                inventory_dir,
                "playbooks/setup_codex.yml",
                [
                    "-e",
                    "codex_require_codex_cli=false",
                    "-e",
                    "codex_run_verify=false",
                ],
                home_dir=home_dir,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("playbook: playbooks/setup_codex.yml", result.stdout)

    def test_claude_playbook_runs_without_nested_confirm_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            home_dir = root / "home"
            inventory_dir = self.create_inventory(root)

            write_text(
                inventory_dir / "group_vars/all/claude_code/settings.yml",
                """
                claude_code_settings:
                  model: "opus"
                  alwaysThinkingEnabled: false
                  env:
                    ANTHROPIC_BASE_URL: "{{ model_configs[claude_code_use_model].baseURL }}"
                    ANTHROPIC_API_KEY: "{{ model_configs[claude_code_use_model].api_key }}"
                    ANTHROPIC_DEFAULT_OPUS_MODEL: "{{ model_configs[claude_code_use_model].opus_model }}"
                    ANTHROPIC_DEFAULT_SONNET_MODEL: "{{ model_configs[claude_code_use_model].sonnet_model }}"
                    ANTHROPIC_DEFAULT_HAIKU_MODEL: "{{ model_configs[claude_code_use_model].haiku_model }}"
                    CLAUDE_CODE_SUBAGENT_MODEL: "{{ model_configs[claude_code_use_model].claude_code_subagent }}"
                  outputStyle: "engineer-professional.md"
                  language: "zh-CN"
                  permissions:
                    defaultMode: "default"
                    allow: []
                    deny: []
                  hooks: {}
                  enabled_plugins: []
                """,
            )
            write_text(
                inventory_dir / "group_vars/all/claude_code/models.yml",
                """
                claude_code_model_configs:
                  test_model:
                    baseURL: "https://example.invalid"
                    api_key: ""
                    opus_model: "test-opus"
                    sonnet_model: "test-sonnet"
                    haiku_model: "test-haiku"
                    claude_code_subagent: "test-subagent"
                claude_code_use_model: "test_model"
                """,
            )
            write_text(
                inventory_dir / "group_vars/all/claude_code/mcp_servers.yml",
                """
                claude_code_dot_claude_json_merge:
                  mcpServers: {}
                """,
            )

            result = self.run_playbook(
                inventory_dir,
                "playbooks/setup_claude_code.yml",
                [
                    "-e",
                    "claude_code_require_claude_cli=false",
                    "-e",
                    "claude_code_manage_plugins=false",
                    "-e",
                    "claude_code_run_verify=false",
                ],
                home_dir=home_dir,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("playbook: playbooks/setup_claude_code.yml", result.stdout)

    def test_gemini_playbook_runs_with_minimal_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            home_dir = root / "home"
            inventory_dir = self.create_inventory(root)

            write_text(
                inventory_dir / "group_vars/all/gemini_cli/settings.yml",
                """
                gemini_settings:
                  general:
                    preferredEditor: vim
                """,
            )
            write_text(
                inventory_dir / "group_vars/all/gemini_cli/models.yml",
                """
                gemini_model_configs:
                  test_model:
                    model:
                      name: "gemini-test"
                    modelConfigs: {}
                    env: {}
                gemini_use_model: "test_model"
                """,
            )

            result = self.run_playbook(
                inventory_dir,
                "playbooks/setup_gemini_cli.yml",
                [
                    "-e",
                    "gemini_require_cli=false",
                    "-e",
                    "gemini_run_verify=false",
                ],
                home_dir=home_dir,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("playbook: playbooks/setup_gemini_cli.yml", result.stdout)


if __name__ == "__main__":
    unittest.main()
