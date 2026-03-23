---
name: tailwind-3
description: >
  Tailwind CSS 3 patterns and best practices for consistent styling in the Next.js frontend.
  Trigger: Working with Tailwind classes in frontend components.
license: MIT
metadata:
  author: tickets-tool
  version: "1.0"
  scope: [root, frontend]
  auto_invoke: "Working with Tailwind classes"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Task
---

## Styling Decision Tree

```text
Static classes?         -> className="..."
Conditional classes?    -> merge utility or template conditions
Truly dynamic values?   -> style={{ ... }}
Reusable visual pattern?-> extract component class pattern
```

## Critical Rules

### Prefer Design Tokens Over Raw Values

```tsx
// Better
<div className="bg-gray-50 text-gray-900" />

// Avoid overusing arbitrary values
<div className="bg-[#fafafa] text-[#171717]" />
```

### Keep Class Lists Readable

```tsx
// Better
<button className="px-4 py-2 rounded-xl bg-blue-600 text-white disabled:opacity-50" />
```

## Common Patterns

```tsx
<div className="flex items-center gap-2" />
<div className="grid grid-cols-1 md:grid-cols-2 gap-4" />
<p className="text-sm text-gray-600" />
```
