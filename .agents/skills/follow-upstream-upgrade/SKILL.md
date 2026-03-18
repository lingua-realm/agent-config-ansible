---
name: follow-upstream-upgrade
description: Use when working in this repository and the user asks to sync upstream changes into private-config, follow upstream updates, assess upgrade impact across inventory profiles, or run a local upgrade rehearsal.
---

# Follow Upstream Upgrade

## Overview

This is a repository-specific upgrade skill for safely rehearsing upstream updates onto `private-config`.

## When to Use

- Sync `upstream/main` into `private-config`
- Follow upstream updates in this repository
- Assess upgrade impact across multiple `inventory/<profile>/`
- Run a local upgrade rehearsal before wider rollout

## When Not to Use

- Routine single-tool configuration edits
- Plain playbook execution without upstream merge work
- Repositories other than this one

## Hard Boundaries

- Never auto-commit.
- Never auto-push.
- Never modify `inventory/<profile>/` or assets directly.
- Never run `target_hosts=all`.
- Stop immediately on dirty working tree, merge conflicts, verification failures, blocking migrations, or local apply failures.

## Default Assumptions

- `upstream` is the upstream remote.
- `main` is the upstream branch.
- `private-config` is the target branch.
- `inventory/default/` is a template, not a managed user profile.

## Execution Flow

1. Inspect repository state.
2. Discover profiles.
3. Fetch and merge upstream into an upgrade branch.
4. Detect impacted tools.
5. Run repository-level verification.
6. Generate profile patch drafts.
7. Stop on blocking migrations.
8. Rehearse local profile applies for impacted tools only.

## Communication Contract

- Report the current stage briefly.
- Surface blockers immediately.
- Keep large diffs and logs in generated artifacts, not chat output.

## Outputs

- Upgrade report
- Impact summary
- Profile patch drafts
- Local apply results

## Failure Handling

- Preserve the upgrade branch and generated artifacts on failure.
- Always write a report before exiting.

## Escalation to Human

- Merge conflicts
- Blocking profile migrations
- Repository verification failures
- Local apply failures
