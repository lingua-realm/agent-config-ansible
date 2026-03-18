#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def get_yaml_keys(yaml_content: str) -> set[str]:
    """简单提取 YAML 文件的顶级 key 集合（非完整解析，仅用于结构对比）"""
    keys = set()
    for line in yaml_content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            if ':' in line:
                key = line.split(':', 1)[0].strip()
                if key and not key.startswith('- '):
                    keys.add(key)
    return keys


def has_yaml_changes(base_yaml: str, new_yaml: str) -> list[dict[str, str]]:
    """对比两个 YAML 内容的结构变化，返回变更描述列表"""
    changes = []
    base_keys = get_yaml_keys(base_yaml)
    new_keys = get_yaml_keys(new_yaml)

    added_keys = new_keys - base_keys
    removed_keys = base_keys - new_keys

    for key in added_keys:
        changes.append({
            "type": "key_added",
            "key": key,
            "description": f"新增配置项: {key}"
        })

    for key in removed_keys:
        changes.append({
            "type": "key_removed",
            "key": key,
            "description": f"移除配置项: {key}"
        })

    # 注意：这是一个简化检测。完整检测需要解析 YAML 并对比嵌套结构和类型
    return changes


def main(argv: list[str]) -> int:
    """
    用法: detect_schema_changes.py <repo_root> <output_dir> <base_ref> <new_ref>
    检测 <base_ref>..<new_ref> 之间 inventory/default/ 的结构变更
    """
    if len(argv) != 5:
        raise SystemExit("Usage: detect_schema_changes.py <repo_root> <output_dir> <base_ref> <new_ref>")

    repo_root = Path(argv[1])
    output_dir = Path(argv[2])
    base_ref = argv[3]
    new_ref = argv[4]

    output_dir.mkdir(parents=True, exist_ok=True)

    # 目标路径：inventory/default/group_vars/all/ 下的 yml 文件
    default_vars_dir = repo_root / "inventory" / "default" / "group_vars" / "all"

    if not default_vars_dir.exists():
        print(json.dumps({"schema_changes": []}, ensure_ascii=False))
        return 0

    all_changes = []

    # 遍历所有 .yml 文件
    for yml_file in default_vars_dir.glob("**/*.yml"):
        rel_path = yml_file.relative_to(repo_root)

        # 获取 base_ref 和 new_ref 的文件内容
        base_content = ""
        new_content = ""

        try:
            base_content = subprocess.run(
                ["git", "-C", str(repo_root), "show", f"{base_ref}:{rel_path}"],
                capture_output=True, text=True, check=False
            ).stdout
        except Exception:
            pass

        try:
            new_content = subprocess.run(
                ["git", "-C", str(repo_root), "show", f"{new_ref}:{rel_path}"],
                capture_output=True, text=True, check=False
            ).stdout
        except Exception:
            pass

        if base_content and new_content and base_content != new_content:
            changes = has_yaml_changes(base_content, new_content)
            if changes:
                all_changes.append({
                    "file": str(rel_path),
                    "changes": changes
                })

    result = {"schema_changes": all_changes}
    output_path = output_dir / "schema_changes.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    import subprocess
    raise SystemExit(main(sys.argv))
