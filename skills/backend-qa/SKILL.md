---
name: backend-qa
description: >
  QA checks focused on code errors (import errors, syntax errors, unresolved references).
  Trigger: When debugging backend errors or validating backend code quality.
license: MIT
metadata:
  author: tickets-tool
  version: "2.0"
  scope: [backend]
  auto_invoke:
    - "Check code quality"
    - "Validate backend"
    - "Fix backend errors"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

## When to Apply

Use this skill when:
- Debugging backend errors
- Validating backend code quality
- Fixing import errors, syntax errors, or code issues

---

## QA Commands

### 1. Check for Python Syntax Errors

```bash
cd backend && source venv/bin/activate && python -m py_compile app/**/*.py
```

### 2. Check for Import Errors

```bash
cd backend && source venv/bin/activate && python -c "import app"
```

### 3. Check Specific File for Errors

```bash
cd backend && source venv/bin/activate && python -m py_compile app/path/to/file.py
```

### 4. Full Error Check Pipeline

```bash
cd backend && source venv/bin/activate && \
  python -m py_compile app/*.py app/**/*.py
```

### 5. Run Backend Server (to verify runtime)

```bash
cd backend && source venv/bin/activate && uvicorn main:app --reload --app-dir backend
```

---

## Error Resolution Guide

### ImportError / ModuleNotFoundError
- Check `venv` is activated
- Verify package is in `requirements.txt`
- Run `pip install -r requirements.txt`

### 500 Internal Server Error
- Check logs in terminal
- Verify `.env` has `GROQ_API_KEY`
- Test with mock AI responses first

### Pydantic Validation Error
- Check `Field(...)` definitions in models.py
- Ensure `model_config = ConfigDict(extra="ignore")` is set if receiving extra fields
- Verify types match expected values

### SyntaxError
- Check for missing colons, parentheses, or brackets
- Verify indentation is correct
- Look for unclosed strings or comments

---

## Success Criteria

Before considering QA complete:

- [ ] `python -m py_compile` passes on all files
- [ ] `import app` succeeds without ImportError
- [ ] Backend starts without errors
- [ ] API endpoints return expected status codes
