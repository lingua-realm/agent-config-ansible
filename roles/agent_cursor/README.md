# agent_cursor

复用仓库现有基础 role，为 Cursor 执行一套最小但完整的 MCP 自动化配置流程：

- 检查可选的 Cursor Agent CLI（官方命令 `agent`）可用性
- deep merge 并同步 `~/.cursor/mcp.json`
- 验证最终 MCP 配置结果

当前 role 只处理 Cursor 的 MCP 配置，不管理模型、认证或其他 CLI 行为设置。

## 依赖的基础 role

- `npm_command_bootstrap`
- `managed_json_merge`

## 变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `agent_cursor_home_dir` | ❌ | `~/.cursor` | Cursor 配置根目录 |
| `agent_cursor_mcp_config_path` | ❌ | `~/.cursor/mcp.json` | Cursor MCP 配置文件路径 |
| `agent_cursor_temp_root` | ❌ | `/tmp/agent-cursor` | role 工作临时目录 |
| `agent_cursor_require_agent_cli` | ❌ | `true` | 是否要求 Cursor Agent CLI（`agent`）可用 |
| `agent_cursor_manage_mcp_config` | ❌ | `true` | 是否管理 `mcp.json` |
| `agent_cursor_run_verify` | ❌ | `true` | role 末尾是否执行验证任务 |
| `agent_cursor_confirm_mcp_config_update` | ❌ | `false` | `mcp.json` 变更时是否交互确认 |
| `agent_cursor_backup` | ❌ | `true` | 是否为托管文件创建备份 |
| `agent_cursor_backup_root` | ❌ | `""` | 统一备份根目录；设置后会自动派生 `mcp-json/` 子目录 |
| `agent_cursor_mcp_config` | ✅ | 见 defaults | 将被 deep merge 到 `mcp.json` 的对象 |

## `agent_cursor_mcp_config` 结构

```yaml
agent_cursor_mcp_config:
  mcpServers:
    context7:
      command: npx
      args:
        - -y
        - '@upstash/context7-mcp'
      env: {}
    deepwiki:
      url: https://mcp.deepwiki.com/mcp
      headers: {}
```

也可以使用 Cursor 额外支持的字段，例如：

- `disabled: true | false`
- `autoApprove: [tool1, tool2]`
- `cwd`（local/stdio）
- `headers`（http/sse）

## 输出

role 执行完成后会写入 `agent_cursor_result`：

```yaml
agent_cursor_result:
  changed: true
  agent_cli:
    available: true
    path: /usr/local/bin/agent
    version: 1.0.0
  mcp_config:
    changed: true
    path: /home/user/.cursor/mcp.json
```

## 示例

```yaml
- hosts: all
  tasks:
    - name: 配置 Cursor MCP
      include_role:
        name: agent_cursor
      vars:
        agent_cursor_mcp_config:
          mcpServers:
            github:
              url: https://api.githubcopilot.com/mcp/
              headers:
                Authorization: Bearer YOUR_TOKEN
              autoApprove:
                - get_issue
                - list_pull_requests
            context7:
              command: npx
              args:
                - -y
                - '@upstash/context7-mcp'
              env: {}
```

## 说明

- `mcp.json` 使用 deep merge，同名 server 只覆盖声明的字段，未声明字段保持原样。
- 如果你希望使用仓库级 `.cursor/mcp.json` 或 `.vscode/mcp.json`，可以覆盖 `agent_cursor_mcp_config_path`；role 本身不强制限定目标路径。
- `agent_cursor_confirm_mcp_config_update` 适用于手动执行 playbook 的交互确认；如果是无人值守执行，应保持为 `false`。
- Cursor 官方 CLI 安装方式不是 npm 包，所以本 role 默认只检查 `agent` 是否存在，不主动安装。
