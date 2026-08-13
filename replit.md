# Archive System

A Django 5.2 document/archive management web application with user accounts, a dashboard, document storage, and reports.

## Stack

- **Backend:** Python 3.11 + Django 5.2.15
- **Database:** SQLite (`db.sqlite3`)
- **Static files:** served via Django dev server
- **Media files:** uploaded files stored in `media/`

## Apps

- `accounts` — custom user model, login/logout, user management
- `core` — general settings and shared models
- `dashboard` — main dashboard views
- `documents` — document upload and management
- `reports` — reporting views

## How to run

The workflow `Start application` runs:
```
python3.11 manage.py runserver 0.0.0.0:5000
```

> **Important:** Use `python3.11` explicitly — the system `python3` is 3.12 but packages are installed under 3.11 (`.pythonlibs/lib/python3.11`).

## Environment variables

- `SECRET_KEY` — Django secret key (falls back to `SESSION_SECRET` if not set)

## First-time setup

If starting fresh, create an admin user:
```
python3.11 manage.py createsuperuser
```

## User preferences

(none yet)
