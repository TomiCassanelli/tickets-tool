---
name: skill-creator
description: >
  Creates new AI agent skills following this repository's skill format and conventions.
  Trigger: When the user asks to create a new skill, add agent instructions, or document repeatable patterns for AI.
license: MIT
metadata:
  author: tickets-tool
  version: "1.0"
  scope: [root]
  auto_invoke: "Creating new skills"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Task
---

## When to Create a Skill

Create a skill when:
- A pattern is repeated and the agent needs explicit guidance
- Project conventions differ from generic best practices
- A workflow needs decision trees and clear step-by-step rules
- Reusable templates/examples will speed up future tasks

Do not create a skill when:
- Existing project docs already cover it clearly
- The pattern is one-off or trivial
- The guidance would duplicate another existing skill

---

## Skill Structure

```text
skills/{skill-name}/
|- SKILL.md
|- assets/        (optional)
|  |- template files
|- references/    (optional)
|  |- local docs links or copied snippets
```

---

## SKILL.md Template

Use `assets/skill-template.md` as the canonical template.

---

## Naming Conventions

| Type | Pattern | Examples |
|------|---------|----------|
| Generic skill | `{technology}` | `pytest`, `tailwind-3`, `tdd` |
| Project-specific | `{project}-{topic}` | `tickets-prompting`, `tickets-api` |
| Workflow skill | `{action}-{target}` | `skill-creator`, `release-helper` |

---

## Decision: assets/ vs references/

```text
Need templates/snippets?        -> assets/
Need sample schemas/configs?    -> assets/
Need links to local project docs? -> references/
Need curated external context?  -> references/ with local summary file
```

---

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, lowercase kebab-case |
| `description` | Yes | What it does + explicit trigger |
| `license` | Yes | Project default license for skills |
| `metadata.author` | Yes | Owner or project name |
| `metadata.version` | Yes | Semantic version string |

Optional but recommended:
- `metadata.scope`
- `metadata.auto_invoke`
- `allowed-tools`

---

## Content Guidelines

Do:
- Put critical rules first
- Use short decision trees and focused examples
- Keep commands copy-paste ready
- Keep skill practical, not theoretical

Don't:
- Repeat long generic documentation
- Mix unrelated domains in one skill
- Leave ambiguous triggers

---

## Registering the Skill

After creating a skill:
1. Add it to the "Available Skills" table in `AGENTS.md`
2. If it should auto-load, add a row in "Auto-invoke Skills"
3. Validate links to `skills/{skill-name}/SKILL.md`

---

## Checklist Before Finishing

- [ ] No duplicate skill exists in `skills/`
- [ ] Name follows kebab-case conventions
- [ ] Frontmatter includes trigger in description
- [ ] Critical patterns are concrete and testable
- [ ] Commands section exists (if applicable)
- [ ] Skill is listed in `AGENTS.md`

## Resources

- **Template**: See [assets/skill-template.md](assets/skill-template.md)
