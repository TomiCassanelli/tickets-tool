# Tickets Tool Frontend - AI Agent Ruleset

> **Skills Reference**: For detailed patterns, use these skills:
> - [`react-18`](../skills/react-18/SKILL.md) - React components and App Router patterns
> - [`typescript`](../skills/typescript/SKILL.md) - Const types and strict interfaces
> - [`web-data-fetching`](../skills/web-data-fetching/SKILL.md) - API calls, loading/error/retry/cancellation
> - [`tailwind-3`](../skills/tailwind-3/SKILL.md) - Tailwind CSS 3 conventions
> - [`tdd`](../skills/tdd/SKILL.md) - TDD workflow for features, fixes, and refactors

### Auto-invoke Skills

When performing these actions, ALWAYS invoke the corresponding skill FIRST:

| Action | Skill |
|--------|-------|
| Adding loading/error states for API requests | `web-data-fetching` |
| Fixing bug | `tdd` |
| Implementing feature | `tdd` |
| Modifying frontend API calls | `web-data-fetching` |
| Refactoring code | `tdd` |
| Working on task | `tdd` |
| Working with Tailwind classes | `tailwind-3` |
| Writing React components | `react-18` |
| Writing TypeScript types/interfaces | `typescript` |

---

## CRITICAL RULES - NON-NEGOTIABLE

### React

- ALWAYS: Use named imports (`import { useState, useEffect } from "react"`)
- NEVER: `import React` / `import * as React`
- ALWAYS: Use `"use client"` only when hooks, browser APIs, or event handlers are needed
- NEVER: Add premature memoization; use `useMemo`/`useCallback` only when profiling shows need

### Types

- ALWAYS: Prefer const-object type pattern for enum-like values
- NEVER: Introduce `any` in new code
- ALWAYS: Use explicit interfaces/types for props and API payloads

### Interfaces

- ALWAYS: Keep interfaces flat; extract nested shapes into dedicated interfaces
- ALWAYS: Reuse via `extends` or shared types
- NEVER: Leave inline nested object types when they are reused

### Data Fetching

- ALWAYS: Validate `response.ok` before reading data
- ALWAYS: Show loading and error states in UI
- ALWAYS: Keep backend URL in `NEXT_PUBLIC_API_URL`
- NEVER: Crash UI on failed requests

### Styling

- Static styles: `className="..."`
- Conditional styles: merged Tailwind classes
- Truly dynamic values: `style={{ ... }}`
- NEVER: Prefer raw hex/arbitrary color values when a Tailwind token exists

### Scope Rule

- Used in 2+ places -> extract to shared module (`components/`, `lib/`, `types/`, `hooks/`)
- Used in 1 place -> keep local to the route/feature file

---

## DECISION TREES

### Component Placement

```
Used in one route/page? -> Keep inside that route segment
Used by multiple pages?  -> Extract to shared component module
Needs local interactivity? -> Client component ("use client")
Static/SSR only?         -> Server component (no directive)
```

### Code Location

```
Shared API helpers (2+) -> src/lib/
Shared types (2+)       -> src/types/
Shared hooks (2+)       -> src/hooks/
Single-use helper       -> keep local in page/component file
```

### Data Fetching Strategy

```
Simple page request      -> fetch in page/component with state handling
Reused request logic     -> extract helper function in src/lib/
Needs cancellation       -> AbortController
```

---

## PATTERNS

### Server Component

```typescript
export default async function Page() {
  return <ClientComponent />;
}
```

### Client Component

```typescript
"use client";

import { useState } from "react";

export function InputBox() {
  const [value, setValue] = useState("");
  return <input value={value} onChange={(e) => setValue(e.target.value)} />;
}
```

### Safe Fetch Pattern

```typescript
const res = await fetch(`${API_BASE}/api/analyze-request`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});

const data = await res.json();
if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
```

---

## TECH STACK

Next.js 14 | React 18 | TypeScript | Tailwind CSS 3

---

## PROJECT STRUCTURE

```
frontend/
├── src/app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── tailwind.config.js
└── package.json
```

---

## COMMANDS

```bash
npm install
npm run dev
npm run build
```

---

## QA CHECKLIST BEFORE COMMIT

- [ ] `npm run build` passes
- [ ] Loading, error, and empty states are handled
- [ ] API errors are visible and sanitized for UI
- [ ] UI works on mobile and desktop breakpoints
- [ ] No secrets in frontend code (`.env*` only)

---

## NAMING CONVENTIONS

| Entity | Pattern | Example |
|--------|---------|---------|
| React component | `PascalCase` | `TicketDrawer` |
| Type/interface | `PascalCase` | `TicketMetadata` |
| Handler function | `handle<Intent>` | `handleSubmit` |
| Async action | `<verb><Domain>` | `analyzeRequest` |
