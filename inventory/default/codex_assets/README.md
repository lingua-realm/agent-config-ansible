# Codex 资产目录

`playbooks/setup_codex.yml` 默认会从当前 inventory 的 `codex_assets/` 目录自动发现以下可选资源：

- `AGENTS.md`：同步到 `~/.codex/AGENTS.md`

如果资源不存在，对应同步步骤会自动跳过；也可以通过 `codex_agents_md_src` 显式覆盖默认路径。
