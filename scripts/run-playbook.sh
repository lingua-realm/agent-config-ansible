#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat >&2 <<'EOF'
用法: scripts/run-playbook.sh <profile> <playbook_relative_path> [extra ansible-playbook args...]
示例: scripts/run-playbook.sh default playbooks/setup_codex.yml -e target_hosts=all
EOF
}

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

profile="$1"
playbook_rel="$2"
shift 2

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
inventory_path="${repo_root}/inventory/${profile}/inventory.yml"

if [[ ! -f "${inventory_path}" ]]; then
  printf '错误: 未找到 profile inventory: %s\n' "${inventory_path}" >&2
  exit 1
fi

if [[ "${playbook_rel}" = /* ]]; then
  printf '错误: playbook 必须使用仓库内相对路径: %s\n' "${playbook_rel}" >&2
  exit 1
fi

if [[ "${playbook_rel}" == ".." || "${playbook_rel}" == ../* || "${playbook_rel}" == */../* || "${playbook_rel}" == */.. ]]; then
  printf '错误: playbook 路径不能跳出仓库根目录: %s\n' "${playbook_rel}" >&2
  exit 1
fi

playbook_path="${repo_root}/${playbook_rel}"

if [[ ! -f "${playbook_path}" ]]; then
  printf '错误: 未找到 playbook: %s\n' "${playbook_path}" >&2
  exit 1
fi

cd -- "${repo_root}"
export ANSIBLE_INVENTORY="${inventory_path}"
exec uv run ansible-playbook "${playbook_rel}" "$@"
