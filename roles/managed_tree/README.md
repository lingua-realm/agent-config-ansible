# managed_tree

将控制端的目录树同步到目标端目录，底层使用 `ansible.posix.synchronize`。适合分发一整组配置文件、脚本或模板产物，而不是单个文件。

这个 role 只处理“控制端 -> 目标端”的同步场景，并在执行前显式检查源目录和两端的 `rsync` 是否可用。

## 变量

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `managed_tree_display_name` | ❌ | `managed tree` | 可读名称，用于日志输出 |
| `managed_tree_src` | ✅ | `""` | 控制端源目录路径 |
| `managed_tree_dest` | ✅ | `""` | 目标端目录路径 |
| `managed_tree_transport` | ❌ | `auto` | 传输方式：`auto`、`rsync`、`archive` |
| `managed_tree_delete` | ❌ | `true` | 是否删除目标端多余文件 |
| `managed_tree_archive` | ❌ | `true` | 是否启用 rsync archive 模式 |
| `managed_tree_recursive` | ❌ | `true` | 是否递归同步目录 |
| `managed_tree_checksum` | ❌ | `false` | 是否基于 checksum 判断差异 |
| `managed_tree_compress` | ❌ | `true` | 传输时是否压缩 |
| `managed_tree_dirs` | ❌ | `false` | 是否仅同步目录条目，不递归内容 |
| `managed_tree_directory_mode` | ❌ | `0755` | 同步前确保目标目录存在时使用的权限 |
| `managed_tree_rsync_timeout` | ❌ | `0` | rsync 超时秒数，`0` 表示不限制 |
| `managed_tree_rsync_opts` | ❌ | `[]` | 额外透传给 rsync 的选项列表 |
| `managed_tree_local_archive_path` | ❌ | `/tmp/managed-tree-...tar` | archive 模式下控制端临时 tar 包路径 |
| `managed_tree_remote_archive_path` | ❌ | `/tmp/managed-tree-...tar` | archive 模式下目标端临时 tar 包路径 |
| `managed_tree_remote_extract_path` | ❌ | `/tmp/managed-tree-...extract` | archive 模式下目标端临时解包目录 |

## 输出

role 执行完成后会写入 `managed_tree_result`：

```yaml
managed_tree_result:
  changed: true
  src: /path/to/source-tree/
  dest: ~/.config/agent
  transport: rsync
  archive: true
  recursive: true
  delete: true
  checksum: false
```

## 示例

```yaml
- hosts: all
  tasks:
    - name: 同步 agent 配置目录
      include_role:
        name: managed_tree
      vars:
        managed_tree_display_name: Agent 配置目录
        managed_tree_src: "{{ playbook_dir }}/files/agent-config/"
        managed_tree_dest: ~/.config/agent
        managed_tree_delete: true
        managed_tree_rsync_opts:
          - --exclude=.DS_Store
```

## 说明

- 该 role 依赖控制端和目标端都已安装 `rsync`。
- `managed_tree_transport: auto` 默认在普通主机连接下使用 `rsync`，在 `podman` / `docker` 这类容器连接下自动回退到 `archive` 方式，避免 `synchronize` 走 ssh 失败。
- `archive` 模式目前不支持 `managed_tree_dirs=true` 或额外 `managed_tree_rsync_opts`。
- `managed_tree_src` 的尾部是否带 `/` 会影响 rsync 语义：带 `/` 时同步目录内容，不带 `/` 时会把目录本身一并复制过去。
- 这个 role 不做交互确认、备份和 diff 预览；如果你只需要管理单个文件，优先使用 `managed_file`。
