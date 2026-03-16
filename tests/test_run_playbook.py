import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run-playbook.sh"


class RunPlaybookScriptTests(unittest.TestCase):
    def run_script(self, *args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)

        return subprocess.run(
            ["bash", str(SCRIPT_PATH), *args],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
        )

    def test_requires_profile_and_playbook_arguments(self) -> None:
        result = self.run_script()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("用法", result.stderr)

    def test_rejects_missing_profile_inventory(self) -> None:
        result = self.run_script("missing-profile", "playbooks/setup_codex.yml")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inventory/missing-profile/inventory.yml", result.stderr)

    def test_rejects_absolute_playbook_path(self) -> None:
        result = self.run_script("default", str(REPO_ROOT / "playbooks" / "setup_codex.yml"))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("相对路径", result.stderr)

    def test_uses_profile_inventory_and_forwards_extra_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            capture_inventory = tmp_path / "inventory.txt"
            capture_args = tmp_path / "args.bin"

            fake_uv = fake_bin / "uv"
            fake_uv.write_text(
                "#!/usr/bin/env bash\n"
                "printf '%s' \"$ANSIBLE_INVENTORY\" > \"$UV_CAPTURE_INVENTORY\"\n"
                "printf '%s\\0' \"$@\" > \"$UV_CAPTURE_ARGS\"\n",
                encoding="utf-8",
            )
            fake_uv.chmod(fake_uv.stat().st_mode | stat.S_IXUSR)

            result = self.run_script(
                "default",
                "playbooks/setup_codex.yml",
                "-e",
                "target_hosts=all",
                extra_env={
                    "PATH": f"{fake_bin}:{os.environ['PATH']}",
                    "UV_CAPTURE_INVENTORY": str(capture_inventory),
                    "UV_CAPTURE_ARGS": str(capture_args),
                },
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(
                capture_inventory.read_text(encoding="utf-8"),
                str(REPO_ROOT / "inventory" / "default" / "inventory.yml"),
            )

            args = [
                part.decode("utf-8")
                for part in capture_args.read_bytes().rstrip(b"\0").split(b"\0")
            ]
            self.assertEqual(
                args,
                [
                    "run",
                    "ansible-playbook",
                    "playbooks/setup_codex.yml",
                    "-e",
                    "target_hosts=all",
                ],
            )


if __name__ == "__main__":
    unittest.main()
