---
name: tdd
description: >
  Test-Driven Development workflow for implementing features, fixing bugs, and refactoring safely.
  Trigger: Working on task, implementing feature, fixing bug, or refactoring code.
license: MIT
metadata:
  author: tickets-tool
  version: "1.0"
  scope: [root, backend, frontend]
  auto_invoke:
    - "Working on task"
    - "Implementing feature"
    - "Fixing bug"
    - "Refactoring code"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Task
---

## Workflow

```text
1) Write a failing test for desired behavior
2) Implement the minimum change to pass
3) Refactor while keeping tests green
```

## Rules

- Start with behavior, not implementation details.
- Keep tests small, deterministic, and easy to read.
- Add regression tests for every bug fix.
- Avoid broad refactors without coverage.
