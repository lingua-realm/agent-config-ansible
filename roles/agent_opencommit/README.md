# agent_opencommit

复用仓库现有基础 role，为 OpenCommit CLI 执行一套完整的自动化配置流程：

- 检查可选的 OpenCommit CLI 可用性
- 生成并同步 `~/.opencommit`

## 依赖的基础 role

- `npm_command_bootstrap`
- `managed_file`

## 变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `agent_opencommit_home_dir` | ❌ | `~` | OpenCommit 所属用户目录 |
| `agent_opencommit_config_path` | ❌ | `~/.opencommit` | OpenCommit 全局配置文件路径 |
| `agent_opencommit_temp_root` | ❌ | `/tmp/agent-opencommit` | role 工作临时目录 |
| `agent_opencommit_require_opencommit_cli` | ❌ | `true` | 是否要求 OpenCommit CLI 可用 |
| `agent_opencommit_opencommit_auto_install_npm` | ❌ | `opencommit` | OpenCommit CLI 自动安装时使用的 npm 包名 |
| `agent_opencommit_manage_config` | ❌ | `true` | 是否管理 `~/.opencommit` |
| `agent_opencommit_run_verify` | ❌ | `true` | role 末尾是否执行验证任务 |
| `agent_opencommit_confirm_config_update` | ❌ | `false` | `~/.opencommit` 变更时是否交互确认 |
| `agent_opencommit_backup` | ❌ | `true` | 是否为托管文件创建备份 |
| `agent_opencommit_backup_root` | ❌ | `""` | 统一备份根目录；设置后会自动派生 `config/` 子目录 |
| `agent_opencommit_config` | ❌ | `{}` | 用于生成 `~/.opencommit` 的配置对象 |

## 输出

role 执行完成后会写入 `agent_opencommit_result`：

```yaml
agent_opencommit_result:
  changed: true
  config:
    changed: true
    path: /home/user/.opencommit
```

## 示例

```yaml
- hosts: all
  tasks:
    - name: 配置 OpenCommit CLI
      include_role:
        name: agent_opencommit
      vars:
        agent_opencommit_config:
          OCO_AI_PROVIDER: openai
          OCO_API_URL: https://api.ppio.com/openai/v1
          OCO_API_KEY: "{{ vault_ppio_api_key }}"
          OCO_MODEL: pa/gpt-5.4
          OCO_EMOJI: true
          OCO_DESCRIPTION: false
          OCO_LANGUAGE: zh-CN
```

## 说明

- `~/.opencommit` 使用按键排序的 `KEY=JSON_VALUE` 形式渲染，既能保留布尔/数字类型，也能安全写入字符串与 JSON 对象。
- `agent_opencommit_confirm_config_update` 适用于手动执行 playbook 的交互确认；如果是无人值守执行，应保持为 `false`。
- 设置 `agent_opencommit_backup_root` 后，`~/.opencommit` 的备份会写入其下的 `config/` 子目录。
