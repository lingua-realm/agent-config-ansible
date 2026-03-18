#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path


def render_template(template_text: str, values: dict[str, str]) -> str:
    rendered = template_text
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", value)
    return rendered


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit("Usage: write_upgrade_report.py <output_dir> <payload.json>")

    output_dir = Path(argv[1])
    payload_path = Path(argv[2])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    output_dir.mkdir(parents=True, exist_ok=True)

    # 只关注 schema 变更和影响工具，过滤掉 profile 配置差异
    has_schema = payload.get("has_schema_changes", False)
    schema_changes = payload.get("schema_changes", [])
    impacted_tools = payload.get("impacted_tools", [])
    impacted_playbooks = payload.get("impacted_playbooks", [])

    # 构建简化的 summary（避免报告内容差异）
    summary_lines = []
    if not has_schema:
        summary_lines.append("✅ 未检测到上游模板的结构性配置变更。")
    else:
        summary_lines.append(f"⚠️  检测到 {len(schema_changes)} 处模板结构变更:")
        for change in schema_changes:
            summary_lines.append(f"  - {change['file']}: {change.get('note', '结构更新')}")

    if impacted_tools:
        summary_lines.append(f"\n🔧 受影响工具: {', '.join(impacted_tools)}")
        summary_lines.append(f"📋 需要验证的 playbooks: {', '.join(impacted_playbooks)}")
    else:
        summary_lines.append("\n✅ 无工具受影响（仅文档或 profile 个性化内容）")

    # 构建 verification 建议（只针对结构变更）
    if has_schema and impacted_tools:
        verification = "建议执行以下命令进行本地验证：\n"
        verification += "```\n"
        for tool in impacted_tools:
            playbook = next((p for t, p in {
                "claude_code": "playbooks/setup_claude_code.yml",
                "codex": "playbooks/setup_codex.yml",
                "gemini_cli": "playbooks/setup_gemini_cli.yml",
                "copilot_cli": "playbooks/setup_copilot_cli.yml",
                "cursor": "playbooks/setup_cursor.yml",
                "agent_skills": "playbooks/setup_agent_skills.yml"
            }.items() if t == tool), None)
            if playbook:
                verification += f"\n# {tool}\n"
                verification += f"scripts/run-playbook.sh <profile> {playbook} -e \"target_hosts=localhost\"\n"
        verification += "```"
    else:
        verification = "无需额外验证（无结构性变更）。"

    # 构建 next_steps
    next_steps = "1. 评审上游结构变更对您的 profile 的影响\n"
    if has_schema:
        next_steps += "2. 如需要，根据模板更新调整您的 profile 覆盖配置\n"
    next_steps += "3. 仅对结构性变更涉及的工具执行本地验证\n"
    next_steps += "4. 注意：profile-specific 配置差异（如 inventory/zzq/）不会在报告中列出，这是预期行为"

    template_path = Path(__file__).resolve().parents[1] / "templates" / "upgrade-report.md.j2"
    template_text = template_path.read_text(encoding="utf-8")

    report_content = render_template(
        template_text,
        {
            "summary": "\n".join(summary_lines),
            "impacted_tools": ", ".join(impacted_tools) if impacted_tools else "无",
            "verification": verification,
            "next_steps": next_steps,
        },
    )

    report_path = output_dir / "upgrade-report.md"
    report_path.write_text(report_content, encoding="utf-8")

    print(json.dumps({"report_path": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
