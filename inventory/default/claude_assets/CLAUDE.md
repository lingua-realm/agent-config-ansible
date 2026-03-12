# 全局规范

总是使用中文回答

## 工具使用约定

- 网络搜索：优先使用 `mcp__open-websearch__search` 工具替代 `WebSearch` 工具

## Skills 使用约定

- **全局 Skills**：位于 `~/.claude/skills/`，在任何项目中都可用
- **项目级 Skills**：位于项目根目录的 `.claude/skills/`，仅在当前项目中可用
- 调用方式：`/skill-name`（自动优先使用项目级，如不存在则使用全局）

## Git 提交规范

遵循 Conventional Commits 格式：

- `feat(scope): 新增功能`
- `fix(scope): 修复缺陷`
- `docs(scope): 文档更新`
- `refactor(scope): 代码重构`
- `chore(scope): 杂务维护`
