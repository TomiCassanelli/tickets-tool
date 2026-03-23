---
name: skill-sync
description: >
  Syncs skill metadata to AGENTS.md Auto-invoke sections.
  Trigger: When updating skill metadata (metadata.scope/metadata.auto_invoke), regenerating Auto-invoke tables, or running ./skills/skill-sync/assets/sync.sh.
license: MIT
metadata:
  author: tickets-tool
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "After creating/modifying a skill"
    - "Regenerate AGENTS.md Auto-invoke tables (sync.sh)"
    - "Troubleshoot why a skill is missing from AGENTS.md auto-invoke"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

## Purpose

Keeps AGENTS.md Auto-invoke sections in sync with skill metadata.
When creating or modifying a skill, run the sync script to regenerate tables.

## Required Skill Metadata

Each skill that should appear in Auto-invoke sections needs these fields inside `metadata`:

```yaml
metadata:
  author: tickets-tool
  version: "1.0"
  scope: [root]                      # root, backend, frontend
  auto_invoke: "Working on task"    # string or list of strings
```

`auto_invoke` can be a single string or a list.

## Scope Values

| Scope | Updates |
|-------|---------|
| `root` | `AGENTS.md` |
| `backend` | `backend/AGENTS.md` |
| `frontend` | `frontend/AGENTS.md` |

Skills can have multiple scopes, for example `scope: [frontend, root]`.

## Usage

```bash
# Sync all AGENTS.md files
./skills/skill-sync/assets/sync.sh

# Dry run (show generated tables only)
./skills/skill-sync/assets/sync.sh --dry-run

# Sync one scope only
./skills/skill-sync/assets/sync.sh --scope frontend
```

## What It Does

1. Reads all `skills/*/SKILL.md` files
2. Extracts `metadata.scope` and `metadata.auto_invoke`
3. Builds sorted Auto-invoke tables by scope
4. Replaces the `### Auto-invoke Skills` section in each AGENTS.md

## Checklist

- [ ] Skill includes `metadata.scope`
- [ ] Skill includes `metadata.auto_invoke`
- [ ] Ran `./skills/skill-sync/assets/sync.sh`
- [ ] Verified AGENTS.md tables updated as expected

## Resources

- **Script**: See [assets/sync.sh](assets/sync.sh)
