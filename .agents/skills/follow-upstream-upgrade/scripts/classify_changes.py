#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path


def classify_change(file_path: str) -> dict[str, str]:
    """
    分类变更类型：结构性（structural）vs 内容性（content）
    规则：
    - 如果是 inventory/default/group_vars/all/ 下的 .yml 文件 → 可能需要检查 schema 变更
    - 其他文件默认为内容/文档变更
    """
    path = Path(file_path)

    # 检查是否是 inventory/default/group_vars/all/ 下的配置文件
    if path.parts[:3] == ['inventory', 'default', 'group_vars'] and path.suffix in {'.yml', '.yaml'}:
        # 这是一个配置模板文件，可能包含结构变更
        return {
            "file": file_path,
            "category": "config_schema",
            "impact": "may_require_migration"
        }
    elif path in {"README.md", "AGENTS.md", "CLAUDE.md"} or str(path).startswith("docs/"):
        return {
            "file": file_path,
            "category": "docs",
            "impact": "informational"
        }
    else:
        return {
            "file": file_path,
            "category": "content",
            "impact": "informational"
        }


def main(argv: list[str]) -> int:
    """
    用法: classify_changes.py <output_dir> <payload.json>
    从上游 JSON 的 changed_files 列表，添加分类信息
    """
    if len(argv) != 3:
        raise SystemExit("Usage: classify_changes.py <output_dir> <payload.json>")

    output_dir = Path(argv[1])
    payload_path = Path(argv[2])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    changed_files = payload.get("changed_files", [])
    classifications = [classify_change(f) for f in changed_files]

    # 更新 payload
    payload["change_classifications"] = classifications

    # 统计
    schema_files = [c for c in classifications if c["category"] == "config_schema"]
    payload["has_schema_changes"] = len(schema_files) > 0
    payload["schema_change_count"] = len(schema_files)

    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
