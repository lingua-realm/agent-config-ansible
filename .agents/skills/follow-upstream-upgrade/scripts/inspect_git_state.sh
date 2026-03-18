#!/usr/bin/env bash

set -euo pipefail

repo_root="${1:-.}"
upstream_remote="${2:-upstream}"
target_branch="${3:-private-config}"

current_branch="$(git -C "${repo_root}" branch --show-current 2>/dev/null || true)"
worktree_status="$(git -C "${repo_root}" status --porcelain 2>/dev/null || true)"

ok="true"
reason=""

if [[ -n "${worktree_status}" ]]; then
  ok="false"
  reason="dirty_worktree"
elif ! git -C "${repo_root}" remote get-url "${upstream_remote}" >/dev/null 2>&1; then
  ok="false"
  reason="missing_remote"
elif ! git -C "${repo_root}" rev-parse --verify "${target_branch}" >/dev/null 2>&1; then
  ok="false"
  reason="missing_target_branch"
fi

python3 - "${ok}" "${reason}" "${current_branch}" "${target_branch}" "${upstream_remote}" <<'PY'
import json
import sys

ok = sys.argv[1] == "true"
reason = sys.argv[2] or None
current_branch = sys.argv[3] or None
target_branch = sys.argv[4]
upstream_remote = sys.argv[5]

print(
    json.dumps(
        {
            "ok": ok,
            "reason": reason,
            "current_branch": current_branch,
            "target_branch": target_branch,
            "upstream_remote": upstream_remote,
        },
        ensure_ascii=False,
    )
)
PY

if [[ "${ok}" != "true" ]]; then
  exit 1
fi
