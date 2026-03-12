# agent_codex

复用仓库现有基础 role，为 Codex CLI 执行一套完整的自动化配置流程：

- 检查可选的 Codex CLI 可用性
- 生成并同步 `~/.codex/config.toml`
- 按需生成并同步 `~/.codex/.env`
- 按需同步外部 `AGENTS.md`

## 依赖的基础 role

- `npm_command_bootstrap`
- `managed_file`

## 变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `agent_codex_home_dir` | ❌ | `~/.codex` | Codex 配置根目录 |
| `agent_codex_config_path` | ❌ | `~/.codex/config.toml` | Codex 主配置文件路径 |
| `agent_codex_env_path` | ❌ | `~/.codex/.env` | Codex 环境变量文件路径 |
| `agent_codex_agents_md_path` | ❌ | `~/.codex/AGENTS.md` | Codex 指令文件路径 |
| `agent_codex_temp_root` | ❌ | `/tmp/agent-codex` | role 工作临时目录 |
| `agent_codex_require_codex_cli` | ❌ | `true` | 是否要求 Codex CLI 可用 |
| `agent_codex_codex_auto_install_npm` | ❌ | `@openai/codex` | Codex CLI 自动安装时使用的 npm 包名 |
| `agent_codex_manage_config` | ❌ | `true` | 是否管理 `config.toml` |
| `agent_codex_manage_env` | ❌ | `true` | 是否管理 `.env`；当 `agent_codex_env` 为空时会自动跳过 |
| `agent_codex_manage_agents_md` | ❌ | `true` | 是否管理 `AGENTS.md`；当 `agent_codex_agents_md_src` 为空时会自动跳过 |
| `agent_codex_run_verify` | ❌ | `true` | role 末尾是否执行验证任务 |
| `agent_codex_confirm_config_update` | ❌ | `false` | config.toml 变更时是否交互确认 |
| `agent_codex_confirm_env_update` | ❌ | `false` | `.env` 变更时是否交互确认 |
| `agent_codex_backup` | ❌ | `true` | 是否为托管文件创建备份 |
| `agent_codex_backup_root` | ❌ | `""` | 统一备份根目录；设置后会自动派生 `config/`、`env/`、`agents-md/` 子目录 |
| `agent_codex_config` | ✅ | 见 defaults | 用于生成 `config.toml` 的配置对象 |
| `agent_codex_env` | ❌ | `{}` | 将被写入 `~/.codex/.env` 的环境变量 |
| `agent_codex_agents_md_src` | ❌ | `""` | 外部 `AGENTS.md` 文件路径；为空时不管理 |

## `agent_codex_config` 结构

```yaml
agent_codex_config:
  model_provider: ppio
  model: pa/gpt-5.4
  model_reasoning_effort: xhigh
  disable_response_storage: true
  preferred_auth_method: apikey
  sandbox_mode: read-only
  history:
    persistence: save-all
  model_providers:
    ppio:
      name: PPIO (GPT-5.4)
      base_url: https://api.ppio.com/openai/v1
      wire_api: responses
      env_key: PPIO_API_KEY
  mcp_servers:
    context7:
      command: npx
      args:
        - -y
        - '@upstash/context7-mcp'
```

## 输出

role 执行完成后会写入 `agent_codex_result`：

```yaml
agent_codex_result:
  changed: true
  config:
    changed: true
    path: /home/user/.codex/config.toml
  env:
    changed: true
    path: /home/user/.codex/.env
  agents_md:
    changed: true
    path: /home/user/.codex/AGENTS.md
```

## 示例

```yaml
- hosts: all
  tasks:
    - name: 配置 Codex CLI
      include_role:
        name: agent_codex
      vars:
        agent_codex_config:
          model_provider: ppio
          model: pa/gpt-5.4
          model_reasoning_effort: xhigh
          disable_response_storage: true
          preferred_auth_method: apikey
          sandbox_mode: read-only
          history:
            persistence: save-all
          model_providers:
            ppio:
              name: PPIO (GPT-5.4)
              base_url: https://api.ppio.com/openai/v1
              wire_api: responses
              env_key: PPIO_API_KEY
          mcp_servers:
            fetch:
              command: uvx
              args:
                - mcp-server-fetch
        agent_codex_env:
          PPIO_API_KEY: "{{ vault_ppio_api_key }}"
        agent_codex_agents_md_src: "{{ playbook_dir }}/files/AGENTS.md"
```

## 说明

- `config.toml` 使用通用 TOML 模板递归渲染：标量、数组和嵌套对象都会映射成对应的 TOML 键或表。
- `agent_codex_manage_env: true` 且 `agent_codex_env` 为空时，会自动跳过 `.env` 同步，不会生成空文件。
- `agent_codex_confirm_config_update` 和 `agent_codex_confirm_env_update` 适用于手动执行 playbook 的交互确认；如果是无人值守执行，应保持为 `false`。
- 设置 `agent_codex_backup_root` 后，`config.toml`、`.env` 和 `AGENTS.md` 的备份会分别写入其下的 `config/`、`env/`、`agents-md/` 子目录。
