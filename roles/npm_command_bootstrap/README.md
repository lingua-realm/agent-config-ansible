# npm_command_bootstrap

检查宿主机上**单个**命令行工具是否存在，不存在时可选通过 `npm install -g` 自动安装，并将可用性、路径、版本等信息写入结果字典供后续任务使用。

> 每次调用只处理一个命令。若需要引导多个命令，请在 playbook 中用 `include_role` + `loop` 循环调用本 role。

## 变量

| 变量 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `npm_command_bootstrap_key` | ✅ | `""` | 结果字典中的唯一键 |
| `npm_command_bootstrap_display_name` | ✅ | `""` | 可读名称，用于日志输出 |
| `npm_command_bootstrap_command` | ✅ | `""` | 在 PATH 中检查的可执行文件名 |
| `npm_command_bootstrap_version_command` | ✅ | `""` | 获取版本的完整命令，如 `node --version` |
| `npm_command_bootstrap_auto_install_npm` | ❌ | 未定义 | 若命令不存在，自动执行 `npm install -g` 的包名 |
| `npm_command_bootstrap_required` | ❌ | `true` | 命令不可用时是否终止 play |
| `npm_command_bootstrap_fail_message` | ❌ | 自动生成 | `required=true` 且命令不可用时的错误信息 |
| `npm_command_bootstrap_install_fail_message` | ❌ | 自动生成 | npm 安装后仍不可用时的错误信息 |

## 输出：`npm_command_bootstrap_results`

字典，每次调用追加一条记录：

```yaml
npm_command_bootstrap_results:
  claude:
    available: true          # 是否最终可用
    path: /usr/local/bin/claude
    version: "1.2.3"
    installed_now: false     # 是否本次 play 通过 npm 安装
```

## 示例

```yaml
- hosts: all
  vars:
    my_tools:
      - key: claude
        display_name: Claude Code
        command: claude
        version_command: claude --version
        auto_install_npm: "@anthropic-ai/claude-code"
      - key: prettier
        display_name: Prettier
        command: prettier
        version_command: prettier --version
        auto_install_npm: prettier
        required: false

  tasks:
    - name: 引导 npm 命令行工具
      include_role:
        name: npm_command_bootstrap
      vars:
        npm_command_bootstrap_key: "{{ item.key }}"
        npm_command_bootstrap_display_name: "{{ item.display_name }}"
        npm_command_bootstrap_command: "{{ item.command }}"
        npm_command_bootstrap_version_command: "{{ item.version_command }}"
        npm_command_bootstrap_auto_install_npm: "{{ item.auto_install_npm | default(omit) }}"
        npm_command_bootstrap_required: "{{ item.required | default(true) }}"
      loop: "{{ my_tools }}"

    - name: 仅在 Claude 可用时执行
      command: claude --help
      when: npm_command_bootstrap_results.claude.available
```

