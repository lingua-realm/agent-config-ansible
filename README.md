# agent-config-ansible

基于Ansible一键同步 Claude Code、Codex、GitHub Copilot CLI 等工具的配置

## Playbooks

- `playbooks/setup_claude_code.yml`：部署 Claude Code 配置
- `playbooks/setup_codex.yml`：部署 Codex CLI 配置
- `playbooks/setup_copilot_cli.yml`：部署 GitHub Copilot CLI 的 MCP 配置
- `playbooks/setup_agent_skills.yml`：声明式管理 Claude Code、Codex 等 agent 的 skills

## Agent Skills 变量目录

`playbooks/setup_agent_skills.yml` 默认会从 `inventory/<profile>/group_vars/all/agent_skills/` 读取以下变量文件：

- `settings.yml`
- `items.yml`

如果你希望在 inventory 里维护本地 skills 源目录，可以约定放在 `inventory/<profile>/agent_skills_assets/`，然后在 `items.yml` 里的 `source` 中引用对应路径。

注意 `source` 必须在目标机上可见：`ansible_connection=local` 时可以直接引用仓库路径；远端主机场景更建议使用 GitHub shorthand、Git URL，或者目标机上已有的本地路径。

## 共享 MCP 变量目录

`playbooks/setup_claude_code.yml` 和 `playbooks/setup_codex.yml` 默认会从 `inventory/<profile>/group_vars/all/agent_mcps/` 读取共享 MCP 定义。

- `servers.yml`

其中 `agent_mcps` 使用统一结构维护 MCP 服务器，Claude Code 会直接渲染为 `mcpServers`，Codex 会在编排层自动转换为 `mcp_servers` 所需格式，GitHub Copilot CLI 会转换为 `~/.copilot/mcp-config.json` 所需的 `mcpServers` 结构。

如果你需要 agent 特有差异，仍然可以在以下文件里按同名服务做覆盖：

- `group_vars/all/claude_code/mcp_servers.yml`
- `group_vars/all/codex/mcp_servers.yml`
- `group_vars/all/copilot_cli/mcp_servers.yml`

## GitHub Copilot CLI 变量目录

`playbooks/setup_copilot_cli.yml` 默认会从 `inventory/<profile>/group_vars/all/copilot_cli/` 读取以下变量文件：

- `backup.yml`
- `settings.yml`
- `mcp_servers.yml`

当前 Copilot CLI 编排只管理 `~/.copilot/mcp-config.json`，主要用于把共享 `agent_mcps` 自动转换成 Copilot CLI 可识别的 MCP 配置；不负责模型、账号或其他 CLI 设置。

## Claude Code 资产目录

`playbooks/setup_claude_code.yml` 默认会从 `inventory/<profile>/claude_assets` 自动发现以下可选资源：

- `output-styles/`
- `CLAUDE.md`

如果这些目录或文件不存在，对应同步步骤会自动跳过；也可以通过 `claude_code_output_styles_src`、`claude_code_claude_md_src` 显式覆盖默认路径。Claude skills 不再由这个 playbook 直接同步，建议改用 `managed_agent_skills` role 统一管理。

## Codex CLI 资产目录

`playbooks/setup_codex.yml` 默认会从 `inventory/<profile>/codex_assets` 自动发现以下可选资源：

- `AGENTS.md`

如果这个文件不存在，对应同步步骤会自动跳过；也可以通过 `codex_agents_md_src` 显式覆盖默认路径。

## GitHub Copilot CLI 备份目录

`playbooks/setup_copilot_cli.yml` 在本地连接执行时，默认会把 `mcp-config.json` 的备份写到当前仓库的 `tmps/copilot-cli-backups/<inventory_hostname>/` 下。

默认子目录如下：

- `mcp-config/`

如果你要改到别的目录，可以覆盖 `copilot_cli_backup_root`；远端主机场景下默认不会强行写到仓库路径，而是回退到目标文件旁边的默认备份目录。

## Claude Code 备份目录

`playbooks/setup_claude_code.yml` 在本地连接执行时，默认会把 `settings.json`、`~/.claude.json` 和 `CLAUDE.md` 的备份写到当前仓库的 `tmps/claude-code-backups/<inventory_hostname>/` 下。

默认子目录如下：

- `settings/`
- `user-json/`
- `claude-md/`

如果你要改到别的目录，可以覆盖 `claude_code_backup_root`；远端主机场景下默认不会强行写到仓库路径，而是回退到目标文件旁边的默认备份目录。

## Codex CLI 备份目录

`playbooks/setup_codex.yml` 在本地连接执行时，默认会把 `config.toml`、`~/.codex/.env` 和 `AGENTS.md` 的备份写到当前仓库的 `tmps/codex-backups/<inventory_hostname>/` 下。

默认子目录如下：

- `config/`
- `env/`
- `agents-md/`

如果你要改到别的目录，可以覆盖 `codex_backup_root`；远端主机场景下默认不会强行写到仓库路径，而是回退到目标文件旁边的默认备份目录。
