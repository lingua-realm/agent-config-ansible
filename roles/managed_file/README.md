# managed_file

管理单个目标文件：先将模板、源文件或直接提供的内容生成到远端临时路径，再进行差异比较、差异预览、可选备份和可选确认，最后按需覆盖目标文件。

这个 role 默认处理普通文本文件。只有在 `managed_file_compare_kind: json_sorted` 时，才会把 JSON 内容按键排序后再比较，以避免仅因键顺序不同而误判为变更。

## 变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `managed_file_display_name` | ❌ | `managed file` | 可读名称，用于日志输出 |
| `managed_file_dest` | ✅ | `""` | 目标文件路径 |
| `managed_file_temp_path` | ❌ | `/tmp/managed-file-...` | 渲染或复制后的远端临时文件路径 |
| `managed_file_template_src` | 三选一 | 未定义 | 模板源文件路径 |
| `managed_file_copy_src` | 三选一 | 未定义 | 原样复制的源文件路径 |
| `managed_file_content` | 三选一 | 未定义 | 直接写入目标文件的内容 |
| `managed_file_mode` | ❌ | `0644` | 最终文件权限 |
| `managed_file_compare_kind` | ❌ | `plain` | 比较策略：`plain` 或 `json_sorted` |
| `managed_file_backup` | ❌ | `true` | 覆盖前是否创建备份 |
| `managed_file_backup_dir` | ❌ | 目标目录下的 `.managed_file_backups` | 备份目录 |
| `managed_file_backup_prefix` | ❌ | 目标文件名 | 备份文件名前缀 |
| `managed_file_confirm` | ❌ | `false` | 检测到变更时是否交互确认 |
| `managed_file_skip_confirm` | ❌ | `false` | 强制跳过交互确认；适用于非交互执行 |
| `managed_file_cleanup_temp` | ❌ | `true` | 任务结束后是否删除远端临时文件 |

## 输出

role 执行完成后会写入 `managed_file_result`：

```yaml
managed_file_result:
  changed: true
  created: false
  backup_path: /path/to/.managed_file_backups/app.conf.20260312_120000
  compare_kind: plain
  diff: |
    --- old
    +++ new
```

## 示例

```yaml
- hosts: all
  tasks:
    - name: 管理配置文件
      include_role:
        name: managed_file
      vars:
        managed_file_display_name: Agent 配置
        managed_file_dest: ~/.config/agent/config.json
        managed_file_temp_path: /tmp/agent-config.json.rendered
        managed_file_template_src: "{{ playbook_dir }}/templates/config.json.j2"
        managed_file_compare_kind: json_sorted
        managed_file_backup: true
        managed_file_confirm: true
```

## 说明

- `plain` 会直接比较目标文件和临时文件。
- `json_sorted` 会先把 JSON 解析并按 key 排序后再比较，但只有检测到语义差异时才会覆盖目标文件。
- `managed_file_template_src`、`managed_file_copy_src` 和 `managed_file_content` 必须三选一，不能同时提供多个，也不能全部省略。
- `managed_file_confirm: true` 时会直接使用 `pause` 等待用户输入确认；如果是无人值守执行，请显式设置 `managed_file_skip_confirm: true` 或关闭确认。
