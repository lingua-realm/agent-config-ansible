# agent-config-ansible

基于 Ansible 的 AI Agent 配置管理仓库，用来把 Claude Code、Codex CLI、Gemini CLI、GitHub Copilot CLI、Cursor 以及 agent skills 以声明式方式同步到本地或远端主机。

## 管理范围

| Playbook                           | 作用                                                          |
| ---------------------------------- | ------------------------------------------------------------- |
| `playbooks/setup_claude_code.yml`  | 部署 Claude Code 的设置、用户级 JSON、插件与可选资产          |
| `playbooks/setup_codex.yml`        | 部署 Codex CLI 的 `config.toml`、`.env` 与可选 `AGENTS.md`    |
| `playbooks/setup_gemini_cli.yml`   | 部署 Gemini CLI 的 `settings.json`、`.env` 与可选 `GEMINI.md` |
| `playbooks/setup_copilot_cli.yml`  | 部署 GitHub Copilot CLI 的 `~/.copilot/mcp-config.json`       |
| `playbooks/setup_cursor.yml`       | 部署 Cursor / Cursor Agent CLI 共用的 `~/.cursor/mcp.json`    |
| `playbooks/setup_agent_skills.yml` | 通过 `skills` CLI 声明式安装或卸载 skills                     |

## 快速开始

### 0. 准备仓库

先克隆仓库到本地：

```bash
# 克隆上游仓库
git clone git@github.com/lingua-realm:agent-config-ansible.git

# 修改remote源为upstream，方便后续拉取更新
git remote rename origin upstream

# 创建一个自己的私有git仓库，用于后续创建自己的分支和提交自己的配置
GITHUB_USERNAME=$(gh api user --jq .login)
gh repo create $GITHUB_USERNAME/agent-config-ansible --private --source=. --remote=origin

# 创建并切换到自己的分支，后续提交都在这个分支上
git checkout -b private-config

# 推送到自己的远程仓库
git push -u origin private-config
```

### 1. 安装依赖

```bash
uv sync --dev
```

### 2. 准备 inventory

`inventory/default/` 是默认示例。实际使用时，建议复制出自己的 profile，例如 `inventory/personal/` 或 `inventory/work/`。

常见结构如下：

```text
inventory/<profile>/
├── inventory.yml
├── group_vars/all/
│   ├── agent_mcps/
│   ├── agent_skills/
│   ├── claude_code/
│   ├── codex/
│   ├── gemini_cli/
│   ├── copilot_cli/
│   ├── cursor/
│   └── secrets.yml
├── claude_assets/
├── codex_assets/
├── gemini_assets/
└── agent_skills_assets/
```

使用建议：

- 共享 MCP 默认值放在 `group_vars/all/agent_mcps/servers.yml`。
- 某个工具的差异化配置放在对应目录下的 `mcp_servers.yml`。
- API Key、token 等敏感信息放在 `group_vars/all/secrets.yml` 或 CI Secret，不要写进说明资产。
- `confirm`、备份目录、CLI 检查、自动安装、`manage_*`、`run_verify` 这类运行控制默认已内置，只有需要覆盖时再显式声明。
- Codex CLI 会把本地信任目录写进 `~/.codex/config.toml` 的 `[projects]` 段；`setup_codex.yml` 会保留目标机现有的本地 `projects` 状态，避免这些路径造成声明式配置漂移，因此无需把它们写进 inventory。

> 仓库根目录的 `AGENTS.md` 是给本仓库维护者和 AI 代理看的；`inventory/<profile>/codex_assets/AGENTS.md` 是要同步到目标机的 Codex 指令文件，两者不是同一个文件。

### 3. 运行 playbook

默认情况下，`ansible.cfg` 会使用 `inventory/default/inventory.yml`，因此可以直接执行：

```bash
uv run ansible-playbook playbooks/setup_claude_code.yml
uv run ansible-playbook playbooks/setup_codex.yml
uv run ansible-playbook playbooks/setup_gemini_cli.yml
uv run ansible-playbook playbooks/setup_copilot_cli.yml
uv run ansible-playbook playbooks/setup_cursor.yml
uv run ansible-playbook playbooks/setup_agent_skills.yml
```

如果要显式指定 profile，使用仓库脚本：

```bash
scripts/run-playbook.sh personal playbooks/setup_codex.yml
scripts/run-playbook.sh personal playbooks/setup_cursor.yml -e "target_hosts=all"
```

这个脚本的两个必填参数分别是：

- `profile`，对应 `inventory/<profile>/inventory.yml`
- playbook 相对路径，例如 `playbooks/setup_gemini_cli.yml`

### 4. 推荐使用方式

- 把 `inventory/default/` 当作模板，而不是长期直接修改的唯一环境。
- 优先按单个工具执行，再决定是否加上 `-e "target_hosts=all"`。
- 只改了某一个 agent，就只跑对应 playbook，没有必要每次全量执行。
- 首次落地或大改前，先确认备份目录和目标输出是否符合预期。

## 常用检查

```bash
uv run ansible-playbook --syntax-check playbooks/setup_codex.yml

cd roles/agent_codex
uv run molecule test
```

## 更多说明

- 仓库架构、变量归一化、CI、测试边界、升级注意事项见根目录 `AGENTS.md`。
- 更具体的变量示例和资产样例见 `inventory/default/`。
