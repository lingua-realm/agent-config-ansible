# AGENTS.md

This file provides guidance to AI coding agents working in this repository.

## 项目快照

这是一个基于 Ansible 的 AI Agent 配置管理仓库，目标是把 Claude Code、Codex CLI、Gemini CLI、GitHub Copilot CLI、Cursor 以及 agent skills 以声明式方式同步到本地或远端主机。

仓库根目录的 `AGENTS.md` 用于约束你在这个代码仓库里的工作方式；`inventory/<profile>/codex_assets/AGENTS.md` 和 `inventory/<profile>/gemini_assets/GEMINI.md` 则是样例资产，会被同步到目标机的用户级指令文件，两者不要混淆。

## 常用命令

```bash
# 依赖安装
uv sync
uv sync --dev

# 运行 Playbook
uv run ansible-playbook playbooks/setup_claude_code.yml
uv run ansible-playbook playbooks/setup_codex.yml
uv run ansible-playbook playbooks/setup_gemini_cli.yml
uv run ansible-playbook playbooks/setup_copilot_cli.yml
uv run ansible-playbook playbooks/setup_cursor.yml
uv run ansible-playbook playbooks/setup_agent_skills.yml

# 显式指定 profile 运行
scripts/run-playbook.sh <profile> playbooks/setup_codex.yml
scripts/run-playbook.sh <profile> playbooks/setup_cursor.yml -e "target_hosts=all"

# 面向 inventory 中全部主机执行
uv run ansible-playbook playbooks/setup_claude_code.yml -e "target_hosts=all"
uv run ansible-playbook playbooks/setup_codex.yml -e "target_hosts=all"
uv run ansible-playbook playbooks/setup_gemini_cli.yml -e "target_hosts=all"
uv run ansible-playbook playbooks/setup_copilot_cli.yml -e "target_hosts=all"
uv run ansible-playbook playbooks/setup_cursor.yml -e "target_hosts=all"
uv run ansible-playbook playbooks/setup_agent_skills.yml -e "target_hosts=all"

# Molecule 测试（需进入对应 role 目录）
cd roles/<role-name>
uv run molecule test
uv run molecule converge
uv run molecule verify
uv run molecule destroy
uv run molecule test -s <scenario>
```

## 心智模型

### 顶层编排 role

```text
agent_claude_code
  ├── npm_command_bootstrap
  ├── managed_file
  ├── managed_json_merge
  └── managed_tree

agent_codex
  ├── npm_command_bootstrap
  └── managed_file

agent_gemini_cli
  ├── npm_command_bootstrap
  └── managed_file

agent_copilot_cli
  ├── npm_command_bootstrap
  └── managed_json_merge

agent_cursor
  ├── npm_command_bootstrap
  └── managed_json_merge

managed_agent_skills
  └── npm_command_bootstrap
```

### 各入口 role 的职责

- `agent_claude_code`：检查 Claude CLI / ccline，管理插件，合并 `~/.claude.json`，生成 `settings.json`，同步 `output-styles/` 和 `CLAUDE.md`。
- `agent_codex`：检查 Codex CLI，生成 `config.toml` 和 `.env`，同步 `AGENTS.md`。
- `agent_gemini_cli`：检查 Gemini CLI，生成 `settings.json` 和 `.env`，同步 `GEMINI.md`。
- `agent_copilot_cli`：检查 Copilot CLI，生成并验证 `~/.copilot/mcp-config.json`。
- `agent_cursor`：检查 Cursor Agent CLI（`agent`），生成并验证 `~/.cursor/mcp.json`。
- `managed_agent_skills`：基于 `skills` CLI 声明式安装或卸载 skills。

### 基础能力 role

- `managed_file`：单文件模板渲染、排序、diff 预览、备份。
- `managed_json_merge`：JSON deep merge。
- `managed_tree`：目录树同步，容器环境会自动从 `synchronize` 切换到 archive 方案。
- `npm_command_bootstrap`：CLI 检查与按需全局 npm 安装。

## 关键目录

```text
playbooks/                     # 顶层入口
roles/                         # 所有 Ansible roles
inventory/default/             # 默认 inventory 示例
inventory/default/group_vars/all/
  ├── agent_mcps/              # Claude / Codex / Copilot / Cursor 共享 MCP 默认值
  ├── agent_skills/            # skills CLI 与条目声明
  ├── claude_code/             # Claude Code 设置、模型、MCP 覆盖
  ├── codex/                   # Codex 设置、模型、MCP 覆盖
  ├── gemini_cli/              # Gemini CLI 设置、模型、MCP 覆盖
  ├── copilot_cli/             # Copilot CLI 设置、MCP 覆盖
  ├── cursor/                  # Cursor 设置、MCP 覆盖
  └── secrets.yml              # inventory 级敏感信息
inventory/default/claude_assets/
inventory/default/codex_assets/
inventory/default/gemini_assets/
inventory/default/agent_skills_assets/
tmps/                          # 本地执行时的默认备份和日志目录
```

## 用户侧推荐使用方式

- 把 `inventory/default/` 当作模板，而不是长期直接修改的唯一环境；推荐复制出自己的 `inventory/<profile>/`。
- 需要显式切换 profile 时，优先使用 `scripts/run-playbook.sh <profile> <playbook>`，而不是手动维护 `ANSIBLE_INVENTORY`。
- `confirm`、备份目录、CLI 检查、自动安装、`manage_*`、`run_verify` 等运行控制默认已内置；默认示例 inventory 只保留真正影响输出内容的变量。
- 通用 MCP 默认值维护在 `group_vars/all/agent_mcps/servers.yml`，只有某个 agent 需要特殊行为时，才写到各自的 `mcp_servers.yml`。
- `CLAUDE.md`、`AGENTS.md`、`GEMINI.md`、skills 源目录这类可同步资产和 `secrets.yml` 这类敏感信息要分开维护。
- 先对单个工具或单台主机验证，再扩大到 `target_hosts=all`；本地执行时优先检查 `tmps/` 下的备份结果。

## 编辑本仓库时要遵守的约定

### 1. 入口 playbook 负责变量归一化

- 顶层 playbook 会显式 `include_vars: dir={{ inventory_dir }}/group_vars/all` 递归加载嵌套变量目录。
- 新增或调整 inventory 变量时，优先在 playbook `pre_tasks` 中完成兼容映射、默认值推导和结构校验，不要把复杂归一化逻辑塞进 role 内部模板。
- **变量归一化应保持简洁**：避免冗余的三目分支（如 `var if defined else settings.xxx`）。检查 `settings` 对象中的后备字段是否实际使用；如果未使用，应简化为 `var | default(value)` 直接引用顶层变量。
- **安全字段默认值**：影响配置变更的字段（如 `confirm`）默认值应为 `true`，无人值守场景通过 `-e` 显式覆盖为 `false`。

### 2. role 结构要保持按职责拆分

- role 内部 task 文件按职责拆分，如 `validate.yml`、`sync_*`、`verify.yml`。
- `tasks/main.yml` 负责顺序编排，不要把所有逻辑堆进一个超大文件。
- 默认变量放在 `defaults/main.yml`，模板放在 `templates/`。

### 3. 保留现有确认与备份语义

- `managed_file_confirm`、`managed_json_merge_confirm`、`agent_claude_code_confirm_*` 这类变量面向人工执行时的交互确认。
- 无人值守场景要能通过变量关闭确认；确认逻辑依赖 `pause`，不要改成自定义 TTY 探测。
- Codex 的 `.env` 可能包含密钥，默认不要开启 diff 确认。
- 本地连接执行时默认把备份写到仓库 `tmps/*-backups/<inventory_hostname>/`；远端执行时回退到目标文件旁边。

### 4. 共享 MCP 与 agent 覆盖要分层维护

- 共享默认值维护在 `group_vars/all/agent_mcps/servers.yml` 的 `agent_mcps` 下。
- Claude、Codex、Gemini、Copilot、Cursor 的差异化覆盖分别放在各自 `mcp_servers.yml`。
- Claude Code 需要 `mcpServers` 结构，Codex 需要 `mcp_servers`，Gemini CLI 需要 `mcpServers`，Copilot CLI 需要 `mcpServers` 且每个条目带 `tools`，Cursor 需要 `mcpServers`；这些转换发生在对应 playbook 的 `pre_tasks`。

### 5. include_role 传路径时先固化 `role_path`

- 如果一个 role 里 `include_role` 调下游 role，且需要把当前 role 的模板/文件路径传下去，先用 `set_fact` 固化当前 `role_path`。
- 不要直接把惰性的 `{{ role_path }}` 传进去，否则容易在下游 role 中解析成错误路径。

## 当前仓库里的关键细节

- `claude_code/settings.yml` 的 `env` 仍引用 `model_configs[claude_code_use_model]`，因此 `setup_claude_code.yml` 需要先把 `claude_code_model_configs` 映射到兼容变量 `model_configs`。
- Claude Code 的模型配置位于 `inventory/default/group_vars/all/claude_code/models.yml`，包含 `private_variables`、`claude_code_model_configs`（每项含 `base_url`、`api_key`、`model`）和 `claude_code_use_model`（默认模型键名）。
- API key 通过 Jinja2 模板引用 secrets：`{{ (secrets | default({})).get('api_keys', {}).get('<provider>', '') }}`，无需硬编码。
- `setup_codex.yml` 会把 `codex/settings.yml`、`models.yml`、`agent_mcps/servers.yml` 和 `codex/mcp_servers.yml` 归一化成单个 `agent_codex_config` / `agent_codex_env` 输入。
- `agent_codex` 会保留目标机现有 `~/.codex/config.toml` 里的 `[projects]` 本地信任状态，避免 Codex CLI 写入的本地目录路径造成托管漂移；这些路径不需要入 inventory。
- `setup_gemini_cli.yml` 会把 `gemini_cli/settings.yml`、`models.yml`、`agent_mcps/servers.yml` 和 `gemini_cli/mcp_servers.yml` 归一化成单个 `agent_gemini_cli_settings` / `agent_gemini_cli_env` 输入。
- `setup_copilot_cli.yml` 当前只管理 `~/.copilot/mcp-config.json`，不负责 Copilot CLI 账号、模型或其他偏好设置。
- `setup_cursor.yml` 当前只管理 `~/.cursor/mcp.json`，供 Cursor 编辑器与 Cursor Agent CLI 共享使用，不负责账号、模型或其他偏好设置。
- `managed_agent_skills` 的 `source` 必须对目标机可见；仓库内路径通常只适用于 `ansible_connection=local`。
- `ansible.cfg` 中启用了 `any_errors_fatal = True` 和 `gathering = explicit`，所以失败会立刻终止，facts 也不会默认收集。

## CI 与升级细节

- `.github/workflows/ci.yml` 会在每次 `push` 时触发，先对 6 个入口 playbook 做 `--syntax-check`，再用 matrix 分别执行 `claude_code`、`codex`、`gemini_cli`、`copilot_cli`、`cursor`，并在每个矩阵实例后执行 `setup_agent_skills.yml`。
- CI 当前固定使用 `inventory/default/inventory.yml` 的 localhost 配置，不会自动切换到其他 profile。
- 当前 CI 依赖的 Repository Secrets 只有 `VOLCES_API_KEY` 和 `PPIO_API_KEY`。
- CI 会通过 extra vars 显式设置这些确认项为 `false` 以实现无人值守：
  - `claude_code_confirm_settings_update`
  - `claude_code_confirm_user_json_update`
  - `copilot_cli_confirm_mcp_config_update`
  - `cursor_confirm_mcp_config_update`
  - `codex_confirm_config_update`
  - `codex_confirm_env_update`
  - `gemini_confirm_settings_update`
  - `gemini_confirm_env_update`
  默认情况下这些确认项均为 `true`，用于防止意外覆盖用户配置。
- 升级仓库时，建议先更新代码和依赖，再阅读 `README.md`、根目录 `AGENTS.md` 以及 `inventory/default/` 下的默认示例变化，然后先做 `--syntax-check`，最后只对需要的工具和小范围目标执行。

## 测试策略

- 测试框架是 Molecule + Podman，容器镜像为 `python:3.13-bookworm`。
- 每个 role 都有 `molecule/default/` 场景。
- 额外场景包括：
  - `roles/managed_file/molecule/json_sorted/`
  - `roles/npm_command_bootstrap/molecule/auto_install/`
  - `roles/npm_command_bootstrap/molecule/required_false/`
- `managed_tree` / `agent_claude_code` 的容器测试依赖 `managed_tree_transport: auto` 自动回退到 archive 模式，不要为了绕过容器限制改回固定 `local/default` driver。
- `agent_codex` 的验证依赖目标端 Python 内置 `tomllib`，目标主机需要 Python `>=3.11`。
- `agent_gemini_cli` 的验证依赖目标端 Python 内置 `json`，默认用户级输出包括 `~/.gemini/settings.json`、`~/.gemini/.env` 和 `~/GEMINI.md`。

如果你修改了某个 role，优先在对应 role 目录下运行相关 Molecule 场景，而不是只做静态阅读。

## 文档更新时的建议

- `README.md` 面向仓库使用者，应保持精简，聚焦仓库能力、最短上手路径、profile 用法和常用命令。
- 仓库根目录 `AGENTS.md` 面向在仓库里执行任务的 AI 代理，应承接架构、变量归一化、CI、测试边界、升级与易错点等细节。
- 如果你改动了 playbook、inventory 结构或 role 边界，通常需要同步更新这两个文件。
