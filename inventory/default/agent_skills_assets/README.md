# Agent Skills Assets

这个目录用于存放 inventory 级本地 skills 源目录，供 `group_vars/all/agent_skills/items.yml` 中的 `source` 引用。

示例：

```yaml
agent_skills_items:
  - name: 安装本地 skill
    state: present
    source: "{{ inventory_dir }}/agent_skills_assets/custom-skills"
    skills:
      - release-notes
    agents:
      - claude-code
    scope: global
```

注意事项：

- `source` 必须在执行 `skills add` 的目标机上可见。
- 对于 `ansible_connection=local`，本目录可以直接作为 `source`。
- 对于远端主机，更稳妥的做法是使用 GitHub shorthand、Git URL，或者目标机上已有的本地路径。
