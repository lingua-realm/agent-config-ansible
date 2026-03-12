# managed_agent_skills

基于 skills CLI 声明式管理 agent skills 的安装与卸载。

这个 role 的设计目标是把 skills CLI 的 add/remove/list 封装成幂等的 Ansible 任务，而不是直接同步某个 agent 的 `skills/` 目录。

## 依赖

- `npm_command_bootstrap`
- 目标机上可用的 Node.js / npm 环境

## 变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `managed_agent_skills_items` | ✅ | `[]` | 声明式 skills 条目列表 |
| `managed_agent_skills_cli_command` | ❌ | `skills` | skills CLI 命令名 |
| `managed_agent_skills_cli_version_command` | ❌ | `skills --version` | 获取 skills CLI 版本的命令 |
| `managed_agent_skills_auto_install_npm` | ❌ | `skills` | CLI 不存在时用于自动安装的 npm 包名；设为空字符串可关闭自动安装 |
| `managed_agent_skills_require_cli` | ❌ | `true` | 是否要求 skills CLI 可用 |
| `managed_agent_skills_disable_telemetry` | ❌ | `true` | 是否默认注入 `DISABLE_TELEMETRY=1` 和 `DO_NOT_TRACK=1` |
| `managed_agent_skills_command_env` | ❌ | `{}` | 传给所有 skills CLI 调用的额外环境变量 |
| `managed_agent_skills_project_dir` | ❌ | `""` | project scope 的默认工作目录 |
| `managed_agent_skills_universal_agents` | ❌ | 当前内置 universal agents 列表 | 走 `.agents/skills` 共享目录的 agent 标识列表 |

## 条目结构

每个条目支持以下字段：

| 字段 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `name` | ❌ | `""` | 可读名称，仅用于结果汇总 |
| `state` | ❌ | `present` | `present` 或 `absent` |
| `source` | `present` 时必填 | `""` | skills 来源；可以是 GitHub shorthand、Git URL 或目标机上的本地路径 |
| `skills` | ✅ | `[]` | 要安装或卸载的 skill 名称列表 |
| `agents` | ✅ | `[]` | 目标 agent 列表；`present` 必须显式列出，`absent` 可使用 `['*']` |
| `scope` | ❌ | `global` | `global` 或 `project` |
| `mode` | ❌ | `symlink` | `symlink` 或 `copy`，仅对 `present` 生效 |
| `project_dir` | `scope=project` 时必填 | 继承 `managed_agent_skills_project_dir` | project scope 对应的工作目录 |
| `env` | ❌ | `{}` | 仅对当前条目生效的额外环境变量 |

## 当前限制

- `present` 只支持显式 skill 名称列表，不支持 `skills: ['*']`。这是为了保证幂等性，不去解析 `skills add --list` 的人类可读输出。
- `present` 只支持显式 agent 列表，不支持 `agents: ['*']`。这是为了避免把自动检测结果当成声明式状态的一部分。
- `source` 是在目标机上执行 `skills add` 时可见的来源。如果你在远端主机上运行 playbook，本地控制端路径不会自动复制过去。

## 输出

role 执行完成后会写入 `managed_agent_skills_result`：

```yaml
managed_agent_skills_result:
  changed: true
  cli:
    available: true
    path: /usr/local/bin/skills
    version: 1.4.4
  items:
    - name: frontend-design@global
      state: present
      scope: global
      mode: symlink
      source: vercel-labs/agent-skills
      skills:
        - frontend-design
      agents:
        - claude-code
        - codex
      changed: true
      action: add
```

## 示例

```yaml
- hosts: localhost
  gather_facts: false
  tasks:
    - name: 声明式管理常用 skills
      include_role:
        name: managed_agent_skills
      vars:
        managed_agent_skills_items:
          - name: 安装全局 frontend skill
            state: present
            source: vercel-labs/agent-skills
            skills:
              - frontend-design
            agents:
              - claude-code
              - codex
            scope: global

          - name: 安装项目级 release-notes skill
            state: present
            source: /path/to/local-skills
            skills:
              - release-notes
            agents:
              - claude-code
            scope: project
            project_dir: /path/to/project
            mode: copy

          - name: 卸载遗留 skill
            state: absent
            skills:
              - legacy-skill
            agents:
              - codex
            scope: global
```

## 实现说明

- role 基于 `skills list` 的文本输出做幂等探测；对于走 `.agents/skills` 的 universal agents，会额外探测共享目录中的 skill 名称，避免被 CLI 的 `not linked` 输出误判。
- `global` 和 `project` 的实际 canonical 路径不由 role 自己推导，统一交给 skills CLI 负责。
- 如果你已经在别处用文件同步直接管理某个 agent 的 `skills/` 目录，不要和这个 role 混用到同一目标目录。
