# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

基于 Ansible 一键同步 Claude Code/Codex 等 AI Agent 工具配置的自动化项目。通过模块化 Roles 管理文件、JSON 合并、目录树同步和 npm 工具安装。

## 常用命令

```bash
# 依赖安装
uv sync            # 生产依赖
uv sync --dev      # 含 molecule 测试依赖

# 运行 Playbook（部署 Claude Code 配置）
uv run ansible-playbook playbooks/setup_claude_code.yml
uv run ansible-playbook playbooks/setup_claude_code.yml -e "target_hosts=all"

# 运行 Playbook（部署 Codex CLI 配置）
uv run ansible-playbook playbooks/setup_codex.yml
uv run ansible-playbook playbooks/setup_codex.yml -e "target_hosts=all"

# 运行 Playbook（声明式管理 Agent Skills）
uv run ansible-playbook playbooks/setup_agent_skills.yml
uv run ansible-playbook playbooks/setup_agent_skills.yml -e "target_hosts=all"

# Molecule 测试（需进入对应 role 目录）
cd roles/<role-name>
uv run molecule test                # 完整测试（含幂等性检查）
uv run molecule converge            # 仅执行 converge
uv run molecule verify              # 仅执行 verify
uv run molecule destroy             # 销毁测试容器
uv run molecule test -s <scenario>  # 运行指定场景（如 json_sorted）
```

## 架构

### Role 依赖关系

```text
agent_claude_code（顶层编排）
  ├── npm_command_bootstrap    — 检查/安装 npm CLI 工具（claude、ccline）
  ├── managed_file             — 单文件管理（模板渲染、diff 预览、备份）
  ├── managed_json_merge       — JSON deep merge（部分更新而非全量重写）
  └── managed_tree             — 目录树同步（rsync/archive，自动检测容器环境）

agent_codex（顶层编排）
  ├── npm_command_bootstrap    — 检查/安装 npm CLI 工具（codex）
  └── managed_file             — 管理 config.toml、.env 与 AGENTS.md

managed_agent_skills（独立 skills 编排）
  └── npm_command_bootstrap    — 检查/安装 skills CLI
```

### agent_claude_code 执行流程

1. **validate** — 检查 Claude CLI / ccline 可用性（复用 npm_command_bootstrap）
2. **plugins** — 管理 marketplace 插件安装
3. **sync_user_json** — Deep merge `~/.claude.json`（复用 managed_json_merge）
4. **sync_settings** — 生成并同步 `~/.claude/settings.json`（复用 managed_file + 模板）
5. **sync_assets** — 同步 output-styles、CLAUDE.md 到 `~/.claude/`（复用 managed_tree + managed_file）

### agent_codex 执行流程

1. **validate** — 检查 Codex CLI 可用性并校验输入结构（复用 npm_command_bootstrap）
2. **sync_config** — 生成并同步 `~/.codex/config.toml`（复用 managed_file + 模板）
3. **sync_env** — 按需生成并同步 `~/.codex/.env`（复用 managed_file + 模板）
4. **sync_assets** — 按需同步 `AGENTS.md` 到 `~/.codex/`（复用 managed_file）

### Inventory 结构

```text
inventory/<profile>/
  ├── inventory.yml
  ├── group_vars/all/
  │   └── claude_code/
  │       ├── backup.yml       # Claude Code 备份根目录
  │       ├── settings.yml     # Claude Code 设置
  │       ├── models.yml       # 模型提供商配置
  │       └── mcp_servers.yml  # MCP 服务器配置
  └── claude_assets/           # 可选资产（自动发现）
      ├── output-styles/
      └── CLAUDE.md

inventory/<profile>/
  ├── inventory.yml
  ├── group_vars/all/
  │   └── codex/
  │       ├── backup.yml       # Codex 备份根目录
  │       ├── settings.yml     # Codex 基础设置
  │       ├── models.yml       # Codex 模型与 provider 配置
  │       └── mcp_servers.yml  # Codex MCP 服务器配置
  └── codex_assets/            # 可选资产（自动发现）
      └── AGENTS.md

inventory/<profile>/
  ├── inventory.yml
  ├── group_vars/all/
  │   └── agent_skills/
  │       ├── settings.yml     # skills CLI / role 编排设置
  │       └── items.yml        # 声明式 skill 条目
  └── agent_skills_assets/     # 可选本地 skill 源目录
```

`claude_assets/` 下的资源由 playbook 自动发现，不存在则跳过。可通过变量 `claude_code_output_styles_src`、`claude_code_claude_md_src` 显式覆盖路径。Claude skills 不再由 `setup_claude_code.yml` 直接同步，建议改用 `managed_agent_skills` role 统一管理。

`codex_assets/` 下的资源由 playbook 自动发现，不存在则跳过。可通过变量 `codex_agents_md_src` 显式覆盖路径。

`setup_agent_skills.yml` 会递归加载 `group_vars/all/agent_skills/*.yml` 并把 `agent_skills_*` 变量桥接到 `managed_agent_skills`。其中 `source` 必须对目标机可见；仓库内本地路径通常只适用于本地连接，远端主机更建议使用 GitHub shorthand、Git URL，或者目标机上已有的本地路径。

由于 Claude Code 变量拆在 `group_vars/all/claude_code/*.yml` 子目录中，顶层 playbook / 入口编排需要显式 `include_vars: dir={{ inventory_dir }}/group_vars/all` 递归加载，不能只依赖默认 inventory 自动加载行为。

当前 `settings.yml` 里的 `env` 仍引用 `model_configs[claude_code_use_model]`，因此编排层需要先把 `claude_code_model_configs` 兼容映射到 `model_configs`，再执行 `agent_claude_code`。

`backup.yml` 默认在本地连接执行时把备份写到仓库 `tmps/claude-code-backups/<inventory_hostname>/` 下；如果切到远端主机执行，则回退到各目标文件旁边的默认备份目录。

Codex 的 `config.toml`、`.env`、`AGENTS.md` 统一由 `agent_codex` 管理；顶层 playbook 需要先把 `codex/settings.yml`、`models.yml`、`mcp_servers.yml` 归一化成单个 `agent_codex_config` 和 `agent_codex_env`，再执行 `agent_codex`。

Codex 的 `backup.yml` 默认在本地连接执行时把备份写到仓库 `tmps/codex-backups/<inventory_hostname>/` 下；如果切到远端主机执行，则回退到各目标文件旁边的默认备份目录。

## 测试

- **框架**: Molecule + Podman（容器镜像 `python:3.13-bookworm`）
- **每个 Role** 均有独立的 `molecule/default/` 测试场景
- **部分 Role 有多场景**: managed_file (`json_sorted`)、npm_command_bootstrap (`auto_install`, `required_false`)
- **测试序列**: dependency → create → prepare → converge → idempotence → verify → destroy
- molecule.yml 中 `roles_path` 使用绝对路径指向项目根的 `roles/`
- `managed_tree` / `agent_claude_code` 的容器测试依赖 `managed_tree_transport: auto` 在 Podman / Docker 连接下自动回退到 archive 模式，不要为了绕过 `synchronize` 限制切回 local/default driver
- `agent_codex` 的验证阶段使用目标端 Python 内置的 `tomllib` 解析 `config.toml`，因此容器/目标主机需要 Python 3.11+

## 开发约定

- Role 的 task 文件按职责拆分（validate、plugins、sync\_\*），通过 `tasks/main.yml` 用 `include_tasks` 编排
- 模板文件放在 `templates/`，Jinja2 渲染
- Role 默认变量在 `defaults/main.yml`，playbook 级归一化逻辑在 playbook 的 `pre_tasks` 中
- `any_errors_fatal = True`：任何任务失败立即终止
- `gathering = explicit`：不自动收集 facts，按需启用
- 在一个 role 里 `include_role` 调下游 role 时，如果需要把当前 role 的模板/文件路径传给下游 role，先用 `set_fact` 固化当前 `role_path`，不要直接把惰性 `{{ role_path }}` 传进去
- `managed_file_confirm` / `managed_json_merge_confirm` / `agent_claude_code_confirm_*` 适用于人工执行时的交互确认；无人值守执行请关闭 confirm 或显式设置 skip_confirm，确认逻辑依赖 `pause` 而不是自定义 TTY 预判
- Codex 的 `.env` 可能包含密钥；如果要开启交互确认，优先只对 `config.toml` 开启，不要默认对 `.env` 打开 diff 确认
