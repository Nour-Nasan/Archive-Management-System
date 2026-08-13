---
name: Django Archive System Setup
description: Key decisions and quirks for the Django archive management project
---

# Django Archive System — Key Decisions

## Python version
- System `python3` = 3.12 but packages installed under 3.11 (`.pythonlibs/lib/python3.11`)
- **Always use `python3.11`** for manage.py commands and the workflow command
- Workflow: `python3.11 manage.py runserver 0.0.0.0:5000`

## Existing files have CRLF line endings (Windows)
- `archive_project/settings.py`, `archive_project/urls.py`, etc. have `\r\n` endings
- `Edit` tool fails on these — use `ShellExec` with a Python script to read-decode-rewrite

## LOGIN_URL
- Set to `"/login/"` in settings.py (Django default is `/accounts/login/`)

## Approval workflow
- `User.approval_status` field: pending / approved / rejected, default='approved'
- Superusers bypass approval check entirely (checked in `login_view` and `is_approved()`)
- `is_manager()` already returns True for superusers — no changes needed to manager_required
- `superuser_required` decorator added for user management pages

## Roles
- Manager (id=1), Employee (id=2) in DB
- `is_manager()` = `is_superuser OR role.name.lower() == 'manager'`

## adminNour account
- id=1, superuser=True, staff=True, role=Manager
- Password was reset to `TestAdmin123!` during automated testing — user must reset it

## Key URLs
- `/login/` — public login + Create Account link
- `/register/` — public registration (creates pending account)
- `/users/` — superuser-only user management (approve/reject/toggle/set-role)
- `/documents/` — requires login
- `/dashboard/manager/` — requires is_manager()
- `/dashboard/employee/` — requires login

## requirements.txt encoding
- Original zip had UTF-16-LE encoded requirements.txt — was rewritten as UTF-8
- mysqlclient was dropped (settings use SQLite)
