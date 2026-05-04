---
name: react-18
description: >
  React 18 patterns for Next.js 14 App Router.
  Trigger: Writing React components/hooks in .tsx files.
license: MIT
metadata:
  author: tickets-tool
  version: "1.0"
  scope: [root, frontend]
  auto_invoke: "Writing React components"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Task
---

## When to Apply

Use this skill when:
- Creating new React components
- Writing custom hooks
- Handling state or side effects
- Working with Next.js App Router

---

## Critical Rules

### 1. Imports (REQUIRED)

```typescript
// ✅ ALWAYS: Named imports
import { useState, useEffect, useRef } from "react";

// ❌ NEVER
import React from "react";
import * as React from "react";
```

### 2. Server vs Client Components

```typescript
// ✅ Server Component (default in App Router)
export default async function Page() {
  const data = await fetchData();
  return <ClientComponent data={data} />;
}

// ✅ Client Component - only when needed
"use client";
export function Interactive() {
  const [state, setState] = useState(false);
  return <button onClick={() => setState(!state)}>Toggle</button>;
}
```

### 3. When to use "use client"

- useState, useEffect, useRef, useContext
- Event handlers (onClick, onChange)
- Browser APIs (window, localStorage)

---

## Decision Tree

```text
Need interactivity (state/handlers)? -> "use client" directive
Fetching data in page?               -> Server Component, await directly
Need browser API?                    -> "use client"
Static UI only?                      -> Server Component (no directive)
```

---

## Common Hook Patterns

```typescript
// State with lazy initializer
const [state, setState] = useState(() => {
  return expensiveInitialValue();
});

// Ref for mutable values that don't trigger re-renders
const ref = useRef<HTMLInputElement>(null);

// Cleanup in useEffect
useEffect(() => {
  const subscription = subscribe(id);
  return () => subscription.unsubscribe();
}, [id]);
```

---

## Next.js App Router Patterns

```typescript
// Server Actions (Next.js 14+)
"use server";
async function submitForm(formData: FormData) {
  await saveToDatabase(formData);
  revalidatePath("/");
}

// Reading URL params (Server Component)
export default async function Page({ params }: { params: { id: string } }) {
  return <div>Ticket {params.id}</div>;
}

// Loading/Error states
export default function Page() {
  return (
    <Suspense fallback={<Skeleton />}>
      <TicketList />
    </Suspense>
  );
}
```

---

## Memoization (Use Sparingly)

```typescript
// Only use when profiling shows it's needed
const filtered = useMemo(() => items.filter(x => x.active), [items]);

// Stable callback references
const handleClick = useCallback((id: string) => {
  console.log(id);
}, []);
```

---

## Component Patterns

```typescript
// Props with explicit types
interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  variant?: "primary" | "secondary";
}

export function Button({ onClick, children, variant = "primary" }: ButtonProps) {
  return (
    <button 
      className={variant === "primary" ? "bg-blue-600" : "bg-gray-600"}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```
