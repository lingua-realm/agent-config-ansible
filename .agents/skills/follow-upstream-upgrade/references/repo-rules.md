# Follow Upstream Upgrade Repo Rules

- Use `private-config` as the maintained user branch.
- Treat `inventory/default/` as the upstream template, not the long-term user environment.
- Review `README.md`, root `AGENTS.md`, and `inventory/default/` changes before applying upgrades.
- Run `--syntax-check` before local apply.
- Prefer only affected playbooks and local scope verification.
- Do not auto-commit, auto-push, or modify user profile files directly.
