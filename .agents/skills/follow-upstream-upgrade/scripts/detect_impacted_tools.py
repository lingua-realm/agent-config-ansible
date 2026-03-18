#!/usr/bin/env python3

from __future__ import annotations

import json
import sys


TOOL_TO_PLAYBOOK = {
    "claude_code": "playbooks/setup_claude_code.yml",
    "codex": "playbooks/setup_codex.yml",
    "gemini_cli": "playbooks/setup_gemini_cli.yml",
    "copilot_cli": "playbooks/setup_copilot_cli.yml",
    "cursor": "playbooks/setup_cursor.yml",
    "agent_skills": "playbooks/setup_agent_skills.yml",
}

SHARED_MCP_TOOLS = {
    "claude_code",
    "codex",
    "gemini_cli",
    "copilot_cli",
    "cursor",
}

DOCUMENTATION_FILES = {"README.md", "AGENTS.md", "CLAUDE.md"}
DOC_PREFIXES = ("docs/",)
TOOL_PATH_RULES = {
    "claude_code": (
        "playbooks/setup_claude_code.yml",
        "roles/agent_claude_code/",
        "inventory/default/group_vars/all/claude_code/",
        "inventory/default/claude_assets/",
    ),
    "codex": (
        "playbooks/setup_codex.yml",
        "roles/agent_codex/",
        "inventory/default/group_vars/all/codex/",
        "inventory/default/codex_assets/",
    ),
    "gemini_cli": (
        "playbooks/setup_gemini_cli.yml",
        "roles/agent_gemini_cli/",
        "inventory/default/group_vars/all/gemini_cli/",
        "inventory/default/gemini_assets/",
    ),
    "copilot_cli": (
        "playbooks/setup_copilot_cli.yml",
        "roles/agent_copilot_cli/",
        "inventory/default/group_vars/all/copilot_cli/",
    ),
    "cursor": (
        "playbooks/setup_cursor.yml",
        "roles/agent_cursor/",
        "inventory/default/group_vars/all/cursor/",
    ),
    "agent_skills": (
        "playbooks/setup_agent_skills.yml",
        "roles/managed_agent_skills/",
        "inventory/default/group_vars/all/agent_skills/",
        "inventory/default/agent_skills_assets/",
    ),
}


def is_documentation_only(changed_files: list[str]) -> bool:
    for path in changed_files:
        if path in DOCUMENTATION_FILES:
            continue
        if path.startswith(DOC_PREFIXES):
            continue
        return False
    return True


def detect_tools(changed_files: list[str]) -> dict[str, object]:
    impacted_tools: set[str] = set()
    reasons: dict[str, list[str]] = {}

    for path in changed_files:
        matched_tools: set[str] = set()
        if path == "inventory/default/group_vars/all/agent_mcps/servers.yml":
            matched_tools |= SHARED_MCP_TOOLS

        for tool, prefixes in TOOL_PATH_RULES.items():
            if any(path.startswith(prefix) for prefix in prefixes):
                matched_tools.add(tool)

        for tool in matched_tools:
            reasons.setdefault(tool, []).append(path)
            impacted_tools.add(tool)

    impacted_playbooks = sorted({TOOL_TO_PLAYBOOK[tool] for tool in impacted_tools})
    return {
        "documentation_only": is_documentation_only(changed_files),
        "impacted_tools": sorted(impacted_tools),
        "impacted_playbooks": impacted_playbooks,
        "reasons": {tool: sorted(paths) for tool, paths in sorted(reasons.items())},
    }


def main(argv: list[str]) -> int:
    changed_files = argv[1:]
    payload = detect_tools(changed_files)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
