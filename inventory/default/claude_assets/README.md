# Claude Assets

这个目录用于存放 `playbooks/setup_claude_code.yml` 默认会读取的 Claude Code 资产。

目录约定：

- `skills/`：将同步到目标端 `~/.claude/skills/`
- `output-styles/`：将同步到目标端 `~/.claude/output-styles/`
- `CLAUDE.md`：将同步到目标端 `~/.claude/CLAUDE.md`

兼容说明：

- 如果某个目录或文件不存在，对应同步步骤会自动跳过
- 也可以在执行 playbook 时通过额外变量覆盖这些默认路径
