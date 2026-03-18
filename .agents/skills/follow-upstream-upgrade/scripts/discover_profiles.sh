#!/usr/bin/env bash

set -euo pipefail

repo_root="${1:-.}"
inventory_root="${repo_root}/inventory"

if [[ ! -d "${inventory_root}" ]]; then
  printf '{"profiles":[]}\n'
  exit 0
fi

tmp_file="$(mktemp)"
trap 'rm -f "${tmp_file}"' EXIT

while IFS= read -r -d '' inventory_file; do
  profile_dir="$(dirname "${inventory_file}")"
  profile_name="$(basename "${profile_dir}")"
  if [[ "${profile_name}" != "default" ]]; then
    printf '%s\n' "${profile_name}" >> "${tmp_file}"
  fi
done < <(find "${inventory_root}" -mindepth 2 -maxdepth 2 -type f -name 'inventory.yml' -print0 | sort -z)

python3 - "${tmp_file}" <<'PY'
import json
import sys
from pathlib import Path

lines = []
path = Path(sys.argv[1])
if path.exists():
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

print(json.dumps({"profiles": lines}, ensure_ascii=False))
PY
