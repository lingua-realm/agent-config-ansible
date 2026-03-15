# agent-config-ansible

基于 Ansible 的 AI Agent 配置管理仓库，用来把 Claude Code、Codex CLI、Gemini CLI、GitHub Copilot CLI、Cursor 以及 agent skills 以声明式方式同步到本地或远端主机。

## 管理范围

- `playbooks/setup_claude_code.yml`：部署 Claude Code 的 `settings.json`、`~/.claude.json`、插件与可选资产。
- `playbooks/setup_codex.yml`：部署 Codex CLI 的 `config.toml`、`.env` 与可选 `AGENTS.md`。
- `playbooks/setup_gemini_cli.yml`：部署 Gemini CLI 的 `settings.json`、`.env` 与可选 `GEMINI.md`。
- `playbooks/setup_copilot_cli.yml`：部署 GitHub Copilot CLI 的 `~/.copilot/mcp-config.json`。
- `playbooks/setup_cursor.yml`：部署 Cursor / Cursor Agent CLI 共享的 `~/.cursor/mcp.json`。
- `playbooks/setup_agent_skills.yml`：通过 `skills` CLI 声明式安装或卸载 skills。

## 快速开始

### 1. 安装依赖

```bash
uv sync --dev
```

仓库开发依赖要求 Python `>=3.13`，核心依赖包括：

- `ansible>=13.4.0`
- `check-jsonschema>=0.37.0`
- `molecule>=26.3.0`
- `molecule-plugins[podman]>=25.8.12`

### 2. 准备 inventory

默认 inventory 位于 `inventory/default/`，常见目录如下：

```text
inventory/default/
├── inventory.yml
├── group_vars/all/
│   ├── agent_mcps/
│   │   └── servers.yml
│   ├── agent_skills/
│   │   ├── settings.yml
│   │   └── items.yml
│   ├── claude_code/
│   │   ├── backup.yml
│   │   ├── settings.yml
│   │   ├── models.yml
│   │   └── mcp_servers.yml
│   ├── codex/
│   │   ├── backup.yml
│   │   ├── settings.yml
│   │   ├── models.yml
│   │   └── mcp_servers.yml
│   ├── gemini_cli/
│   │   ├── backup.yml
│   │   ├── settings.yml
│   │   ├── models.yml
│   │   └── mcp_servers.yml
│   ├── copilot_cli/
│   │   ├── backup.yml
│   │   ├── settings.yml
│   │   └── mcp_servers.yml
│   ├── cursor/
│   │   ├── backup.yml
│   │   ├── settings.yml
│   │   └── mcp_servers.yml
│   └── secrets.yml
├── claude_assets/
│   ├── output-styles/
│   └── CLAUDE.md
├── codex_assets/
│   └── AGENTS.md
├── gemini_assets/
│   └── GEMINI.md
└── agent_skills_assets/
```

> 入口 playbook 会显式递归加载 `group_vars/all/` 下的 YAML 片段，所以变量按子目录拆分是仓库的既定模式，不能只依赖 Ansible 默认的 inventory 自动加载。

### 3. 执行需要的 playbook

`ansible.cfg` 已经把默认 inventory 指向 `inventory/default/inventory.yml`，因此在默认场景下可以直接运行：

```bash
uv run ansible-playbook playbooks/setup_claude_code.yml
uv run ansible-playbook playbooks/setup_codex.yml
uv run ansible-playbook playbooks/setup_gemini_cli.yml
uv run ansible-playbook playbooks/setup_copilot_cli.yml
uv run ansible-playbook playbooks/setup_cursor.yml
uv run ansible-playbook playbooks/setup_agent_skills.yml
```

如果要面向 inventory 中的全部主机执行：

```bash
uv run ansible-playbook playbooks/setup_claude_code.yml -e "target_hosts=all"
uv run ansible-playbook playbooks/setup_codex.yml -e "target_hosts=all"
uv run ansible-playbook playbooks/setup_gemini_cli.yml -e "target_hosts=all"
uv run ansible-playbook playbooks/setup_copilot_cli.yml -e "target_hosts=all"
uv run ansible-playbook playbooks/setup_cursor.yml -e "target_hosts=all"
uv run ansible-playbook playbooks/setup_agent_skills.yml -e "target_hosts=all"
```

## Playbooks 一览

| Playbook                           | 作用                 | 主要输入                                                                                      | 主要输出                                                                                             |
| ---------------------------------- | -------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `playbooks/setup_claude_code.yml`  | Claude Code 顶层编排 | `group_vars/all/claude_code/*.yml`、`group_vars/all/agent_mcps/servers.yml`、`claude_assets/` | `~/.claude/settings.json`、`~/.claude.json`、插件、`~/.claude/output-styles/`、`~/.claude/CLAUDE.md` |
| `playbooks/setup_codex.yml`        | Codex CLI 顶层编排   | `group_vars/all/codex/*.yml`、`group_vars/all/agent_mcps/servers.yml`、`codex_assets/`        | `~/.codex/config.toml`、`~/.codex/.env`、`~/.codex/AGENTS.md`                                        |
| `playbooks/setup_gemini_cli.yml`   | Gemini CLI 顶层编排  | `group_vars/all/gemini_cli/*.yml`、`group_vars/all/agent_mcps/servers.yml`、`gemini_assets/`  | `~/.gemini/settings.json`、`~/.gemini/.env`、`~/GEMINI.md`                                           |
| `playbooks/setup_copilot_cli.yml`  | Copilot CLI MCP 编排 | `group_vars/all/copilot_cli/*.yml`、`group_vars/all/agent_mcps/servers.yml`                   | `~/.copilot/mcp-config.json`                                                                         |
| `playbooks/setup_cursor.yml`       | Cursor MCP 编排      | `group_vars/all/cursor/*.yml`、`group_vars/all/agent_mcps/servers.yml`                        | `~/.cursor/mcp.json`                                                                                 |
| `playbooks/setup_agent_skills.yml` | Skills 声明式编排    | `group_vars/all/agent_skills/*.yml`、`agent_skills_assets/`                                   | 对目标 agent 执行 `skills add` / `skills remove`                                                     |

## Role 架构

仓库分成 6 个顶层编排 role 和 4 个基础能力 role：

### 顶层编排 role

| Role                   | 职责                                                                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------- |
| `agent_claude_code`    | 编排 Claude CLI / ccline 检查、插件管理、`~/.claude.json` 合并、`settings.json` 渲染、资产同步与校验 |
| `agent_codex`          | 编排 Codex CLI 检查、`config.toml` 渲染、`.env` 渲染、`AGENTS.md` 同步与校验                         |
| `agent_gemini_cli`     | 编排 Gemini CLI 检查、`settings.json` 渲染、`.env` 渲染、`GEMINI.md` 同步与校验                      |
| `agent_copilot_cli`    | 编排 Copilot CLI 检查、`mcp-config.json` 生成与校验                                                  |
| `agent_cursor`         | 编排 Cursor Agent CLI 检查、`mcp.json` 生成与校验                                                    |
| `managed_agent_skills` | 基于 `skills` CLI 声明式安装/卸载 skills                                                             |

### 基础能力 role

| Role                    | 职责                                                               |
| ----------------------- | ------------------------------------------------------------------ |
| `managed_file`          | 单文件模板渲染、排序、diff 预览、备份                              |
| `managed_json_merge`    | JSON deep merge，适合局部更新而不是全量覆盖                        |
| `managed_tree`          | 目录树同步；在容器环境下可自动从 `synchronize` 回退到 archive 方案 |
| `npm_command_bootstrap` | 检查 npm CLI 是否存在，并按需 `npm install -g` 自动安装            |

## MCP 配置约定

共享 MCP 默认值统一维护在 `group_vars/all/agent_mcps/servers.yml` 的 `agent_mcps` 下，再由各入口 playbook 转换成目标 agent 需要的格式：

- Claude Code：合并进 `claude_code_dot_claude_json_merge.mcpServers`
- Codex：合并进 `codex_config_effective.mcp_servers`
- Gemini CLI：转换成 `mcpServers` 格式写入 `settings.json`
- GitHub Copilot CLI：转换成 `mcpServers` 格式写入 `mcp-config.json`
- Cursor：转换成 `mcpServers` 格式写入 `mcp.json`

如果要做 agent 特有差异，可以在以下文件中按同名服务覆盖：

- `group_vars/all/claude_code/mcp_servers.yml`
- `group_vars/all/codex/mcp_servers.yml`
- `group_vars/all/gemini_cli/mcp_servers.yml`
- `group_vars/all/copilot_cli/mcp_servers.yml`
- `group_vars/all/cursor/mcp_servers.yml`

## 资产目录约定

### Claude Code

`playbooks/setup_claude_code.yml` 默认自动发现：

- `inventory/<profile>/claude_assets/output-styles/`
- `inventory/<profile>/claude_assets/CLAUDE.md`

也可以通过以下变量覆盖默认路径：

- `claude_code_output_styles_src`
- `claude_code_claude_md_src`

### Codex CLI

`playbooks/setup_codex.yml` 默认自动发现：

- `inventory/<profile>/codex_assets/AGENTS.md`

也可以通过 `codex_agents_md_src` 覆盖默认路径。

### Gemini CLI

`playbooks/setup_gemini_cli.yml` 默认自动发现：

- `inventory/<profile>/gemini_assets/GEMINI.md`

也可以通过 `gemini_gemini_md_src` 覆盖默认路径。

### Agent Skills

如果希望在 inventory 中维护本地 skill 源目录，可使用：

- `inventory/<profile>/agent_skills_assets/`

注意 `agent_skills_items[*].source` 必须对目标机可见：仓库内路径通常只适用于 `ansible_connection=local`；远端主机更推荐 GitHub shorthand、Git URL 或目标机已有路径。

> 仓库根目录的 `AGENTS.md` 是给在本仓库里工作的 AI 代理看的；`inventory/<profile>/codex_assets/AGENTS.md` 和 `inventory/<profile>/gemini_assets/GEMINI.md` 则是要同步到目标机的用户级指令资产样例，两者用途不同。

## 备份策略

本地连接执行时，默认备份会写入仓库的 `tmps/` 目录；远端执行时则回退到目标文件旁边的默认备份目录。

默认子目录如下：

- Claude Code：`tmps/claude-code-backups/<inventory_hostname>/`
  - `settings/`
  - `user-json/`
  - `claude-md/`
- Codex CLI：`tmps/codex-backups/<inventory_hostname>/`
  - `config/`
  - `env/`
  - `agents-md/`
- Gemini CLI：`tmps/gemini-cli-backups/<inventory_hostname>/`
  - `settings/`
  - `env/`
  - `gemini-md/`
- GitHub Copilot CLI：`tmps/copilot-cli-backups/<inventory_hostname>/`
  - `mcp-config/`
- Cursor：`tmps/cursor-backups/<inventory_hostname>/`
  - `mcp-json/`

## GitHub Actions CI

仓库内置 `.github/workflows/ci.yml`，在每次 `push` 时自动触发。

### 工作流结构

| Job | 说明 |
| --- | ---- |
| `syntax-check` | 对六个入口 playbook 依次执行 `--syntax-check` |
| `setup-tools` | matrix job，并发运行 `claude_code`、`codex`、`gemini_cli`、`copilot_cli`、`cursor` 五个工具的完整部署 |

`setup-tools` 的每个 matrix 实例会：

1. 运行对应工具的 playbook（`setup_claude_code.yml` / `setup_codex.yml` / `setup_gemini_cli.yml` / `setup_copilot_cli.yml` / `setup_cursor.yml`）
2. 紧接着运行 `setup_agent_skills.yml`，保证每个工具都完成 skills 同步

所有 playbook 使用 `ansible.cfg` 中预设的 `inventory/default/` 本地 localhost 配置，无需额外的 `-i` 参数。

### 必要的 Repository Secrets

在仓库的 **Settings → Secrets and variables → Actions** 中配置以下密钥：

| Secret 名称 | 用途 |
| ----------- | ---- |
| `VOLCES_API_KEY` | Claude Code 模型接入（火山引擎 API Key） |
| `PPIO_API_KEY` | Codex CLI 模型接入（PPIO API Key） |

CI 会将这两个 Secret 写入 `$RUNNER_TEMP/ansible-extra-vars.yml`，并同时覆盖以下确认开关为 `false` 以保证无人值守执行：

- `claude_code_settings.confirm_settings_update`
- `claude_code_dot_claude_json_merge.confirm_claude_json_update`
- `copilot_cli_confirm_mcp_config_update`
- `cursor_confirm_mcp_config_update`
- `cursor_require_agent_cli`
- `codex_settings.confirm_codex_config_update`
- `codex_settings.confirm_codex_env_update`

## 测试

测试框架为 Molecule + Podman，容器镜像使用 `python:3.13-bookworm`。每个 role 都有独立的 `molecule/default/` 场景，另外还有：

- `roles/managed_file/molecule/json_sorted/`
- `roles/npm_command_bootstrap/molecule/auto_install/`
- `roles/npm_command_bootstrap/molecule/required_false/`

常用命令：

```bash
cd roles/<role-name>
uv run molecule test
uv run molecule converge
uv run molecule verify
uv run molecule destroy
uv run molecule test -s <scenario>
```

其中：

- `managed_tree` / `agent_claude_code` 的容器测试依赖 `managed_tree_transport: auto` 自动回退到 archive 模式
- `agent_codex` 的验证阶段依赖目标端 Python 内置 `tomllib`，因此目标主机需要 Python `>=3.11`
- `agent_gemini_cli` 的验证阶段依赖目标端 Python 内置 `json`，不会额外引入第三方解析依赖

## 开发约定

- Role 默认变量放在 `defaults/main.yml`，编排层变量归一化放在 playbook `pre_tasks`。
- Role 内部 task 文件按职责拆分，通过 `tasks/main.yml` 的 `include_tasks` 编排。
- `any_errors_fatal = True`，任何任务失败会立即终止整个 playbook。
- `gathering = explicit`，默认不自动收集 facts。
- 在 role 内用 `include_role` 调下游 role 且需要传递当前 role 路径时，先用 `set_fact` 固化 `role_path`，不要直接传惰性的 `{{ role_path }}`。
- 交互确认依赖 `pause` 模块；无人值守场景应关闭 confirm 或显式设置 skip 变量。
- Codex 的 `.env` 可能包含密钥，默认不建议开启 diff 确认。
- Gemini CLI 的 `.env` 同样可能包含密钥，默认不建议开启 diff 确认。
- Copilot CLI 编排当前只管理 MCP 配置，不负责账号、模型或其他 CLI 偏好项。
