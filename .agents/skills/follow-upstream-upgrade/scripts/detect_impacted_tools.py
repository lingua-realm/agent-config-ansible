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


def is_profile_configuration(path: str) -> bool:
    """判断路径是否属于 profile-specific 配置文件（非 default/）"""
    # inventory/ 下的所有配置文件都属于结构关注范围
    # 但我们要区分 default/（模板）和 <profile>/（个性化）
    if path.startswith("inventory/") and path != "inventory/default/":
        parts = path.split("/")
        if len(parts) >= 2 and parts[1] != "default":
            return True
    return False


def detect_schema_changes(changed_files: list[str]) -> dict[str, object]:
    """
    检测上游 default/ 模板的结构性变更，忽略 profile-specific 的内容差异。
    结构性变更是指：inventory/default/group_vars/all/ 下配置文件的schema变化。
    """
    schema_changes = []
    default_config_files = set()

    # 收集 default/ 下的配置变更
    for path in changed_files:
        if path.startswith("inventory/default/group_vars/all/") and path.endswith(".yml"):
            default_config_files.add(path)

    # 简化判断：如果 default/ 的配置变了，就视为有结构变更
    # 完整实现可以diff具体的YAML结构（keys、嵌套等），但此处仅标记文件
    for file in sorted(default_config_files):
        schema_changes.append({
            "file": file,
            "type": "template_updated",
            "note": "上游模板配置已更新，需要检查是否需要迁移到各profile"
        })

    return {
        "has_schema_changes": len(schema_changes) > 0,
        "schema_changes": schema_changes,
        "schema_change_count": len(schema_changes)
    }


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

    # 检测结构性变更（仅限 default/ 模板）
    schema_info = detect_schema_changes(changed_files)

    return {
        "documentation_only": is_documentation_only(changed_files),
        "impacted_tools": sorted(impacted_tools),
        "impacted_playbooks": impacted_playbooks,
        "reasons": {tool: sorted(paths) for tool, paths in sorted(reasons.items())},
        "schema_changes": schema_info["schema_changes"],
        "has_schema_changes": schema_info["has_schema_changes"],
        # 新增：过滤掉 profile-specific 的变更，避免报告内容差异
        "config_changes": [
            path for path in changed_files
            if not is_profile_configuration(path)  # 排除 profile 配置
        ]
    }


def main(argv: list[str]) -> int:
    changed_files = argv[1:]
    payload = detect_tools(changed_files)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
