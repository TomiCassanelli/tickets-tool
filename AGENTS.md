# Repository Guidelines

## How to Use This Guide

- Start here for repository-wide conventions.
- Component guides override this file when guidance conflicts:
  - `backend/AGENTS.md`
  - `frontend/AGENTS.md`

## Available Skills

Use these skills for implementation patterns and consistent AI-assisted workflows.

| Skill | Description | URL |
|-------|-------------|-----|
| `tdd` | Test-Driven Development workflow | [SKILL.md](skills/tdd/SKILL.md) |
| `fastapi-backend` | FastAPI routes, models, services, and backend patterns | [SKILL.md](skills/fastapi-backend/SKILL.md) |
| `web-data-fetching` | Frontend fetch patterns, error handling, retry, cancellation | [SKILL.md](skills/web-data-fetching/SKILL.md) |
| `tailwind-3` | Tailwind CSS 3 conventions for this repository | [SKILL.md](skills/tailwind-3/SKILL.md) |
| `skill-creator` | Creates new AI skills with standard structure and registration | [SKILL.md](skills/skill-creator/SKILL.md) |
| `skill-sync` | Syncs skill metadata into AGENTS auto-invoke tables | [SKILL.md](skills/skill-sync/SKILL.md) |
| `typescript` | TypeScript strict typing patterns and conventions | [SKILL.md](skills/typescript/SKILL.md) |
| `react-18` | React 18 patterns for Next.js 14 App Router | [SKILL.md](skills/react-18/SKILL.md) |
| `backend-qa` | QA, lint, type checks, and test validation for backend | [SKILL.md](skills/backend-qa/SKILL.md) |

### Auto-invoke Skills

When performing these actions, ALWAYS invoke the corresponding skill FIRST:

| Action | Skill |
|--------|-------|
| Adding loading/error states for API requests | `web-data-fetching` |
| After creating/modifying a skill | `skill-sync` |
| Creating Pydantic request/response models | `fastapi-backend` |
| Creating new skills | `skill-creator` |
| Creating or modifying FastAPI routes | `fastapi-backend` |
| Fixing bug | `tdd` |
| Implementing feature | `tdd` |
| Modifying frontend API calls | `web-data-fetching` |
| Refactoring code | `tdd` |
| Regenerate AGENTS.md Auto-invoke tables (sync.sh) | `skill-sync` |
| Running backend tests | `backend-qa` |
| Running lint/type checks on backend | `backend-qa` |
| Troubleshooting backend errors | `backend-qa` |
| Troubleshoot why a skill is missing from AGENTS.md auto-invoke | `skill-sync` |
| Working on task | `tdd` |
| Working with Tailwind classes | `tailwind-3` |
| Writing React components | `react-18` |
| Writing TypeScript types/interfaces | `typescript` |

## Project Overview

Tickets Tool is a two-part application:

| Component | Location | Tech Stack |
|-----------|----------|------------|
| Backend API | `backend/` | FastAPI, Pydantic, Groq client |
| Frontend UI | `frontend/` | Next.js 14, React 18, Tailwind CSS 3 |

---

## Development Commands

```bash
# Backend
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
uvicorn main:app --reload --app-dir backend

# Frontend
cd frontend
npm install
npm run dev
```

---

## Commit Guidelines

Follow conventional commits:

`<type>(<scope>): <description>`

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `style`
