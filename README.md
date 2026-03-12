# agent-config-ansible

基于Ansible一键同步 Claude Code、Codex 等工具的配置

## Playbooks

- `playbooks/setup_claude_code.yml`：部署 Claude Code 配置
- `playbooks/setup_codex.yml`：部署 Codex CLI 配置

## Claude Code 资产目录

`playbooks/setup_claude_code.yml` 默认会从 `inventory/<profile>/claude_assets` 自动发现以下可选资源：

- `output-styles/`
- `CLAUDE.md`

如果这些目录或文件不存在，对应同步步骤会自动跳过；也可以通过 `claude_code_output_styles_src`、`claude_code_claude_md_src` 显式覆盖默认路径。Claude skills 不再由这个 playbook 直接同步，建议改用 `managed_agent_skills` role 统一管理。

## Codex CLI 资产目录

`playbooks/setup_codex.yml` 默认会从 `inventory/<profile>/codex_assets` 自动发现以下可选资源：

- `AGENTS.md`

如果这个文件不存在，对应同步步骤会自动跳过；也可以通过 `codex_agents_md_src` 显式覆盖默认路径。

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
