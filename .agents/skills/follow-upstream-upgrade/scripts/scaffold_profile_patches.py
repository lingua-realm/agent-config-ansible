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
        raise SystemExit("Usage: scaffold_profile_patches.py <output_dir> <payload.json>")

    output_dir = Path(argv[1])
    payload_path = Path(argv[2])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    template_path = Path(__file__).resolve().parents[1] / "templates" / "profile-patch.md.j2"
    template_text = template_path.read_text(encoding="utf-8")

    has_schema = payload.get("has_schema_changes", False)
    schema_changes = payload.get("schema_changes", [])
    profiles = payload.get("profiles", [])

    generated_profiles: list[str] = []

    # 只有存在结构性变更时，才生成 profile patch
    if has_schema and schema_changes:
        for profile in profiles:
            profile_name = profile["name"]
            profile_dir = output_dir / "profiles" / profile_name
            profile_dir.mkdir(parents=True, exist_ok=True)

            # 构建针对该 profile 的迁移建议（仅基于结构化变更）
            summary = f"上游模板有 {len(schema_changes)} 处结构变更，请检查以下文件并同步：\n"
            for change in schema_changes:
                summary += f"- {change['file']}: {change.get('note', '结构更新')}\n"
            summary += "\n注意：仅当您的 profile 覆盖了这些配置才需要迁移。不要直接覆盖个性化配置。"

            notes = "此补丁仅提示结构变更，不包含具体 diff。请对比 inventory/default/ 与您的 profile 目录。"

            rendered = render_template(
                template_text,
                {
                    "profile": profile_name,
                    "summary": summary,
                    "suggested_changes": "见上方概要（请人工评审）",
                    "notes": notes,
                },
            )
            draft_path = profile_dir / "patch-draft.md"
            draft_path.write_text(rendered, encoding="utf-8")
            generated_profiles.append(profile_name)
    else:
        # 无结构变更，不生成任何 profile patch
        (output_dir / "no-schema-changes.txt").write_text(
            "未检测到结构性配置变更，无需生成 profile 补丁。\n"
            "注意：inventory/<profile>/ 与 inventory/default/ 的内容差异属于用户个性化，不会在此报告中出现。",
            encoding="utf-8"
        )

    print(
        json.dumps(
            {
                "generated_profiles": generated_profiles,
                "output_dir": str(output_dir),
                "has_schema_changes": has_schema,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
