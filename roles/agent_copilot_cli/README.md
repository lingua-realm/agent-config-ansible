# agent_copilot_cli

复用仓库现有基础 role，为 GitHub Copilot CLI 执行一套最小但完整的 MCP 自动化配置流程：

- 检查可选的 GitHub Copilot CLI 可用性
- deep merge 并同步 `~/.copilot/mcp-config.json`
- 验证最终 MCP 配置结果

当前 role 只处理 Copilot CLI 的 MCP 配置，不管理模型、认证或其他 CLI 行为设置。

## 依赖的基础 role

- `npm_command_bootstrap`
- `managed_json_merge`

## 变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `agent_copilot_cli_home_dir` | ❌ | `~/.copilot` | Copilot CLI 配置根目录 |
| `agent_copilot_cli_mcp_config_path` | ❌ | `~/.copilot/mcp-config.json` | Copilot CLI MCP 配置文件路径 |
| `agent_copilot_cli_temp_root` | ❌ | `/tmp/agent-copilot-cli` | role 工作临时目录 |
| `agent_copilot_cli_require_copilot_cli` | ❌ | `true` | 是否要求 Copilot CLI 可用 |
| `agent_copilot_cli_copilot_auto_install_npm` | ❌ | `@github/copilot` | Copilot CLI 自动安装时使用的 npm 包名 |
| `agent_copilot_cli_manage_mcp_config` | ❌ | `true` | 是否管理 `mcp-config.json` |
| `agent_copilot_cli_run_verify` | ❌ | `true` | role 末尾是否执行验证任务 |
| `agent_copilot_cli_confirm_mcp_config_update` | ❌ | `false` | `mcp-config.json` 变更时是否交互确认 |
| `agent_copilot_cli_backup` | ❌ | `true` | 是否为托管文件创建备份 |
| `agent_copilot_cli_backup_root` | ❌ | `""` | 统一备份根目录；设置后会自动派生 `mcp-config/` 子目录 |
| `agent_copilot_cli_mcp_config` | ✅ | 见 defaults | 将被 deep merge 到 `mcp-config.json` 的对象 |

## `agent_copilot_cli_mcp_config` 结构

```yaml
agent_copilot_cli_mcp_config:
  mcpServers:
    context7:
      type: stdio
      command: npx
      args:
        - -y
        - '@upstash/context7-mcp'
      env: {}
      tools:
        - "*"
    deepwiki:
      type: http
      url: https://mcp.deepwiki.com/mcp
      headers: {}
      tools:
        - read_page
```

## 输出

role 执行完成后会写入 `agent_copilot_cli_result`：

```yaml
agent_copilot_cli_result:
  changed: true
  mcp_config:
    changed: true
    path: /home/user/.copilot/mcp-config.json
```

## 示例

```yaml
- hosts: all
  tasks:
    - name: 配置 GitHub Copilot CLI MCP
      include_role:
        name: agent_copilot_cli
      vars:
        agent_copilot_cli_mcp_config:
          mcpServers:
            context7:
              type: stdio
              command: npx
              args:
                - -y
                - '@upstash/context7-mcp'
              env: {}
              tools:
                - "*"
            open-websearch:
              type: stdio
              command: npx
              args:
                - -y
                - open-websearch@latest
              env:
                MODE: stdio
              tools:
                - search
```

## 说明

- `mcp-config.json` 使用 deep merge，同名 server 只覆盖声明的字段，未声明字段保持原样。
- 如果你希望使用仓库级 `.vscode/mcp.json`，可以覆盖 `agent_copilot_cli_mcp_config_path`；role 本身不强制限定目标路径。
- `agent_copilot_cli_confirm_mcp_config_update` 适用于手动执行 playbook 的交互确认；如果是无人值守执行，应保持为 `false`。
