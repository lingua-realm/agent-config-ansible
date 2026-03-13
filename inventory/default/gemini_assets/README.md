# Gemini Assets

这个目录用于存放 `playbooks/setup_gemini_cli.yml` 默认会读取的 Gemini CLI 资产。

目录约定：

- `GEMINI.md`：将同步到目标端 `~/GEMINI.md`

兼容说明：

- 如果文件不存在，对应同步步骤会自动跳过
- 也可以在执行 playbook 时通过额外变量覆盖默认路径
- 这里的 `GEMINI.md` 是同步到目标机的用户级 Gemini 指令文件，不是仓库根目录的 `AGENTS.md`
