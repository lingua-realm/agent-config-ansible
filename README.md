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

如果希望显式按 profile 运行，也可以使用仓库脚本：

```bash
scripts/run-playbook.sh default playbooks/setup_codex.yml
scripts/run-playbook.sh default playbooks/setup_claude_code.yml -e "target_hosts=all"
```

这个脚本要求两个必填参数：

- 第一个参数是 profile，对应 `inventory/<profile>/inventory.yml`
- 第二个参数是仓库内 playbook 相对路径，例如 `playbooks/setup_gemini_cli.yml`

脚本内部会自动设置 `ANSIBLE_INVENTORY`，并从仓库根目录执行 `uv run ansible-playbook`。

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

## 推荐使用姿势

为了让这套声明式配置在长期维护时更稳，建议按下面的方式使用：

1. **把 `inventory/default/` 当作模板，而不是长期直接修改的唯一环境。**
   - 推荐复制出自己的 profile，例如 `inventory/work/`、`inventory/home/`，然后在该 profile 下维护 `group_vars/all/` 和各类 assets。
   - 这样后续跟进仓库更新时，更容易对比默认示例和你自己的实际配置。
2. **优先按工具分批执行，再扩大到全部主机。**
   - 例如先单独运行 `setup_codex.yml` 或 `setup_gemini_cli.yml` 验证结果，再决定是否加上 `-e "target_hosts=all"` 面向全 inventory 推送。
   - 如果只调整了某一个 agent 的配置，没有必要每次都执行全部 playbook。
3. **共享项放共享目录，差异项放各工具覆盖文件。**
   - 通用 MCP 配置尽量维护在 `group_vars/all/agent_mcps/servers.yml`。
   - 只有某个 agent 需要特殊行为时，再写入对应的 `claude_code/mcp_servers.yml`、`codex/mcp_servers.yml`、`gemini_cli/mcp_servers.yml` 或 `copilot_cli/mcp_servers.yml`。
4. **把“可同步资产”和“敏感信息”分开维护。**
   - `CLAUDE.md`、`AGENTS.md`、`GEMINI.md`、skills 源目录这类内容适合放进 inventory 资产目录。
   - API Key、token 等敏感信息应集中维护在 `group_vars/all/secrets.yml` 或 CI Secret 中，不要写入可公开同步的说明文件。
5. **保留交互确认用于人工执行，无人值守时显式关闭确认。**
   - 人工执行时，仓库默认的 confirm/pause 流程可以帮助你在覆盖关键文件前再确认一次。
   - 放到 CI 或批量自动执行时，再通过 extra vars 把相关确认开关关闭。
6. **把备份目录当作升级和回滚的第一道保险。**
   - 本地执行时，优先检查 `tmps/` 下对应工具的备份是否符合预期。
   - 尤其是 Codex / Gemini 的 `.env` 一类文件，建议在首次落地或大改前先确认备份路径和恢复方式。

## 升级 / 更新指南

仓库后续升级时，建议按以下顺序操作，尽量把风险控制在单个 profile、单个工具、单台主机范围内：

1. **先更新仓库和依赖。**

   ```bash
   git pull
   uv sync --dev
   ```

2. **先阅读本次更新涉及的文档与默认示例。**
   - 重点关注 `README.md`、仓库根目录 `AGENTS.md`，以及 `inventory/default/group_vars/all/` 下新增或调整的变量文件。
   - 如果上游调整了目录结构、变量命名或 assets 约定，先把这些变化映射到你自己的 profile，再执行 playbook。
3. **先做语法校验，再做定向执行。**

   ```bash
   uv run ansible-playbook --syntax-check playbooks/setup_claude_code.yml
   uv run ansible-playbook --syntax-check playbooks/setup_codex.yml
   uv run ansible-playbook --syntax-check playbooks/setup_gemini_cli.yml
   uv run ansible-playbook --syntax-check playbooks/setup_copilot_cli.yml
   uv run ansible-playbook --syntax-check playbooks/setup_agent_skills.yml
   ```

   - 如果你这次只升级某一个工具，也可以只校验和执行对应 playbook。
4. **先在一个小范围目标上验证。**
   - 推荐先对 localhost 或单台测试机执行。
   - 确认生成的配置文件、同步的资产文件以及 CLI 自身校验都正常后，再扩大到 `target_hosts=all`。
5. **升级后核对备份与结果文件。**
   - 检查 `tmps/*-backups/<inventory_hostname>/` 是否生成了预期备份。
   - 再核对目标端的 `settings.json`、`.env`、`AGENTS.md`、`GEMINI.md`、`mcp-config.json` 等关键输出。
6. **如果升级结果不符合预期，优先按备份回滚。**
   - 本仓库默认保留覆盖前的备份，通常可以直接从 `tmps/` 或目标文件旁的备份目录恢复。
   - 回滚后建议重新检查 inventory 变量归一化是否跟上了上游变更，避免重复覆盖出错。

如果你维护了多个 profile，推荐采用“**先升级默认示例理解变更，再逐个 profile 合并**”的节奏，而不是一次性同时修改所有环境配置。

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

| Secret 名称      | 用途                                     |
| ---------------- | ---------------------------------------- |
| `VOLCES_API_KEY` | Claude Code 模型接入（火山引擎 API Key） |
| `PPIO_API_KEY`   | Codex CLI 模型接入（PPIO API Key）       |

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
