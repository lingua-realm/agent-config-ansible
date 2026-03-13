# agent_gemini_cli

复用仓库现有基础 role，为 Gemini CLI 执行一套完整的自动化配置流程：

- 检查可选的 Gemini CLI 可用性
- 生成并同步 `~/.gemini/settings.json`
- 按需生成并同步 `~/.gemini/.env`
- 按需同步用户级 `GEMINI.md`

## 依赖的基础 role

- `npm_command_bootstrap`
- `managed_file`

## 变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `agent_gemini_cli_home_dir` | ❌ | `~/.gemini` | Gemini 配置根目录 |
| `agent_gemini_cli_settings_path` | ❌ | `~/.gemini/settings.json` | Gemini 主配置文件路径 |
| `agent_gemini_cli_env_path` | ❌ | `~/.gemini/.env` | Gemini 环境变量文件路径 |
| `agent_gemini_cli_gemini_md_path` | ❌ | `~/GEMINI.md` | 用户级 Gemini 指令文件路径 |
| `agent_gemini_cli_temp_root` | ❌ | `/tmp/agent-gemini-cli` | role 工作临时目录 |
| `agent_gemini_cli_require_gemini_cli` | ❌ | `true` | 是否要求 Gemini CLI 可用 |
| `agent_gemini_cli_gemini_auto_install_npm` | ❌ | `@google/gemini-cli` | Gemini CLI 自动安装时使用的 npm 包名 |
| `agent_gemini_cli_manage_settings` | ❌ | `true` | 是否管理 `settings.json` |
| `agent_gemini_cli_manage_env` | ❌ | `true` | 是否管理 `.env`；当 `agent_gemini_cli_env` 为空时会自动跳过 |
| `agent_gemini_cli_manage_gemini_md` | ❌ | `true` | 是否管理 `GEMINI.md`；当 `agent_gemini_cli_gemini_md_src` 为空时会自动跳过 |
| `agent_gemini_cli_run_verify` | ❌ | `true` | role 末尾是否执行验证任务 |
| `agent_gemini_cli_verify_schema` | ❌ | `false` | 是否在控制端执行 `settings.json` JSON Schema 校验；失败会终止 role |
| `agent_gemini_cli_settings_schemafile` | ❌ | Gemini 官方 schema URL | `check-jsonschema --schemafile` 使用的 schema 来源；支持本地文件路径或 URL |
| `agent_gemini_cli_confirm_settings_update` | ❌ | `false` | settings.json 变更时是否交互确认 |
| `agent_gemini_cli_confirm_env_update` | ❌ | `false` | `.env` 变更时是否交互确认 |
| `agent_gemini_cli_backup` | ❌ | `true` | 是否为托管文件创建备份 |
| `agent_gemini_cli_backup_root` | ❌ | `""` | 统一备份根目录；设置后会自动派生 `settings/`、`env/`、`gemini-md/` 子目录 |
| `agent_gemini_cli_settings` | ✅ | 见 defaults | 用于生成 `settings.json` 的配置对象 |
| `agent_gemini_cli_env` | ❌ | `{}` | 将被写入 `~/.gemini/.env` 的环境变量 |
| `agent_gemini_cli_gemini_md_src` | ❌ | `""` | 外部 `GEMINI.md` 文件路径；为空时不管理 |

## `agent_gemini_cli_settings` 结构

```yaml
agent_gemini_cli_settings:
  general:
    preferredEditor: vim
  ui:
    theme: Default
  model:
    name: gemini-2.5-pro
  modelConfigs:
    aliases:
      quick:
        modelConfig:
          model: gemini-2.5-flash
  mcpServers:
    context7:
      command: npx
      args:
        - -y
        - "@upstash/context7-mcp"
    deepwiki:
      httpUrl: https://mcp.deepwiki.com/mcp
```

## 输出

role 执行完成后会写入 `agent_gemini_cli_result`：

```yaml
agent_gemini_cli_result:
  changed: true
  settings:
    changed: true
    path: /home/user/.gemini/settings.json
  env:
    changed: true
    path: /home/user/.gemini/.env
  gemini_md:
    changed: true
    path: /home/user/GEMINI.md
```

## 示例

```yaml
- hosts: all
  tasks:
    - name: 配置 Gemini CLI
      include_role:
        name: agent_gemini_cli
      vars:
        agent_gemini_cli_settings:
          general:
            preferredEditor: vim
          ui:
            theme: Default
          model:
            name: gemini-2.5-pro
          modelConfigs:
            aliases:
              quick:
                modelConfig:
                  model: gemini-2.5-flash
          mcpServers:
            context7:
              command: npx
              args:
                - -y
                - "@upstash/context7-mcp"
        agent_gemini_cli_env:
          GEMINI_API_KEY: "{{ vault_gemini_api_key }}"
        agent_gemini_cli_gemini_md_src: "{{ playbook_dir }}/files/GEMINI.md"
```

## 说明

- `settings.json` 使用 JSON 模板全量渲染，适合用户级默认配置托管。
- `agent_gemini_cli_manage_env: true` 且 `agent_gemini_cli_env` 为空时，会自动跳过 `.env` 同步，不会生成空文件。
- `agent_gemini_cli_confirm_settings_update` 和 `agent_gemini_cli_confirm_env_update` 适用于手动执行 playbook 的交互确认；如果是无人值守执行，应保持为 `false`。
- 设置 `agent_gemini_cli_backup_root` 后，`settings.json`、`.env` 和 `GEMINI.md` 的备份会分别写入其下的 `settings/`、`env/`、`gemini-md/` 子目录。
- `agent_gemini_cli_verify_schema: true` 时，Schema 校验在控制端执行，因此控制端需要可用的 `check-jsonschema`，并且 `agent_gemini_cli_settings_schemafile` 指向的 schema 在控制端可访问。
