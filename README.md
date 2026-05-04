# Feedback Management System

A Django-based feedback workflow platform for organizations that need role-based access control, department routing, responder assignment, notifications, and tracked responses.

## Overview

This project provides a web-based feedback portal with a custom email-based user model, permission-driven workflow routing, and real-time notification support. It is built with Django templates and Channels, and it uses django-guardian for object-level permissions.

## Key Features

- Custom authentication with email as the login identity
- Role setup for Employee, Responder, Department Manager, Feedback Admin, and Auditor
- Object-level permissions backed by django-guardian
- Feedback creation, detail, delete, assignment, and response workflows
- Department and category management
- Notifications list, read-state updates, and SSE-based live updates
- Django admin support for managing core records

## Tech Stack

- Python 3
- Django 6.0.3
- Channels 4
- Daphne 4
- django-guardian 3
- python-decouple
- WhiteNoise
- SQLite for local development

## Project Structure

- `account/` - custom user model, authentication views/forms, role seeding command
- `feedback/` - feedback domain models, views, permissions, notifications, and management commands
- `config/` - project settings, ASGI/WSGI entry points, and URL routing
- `templates/` - shared and app templates
- `static/` - source styles and assets

## Getting Started

### 1) Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a `.env` file in the project root if you want to override the defaults:

```env
SECRET_KEY=replace-with-a-secure-key
DEBUG=True
```

### 4) Apply database migrations

```powershell
python manage.py migrate
```

### 5) Create an admin account

```powershell
python manage.py createsuperuser
```

### 6) Seed roles and permissions

```powershell
python manage.py seed_roles_permissions
```

### 7) Add departments as needed

```powershell
python manage.py adddepartment "HR" --description "Human Resources"
python manage.py adddepartment "IT" --description "Technology and Systems"
```

### 8) Start the development server

```powershell
python manage.py runserver
```

Open the application in your browser:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/account/login/
- http://127.0.0.1:8000/feedback/
- http://127.0.0.1:8000/admin/

## Main Routes

### Account

- `/account/register/`
- `/account/login/`
- `/account/logout/`

### Feedback

- `/feedback/`
- `/feedback/analytics/`
- `/feedback/create/`
- `/feedback/<uuid>/`
- `/feedback/<uuid>/delete/`
- `/feedback/<uuid>/response/create/`
- `/feedback/<uuid>/responses/`
- `/feedback/response/<uuid>/edit/`
- `/feedback/response/<uuid>/delete/`
- `/feedback/<uuid>/assign/`
- `/feedback/department/create/`
- `/feedback/category/create/`
- `/feedback/notifications/`
- `/feedback/notifications/mark/<int:pk>/`
- `/feedback/notifications/sse/`

## Management Commands

- `python manage.py seed_roles_permissions` - creates or updates role groups and permission mappings
- `python manage.py adddepartment <name> --description <text>` - creates a new department

## Configuration Notes

- The default database is SQLite at `db.sqlite3`
- The default email backend writes messages to the console
- Channels uses the in-memory channel layer for local development

