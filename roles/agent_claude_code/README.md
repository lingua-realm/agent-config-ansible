# agent_claude_code

复用仓库现有基础 role，为 Claude Code 执行一套完整的自动化配置流程：

- 检查 Claude CLI 与可选的 `ccline`，支持 Claude CLI 缺失时自动安装
- 管理插件 marketplace 与插件安装
- deep merge `~/.claude.json`
- 生成并同步 `~/.claude/settings.json`
- 按需同步外部 `output-styles` 和 `CLAUDE.md`

这个 role 不再内置 `agents`、`output-styles` 目录内容；其中 `output-styles` 需要通过外部路径传入，`skills` 建议改由 `managed_agent_skills` role 统一管理，`agents` 目录完全不管理。

当 `agent_claude_code_verify_schema: true` 时，Schema 校验在控制端执行，因此控制端需要可用的 `check-jsonschema`，并且 `agent_claude_code_settings_schemafile` 指向的 schema 在控制端可访问。

## 依赖的基础 role

- `npm_command_bootstrap`
- `managed_file`
- `managed_json_merge`
- `managed_tree`

## 变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `agent_claude_code_home_dir` | ❌ | `~/.claude` | Claude 配置根目录 |
| `agent_claude_code_user_json_path` | ❌ | `~/.claude.json` | 用户级 claude.json 路径 |
| `agent_claude_code_temp_root` | ❌ | `/tmp/agent-claude-code` | role 工作临时目录 |
| `agent_claude_code_require_claude_cli` | ❌ | `true` | 是否要求 Claude CLI 可用 |
| `agent_claude_code_claude_auto_install` | ❌ | `true` | Claude CLI 不可用时是否自动安装；设为 `false` 则在未找到时直接报错 |
| `agent_claude_code_claude_install_command` | ❌ | `curl -fsSL https://claude.ai/install.sh \| bash` | Claude CLI 自动安装命令；安装失败或安装后仍不可用时 role 会显式报错 |
| `agent_claude_code_require_ccline` | ❌ | `true` | 当 statusLine 使用 ccline 时是否要求 ccline 可用 |
| `agent_claude_code_ccline_auto_install_npm` | ❌ | `@cometix/ccline` | ccline 自动安装时使用的 npm 包名 |
| `agent_claude_code_manage_plugins` | ❌ | `true` | 是否管理插件 marketplace 与插件安装 |
| `agent_claude_code_manage_user_json` | ❌ | `true` | 是否管理 `~/.claude.json` |
| `agent_claude_code_manage_settings` | ❌ | `true` | 是否管理 `settings.json` |
| `agent_claude_code_run_verify` | ❌ | `true` | role 末尾是否执行验证任务 |
| `agent_claude_code_verify_schema` | ❌ | `false` | 是否在控制端执行 `settings.json` JSON Schema 校验；失败会终止 role |
| `agent_claude_code_settings_schemafile` | ❌ | Claude 官方 schema URL | `check-jsonschema --schemafile` 使用的 schema 来源；支持本地文件路径或 URL |
| `agent_claude_code_confirm_settings_update` | ❌ | `false` | settings.json 变更时是否交互确认 |
| `agent_claude_code_confirm_user_json_update` | ❌ | `false` | `~/.claude.json` 变更时是否交互确认 |
| `agent_claude_code_backup` | ❌ | `true` | 是否为托管文件创建备份 |
| `agent_claude_code_backup_root` | ❌ | `""` | 统一备份根目录；设置后会自动派生 `settings/`、`user-json/`、`claude-md/` 子目录 |
| `agent_claude_code_plugin_marketplaces` | ❌ | 内置官方 marketplace | 插件 marketplace 名称到 URL 的映射 |
| `agent_claude_code_plugins_to_install` | ❌ | `[]` | 显式安装的插件列表；为空时回退到 `settings.enabledPlugins` |
| `agent_claude_code_settings` | ✅ | 见 defaults | 用于生成 `settings.json` 的配置对象 |
| `agent_claude_code_user_json` | ❌ | `hasCompletedOnboarding + 空 mcpServers` | 将被 deep merge 到 `~/.claude.json` 的对象 |
| `agent_claude_code_output_styles_src` | ❌ | `""` | 外部 output-styles 目录路径；为空时不管理 |
| `agent_claude_code_claude_md_src` | ❌ | `""` | 外部 `CLAUDE.md` 文件路径；为空时不管理 |
| `agent_claude_code_output_styles_delete` | ❌ | `true` | 同步 output-styles 时是否删除目标端多余文件 |

## `agent_claude_code_settings` 结构

```yaml
agent_claude_code_settings:
  env:
    ANTHROPIC_API_KEY: xxx
    ANTHROPIC_BASE_URL: https://example.com
  model: claude-sonnet-4-5
  alwaysThinkingEnabled: true
  outputStyle: engineer-professional
  language: zh-CN
  permissions:
    defaultMode: default
    allow:
      - Read(*)
      - Edit(*)
    deny: []
  cleanupPeriodDays: 30
  hooks: {}
  enabledPlugins:
    - example-plugin@claude-plugins-official
  statusLine:
    type: command
    command: ccline
    padding: 0
```

## 输出

role 执行完成后会写入 `agent_claude_code_result`：

```yaml
agent_claude_code_result:
  changed: true
  plugins:
    changed: true
    requested:
      - example-plugin@claude-plugins-official
  settings:
    changed: true
    path: /home/user/.claude/settings.json
  user_json:
    changed: true
    path: /home/user/.claude.json
```

## 示例

```yaml
- hosts: all
  tasks:
    - name: 配置 Claude Code
      include_role:
        name: agent_claude_code
      vars:
        agent_claude_code_settings:
          env:
            ANTHROPIC_API_KEY: "{{ vault_anthropic_api_key }}"
            ANTHROPIC_BASE_URL: https://example.com
          model: claude-sonnet-4-5
          alwaysThinkingEnabled: true
          outputStyle: engineer-professional
          language: zh-CN
          permissions:
            defaultMode: default
            allow:
              - Read(*)
              - Edit(*)
            deny: []
          cleanupPeriodDays: 30
          hooks: {}
          enabledPlugins:
            - test-plugin@claude-plugins-official
          statusLine:
            type: command
            command: ccline
            padding: 0
        agent_claude_code_user_json:
          hasCompletedOnboarding: true
          mcpServers:
            local-demo:
              command: node
              args:
                - server.js
        agent_claude_code_output_styles_src: "{{ playbook_dir }}/files/output-styles"
        agent_claude_code_claude_md_src: "{{ playbook_dir }}/files/CLAUDE.md"
```

## 说明

- `output-styles` 必须通过外部路径传入，本 role 不再内置这些目录内容。
- `skills` 不再由本 role 直接同步，建议改用 `managed_agent_skills` role 统一管理。
- 本 role 不管理 `agents` 目录，也不会主动创建它。
- `agent_claude_code_plugins_to_install` 为空时，会自动使用 `agent_claude_code_settings.enabledPlugins` 作为插件安装目标。
- `agent_claude_code_output_styles_src` 会自动归一化为以 `/` 结尾的目录同步语义。
- `agent_claude_code_confirm_settings_update` 和 `agent_claude_code_confirm_user_json_update` 适用于手动执行 playbook 的交互确认；如果是无人值守执行，应保持为 `false`。
- 设置 `agent_claude_code_backup_root` 后，`settings.json`、`~/.claude.json` 和 `CLAUDE.md` 的备份会分别写入其下的 `settings/`、`user-json/`、`claude-md/` 子目录。
