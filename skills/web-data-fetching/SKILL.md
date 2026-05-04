---
name: web-data-fetching
description: >
  Frontend data-fetching patterns for fetch API, loading/error states, retries, cancellation, and API config.
  Trigger: Modifying frontend API calls or adding loading/error handling.
license: MIT
metadata:
  author: tickets-tool
  version: "1.0"
  scope: [root, frontend]
  auto_invoke:
    - "Modifying frontend API calls"
    - "Adding loading/error states for API requests"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Task
---

## Base Pattern

```typescript
const res = await fetch(url, options)
if (!res.ok) {
  const payload = await res.json().catch(() => ({}))
  throw new Error(payload.detail || `HTTP ${res.status}`)
}
const data = await res.json()
```

## Rules

- Always expose loading and error UI states.
- Keep base URL in `NEXT_PUBLIC_API_URL`.
- Use `AbortController` for cancellable requests when needed.
- Avoid duplicated fetch logic; extract helper when repeated.
