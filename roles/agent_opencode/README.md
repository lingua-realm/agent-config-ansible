# agent_opencode

声明式管理 OpenCode 用户级配置。

## 管理内容

- 检查 `opencode` CLI，并可通过 npm 包 `opencode-ai` 自动安装。
- 渲染 `~/.config/opencode/opencode.json`。
- 可选渲染 `~/.config/opencode/tui.json`。
- 可选同步 `~/.local/share/opencode/managed-secrets/*`、`auth.json`、`mcp-auth.json`。
- 可选同步 OpenCode 资产目录：`agents/`、`commands/`、`modes/`、`plugins/`、`skills/`、`tools/`、`themes/`。

敏感文件不通过 `managed_file` 输出 diff，任务使用 `no_log` 并以 `0600` 权限写入。

## 常用验证

```bash
cd roles/agent_opencode
uv run molecule test
```
