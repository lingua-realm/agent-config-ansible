#!/usr/bin/env bash

set -euo pipefail

repo_root="${1:-.}"
upstream_remote="${2:-upstream}"
upstream_branch="${3:-main}"
target_branch="${4:-private-config}"
upgrade_branch="${5:-upgrade/$(date +%F)-upstream-sync}"
output_dir="${6:-${repo_root}/tmps/upstream-upgrade/$(date +%Y%m%d-%H%M%S)}"

mkdir -p "${output_dir}"

merge_log="$(mktemp)"
trap 'rm -f "${merge_log}"' EXIT

current_branch_before="$(git -C "${repo_root}" branch --show-current)"
target_head="$(git -C "${repo_root}" rev-parse "${target_branch}")"

status="ok"
reason=""
ok="true"

if ! git -C "${repo_root}" fetch "${upstream_remote}" "${upstream_branch}" >"${merge_log}" 2>&1; then
  status="failed"
  reason="fetch_failed"
  ok="false"
else
  git -C "${repo_root}" checkout "${target_branch}" >>"${merge_log}" 2>&1
  git -C "${repo_root}" checkout -B "${upgrade_branch}" "${target_branch}" >>"${merge_log}" 2>&1

  if ! git -C "${repo_root}" merge --no-edit "${upstream_remote}/${upstream_branch}" >>"${merge_log}" 2>&1; then
    status="failed"
    reason="merge_conflict"
    ok="false"
  fi
fi

current_branch_after="$(git -C "${repo_root}" branch --show-current)"
head_after="$(git -C "${repo_root}" rev-parse HEAD)"
target_head_after="$(git -C "${repo_root}" rev-parse "${target_branch}")"

python3 - \
  "${repo_root}" \
  "${output_dir}" \
  "${ok}" \
  "${status}" \
  "${reason}" \
  "${current_branch_before}" \
  "${current_branch_after}" \
  "${target_branch}" \
  "${target_head}" \
  "${upgrade_branch}" \
  "${upstream_remote}" \
  "${upstream_branch}" \
  "${head_after}" \
  "${target_head_after}" \
  "${merge_log}" <<'PY'
import json
import subprocess
import sys
from pathlib import Path


def git(repo_root: str, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", repo_root, *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


(
    repo_root,
    output_dir,
    ok_raw,
    status,
    reason,
    current_branch_before,
    current_branch_after,
    target_branch,
    target_head,
    upgrade_branch,
    upstream_remote,
    upstream_branch,
    head_after,
    target_head_after,
    merge_log,
) = sys.argv[1:]

ok = ok_raw == "true"

if ok:
    changed_files = [
        line for line in git(repo_root, "diff", "--name-only", f"{target_branch}..HEAD").splitlines() if line
    ]
else:
    changed_files = [
        line for line in git(repo_root, "diff", "--name-only", "--diff-filter=U").splitlines() if line
    ]

summary = {
    "ok": ok,
    "status": status,
    "reason": reason or None,
    "current_branch_before": current_branch_before,
    "current_branch_after": current_branch_after,
    "target_branch": target_branch,
    "target_head": target_head,
    "target_head_after": target_head_after,
    "upgrade_branch": upgrade_branch,
    "upstream_remote": upstream_remote,
    "upstream_branch": upstream_branch,
    "head_after": head_after,
    "changed_files": changed_files,
    "merge_log": Path(merge_log).read_text(encoding="utf-8"),
}

output_path = Path(output_dir) / "git-summary.json"
output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
PY

if [[ "${ok}" != "true" ]]; then
  exit 1
fi
