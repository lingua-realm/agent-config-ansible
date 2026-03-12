# agent-config-ansible

基于Ansible一键同步claude code/codex/...等工具的配置

## Claude Code 资产目录

`playbooks/setup_claude_code.yml` 默认会从 `inventory/<profile>/claude_assets` 自动发现以下可选资源：

- `skills/`
- `output-styles/`
- `CLAUDE.md`

如果这些目录或文件不存在，对应同步步骤会自动跳过；也可以通过 `claude_code_skills_src`、`claude_code_output_styles_src`、`claude_code_claude_md_src` 显式覆盖默认路径。

## Claude Code 备份目录

`playbooks/setup_claude_code.yml` 在本地连接执行时，默认会把 `settings.json`、`~/.claude.json` 和 `CLAUDE.md` 的备份写到当前仓库的 `tmps/claude-code-backups/<inventory_hostname>/` 下。

默认子目录如下：

- `settings/`
- `user-json/`
- `claude-md/`

如果你要改到别的目录，可以覆盖 `claude_code_backup_root`；远端主机场景下默认不会强行写到仓库路径，而是回退到目标文件旁边的默认备份目录。
