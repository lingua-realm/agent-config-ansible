# managed_json_merge

将 patch 模板渲染成一个 YAML/JSON 对象，并把它 deep merge 到现有 JSON 文件中。merge 完成后，实际的差异预览、备份、交互确认和落盘逻辑由 managed_file 统一处理。

这个 role 适合“只改部分 JSON key，不想整文件重写”的场景。

## 变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `managed_json_merge_display_name` | ❌ | `managed json merge` | 可读名称，用于日志输出 |
| `managed_json_merge_dest` | ✅ | `""` | 目标 JSON 文件路径 |
| `managed_json_merge_template_src` | ✅ | `""` | patch 模板路径，需渲染为 YAML/JSON 对象 |
| `managed_json_merge_mode` | ❌ | `0644` | 最终文件权限 |
| `managed_json_merge_temp_path` | ❌ | `/tmp/managed-json-merge-...json` | 交给 managed_file 使用的远端临时文件路径 |
| `managed_json_merge_backup` | ❌ | `true` | 覆盖前是否创建备份 |
| `managed_json_merge_backup_dir` | ❌ | 目标目录下的 `.managed_json_merge_backups` | 备份目录 |
| `managed_json_merge_backup_prefix` | ❌ | 目标文件名 | 备份文件名前缀 |
| `managed_json_merge_confirm` | ❌ | `false` | 检测到变更时是否交互确认 |
| `managed_json_merge_skip_confirm` | ❌ | `false` | 强制跳过交互确认 |
| `managed_json_merge_cleanup_temp` | ❌ | `true` | 任务结束后是否删除远端临时文件 |

## 行为说明

- 现有目标文件和 patch 模板都必须解析为 JSON/YAML 对象。
- merge 使用递归对象合并；数组采用 replace 策略，新数组会覆盖旧数组。
- 实际文件管理流程复用 managed_file，因此比较模式固定为 `json_sorted`。
- `managed_json_merge_confirm: true` 时最终会通过 managed_file 的 `pause` 交互确认；非交互执行请配合 `managed_json_merge_skip_confirm: true` 使用。

## 输出

role 执行完成后会写入 `managed_json_merge_result`：

```yaml
managed_json_merge_result:
  changed: true
  created: false
  backup_path: /path/to/.managed_json_merge_backups/config.json.20260312_120000
  compare_kind: json_sorted
  diff: |
    --- old
    +++ new
  merged:
    agent:
      enabled: true
```

## 示例

```yaml
- hosts: all
  tasks:
    - name: 合并 agent 配置 patch
      include_role:
        name: managed_json_merge
      vars:
        managed_json_merge_display_name: Agent JSON Patch
        managed_json_merge_dest: ~/.config/agent/config.json
        managed_json_merge_template_src: "{{ playbook_dir }}/templates/agent-config-patch.yml.j2"
        managed_json_merge_confirm: true
```
