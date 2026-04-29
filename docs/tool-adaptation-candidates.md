# 候选适配工具研究

这份清单不是在做“通用 AI 工具排行榜”，而是站在**本仓库现有架构**上，评估哪些工具更适合继续纳入声明式配置管理。

当前仓库最擅长的场景是：

- 有明确的 CLI 或至少有稳定的用户级配置目录
- 配置可以落到 JSON / TOML / YAML / Markdown / `.env`
- 敏感信息可以通过 inventory 或环境变量注入
- 最好能把 MCP、模型、提示词资产拆成声明式文件
- 最好支持无人值守校验，而不是必须依赖 GUI 登录或编辑器运行态

## 当前已适配的工具

- Claude Code
- Codex CLI
- Gemini CLI
- GitHub Copilot CLI（当前只管理 MCP 配置）
- Cursor（当前只管理 MCP 配置）
- agent skills

## 评估标准

### 优先级高

满足越多，越适合优先适配：

1. **终端优先**：有独立 CLI，可以在本地或 CI 中无头执行
2. **配置稳定**：有清晰、文档化的配置文件路径和 schema
3. **密钥解耦**：支持环境变量或 `.env` 注入 API Key / token
4. **MCP 友好**：原生支持 MCP，或至少有稳定的 tools / extension 配置
5. **易于验证**：支持 `--version`、配置检查或最小功能验证
6. **自动化安装友好**：npm / Homebrew / 官方二进制安装流程清晰

### 优先级低

下面这些特征会显著拉低适配收益：

- 主要以编辑器插件存在，没有稳定 CLI
- 配置强依赖 GUI 登录态、云端工作区或扩展市场
- 用户本地状态很多，难以做到声明式同步
- 缺少稳定的配置 schema 或无头验证路径

## 候选工具结论

| 工具 | 结论 | 适配理由 | 主要阻碍 |
| --- | --- | --- | --- |
| OpenCode | **最高优先级** | 终端优先、配置结构清晰、原生 MCP、整体形态最接近本仓库现有模式 | 需要新增一套 playbook / role / inventory 命名约定 |
| Goose CLI | **高优先级** | CLI 与共享配置明确，MCP/extension 能力强，适合声明式同步 | 安装方式与当前 npm bootstrap 模式不完全一致 |
| Continue | **中优先级** | `config.yaml`、models、prompts、`mcpServers` 都适合做配置管理 | 更偏编辑器生态，而不是纯 CLI 工具 |
| Aider | **中优先级** | `.aider.conf.yml` + `.env` 非常适合托管，模型供应商灵活 | 没有像当前几类工具那样突出的 MCP 主线，且安装生态偏 Python |
| Cline / Roo Code / Windsurf 一类编辑器扩展 | **暂不优先** | 用户群体大，但更多是编辑器插件配置 | GUI/账号/扩展运行态较重，和本仓库的 CLI-first 设计不够贴合 |

## 为什么优先推荐 OpenCode

如果只选一个新工具开始落地，优先建议 **OpenCode**：

- 它和当前已支持的 Claude Code / Codex CLI / Gemini CLI 一样，都是**终端优先**的交互模式
- 原生支持 MCP，和仓库现有 `agent_mcps` 的分层思路最接近
- 配置更像“可渲染、可合并、可验证”的声明式文件，而不是强绑定 GUI 状态
- 后续如果要支持共享 MCP 默认值、profile 覆盖、用户级资产，迁移心智成本最低

## 第二梯队为什么是 Goose CLI

**Goose CLI** 也值得优先考虑，原因是：

- 有稳定的 CLI 入口和共享配置
- MCP / extension 能力比较强，适合接入本仓库已经存在的 MCP 分层模型
- 文档里明确提到了 CI/CD 和版本固定场景，比较适合自动化部署

它没有排在第一，主要是因为当前仓库的 CLI 自安装能力更偏向 npm，而 Goose 的安装与验证路径需要补一层新的通用 bootstrap 设计。

## 为什么 Continue 和 Aider 放在中优先级

### Continue

Continue 的配置能力其实很强，尤其是：

- `config.yaml`
- models / prompts / docs / rules
- `mcpServers`

这些都很适合声明式管理。

但它的主要使用形态仍然更偏向编辑器插件和 agent 配置，而不是像当前仓库已支持工具那样天然以“独立 CLI + 用户主目录配置”为中心，所以更适合放在第二阶段评估。

### Aider

Aider 的优点是：

- CLI 稳定
- `.aider.conf.yml` 与 `.env` 很适合 managed file
- 对模型供应商的兼容性很好

但从本仓库视角看，它更像一个“多模型 coding CLI”，而不是一个以 MCP / tools 配置为中心的 agent 入口；同时如果要把“自动安装”也纳入仓库职责，还需要补齐 Python 生态下的 bootstrap 方案。

## 建议的落地顺序

建议按下面顺序推进，而不是同时开很多坑：

1. **OpenCode**
2. **Goose CLI**
3. **Continue**
4. **Aider**

## 如果真的开始做新适配，建议复用的仓库模式

无论选哪一个工具，尽量沿用现有骨架：

```text
playbooks/setup_<tool>.yml
roles/agent_<tool>/
inventory/<profile>/group_vars/all/<tool>/
inventory/<profile>/<tool>_assets/
```

并尽量复用现有能力：

- 单文件渲染：`managed_file`
- JSON deep merge：`managed_json_merge`
- 目录树同步：`managed_tree`
- CLI 安装与检查：复用或扩展 `npm_command_bootstrap`

## 一句话结论

如果目标是**用最小新增复杂度，继续扩展这个仓库的工具覆盖面**，下一步最值得做的是：

1. 先做 **OpenCode**
2. 再看 **Goose CLI**
3. Continue / Aider 放在后续补位
