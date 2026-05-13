# Gestion des Stages - Django 6

Plateforme web de gestion des stages pour l'EMSI Casablanca, migrée vers Django.

## Prerequisites

- Python 3.14+
- `pip`
- SQLite for local development

## Quick Start

1. Create and activate a virtual environment.
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     . .venv\Scripts\Activate.ps1
     ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```powershell
   python manage.py migrate
   ```
4. Load demo data if needed:
   ```powershell
   python seed_data.py
   ```
5. Start the development server:
   ```powershell
   python manage.py runserver 127.0.0.1:8000
   ```

## Run with Docker

### Setup

1. **Update `.env.docker`** with production environment variables:

   ```bash
   # Example: .env.docker (IMPORTANT: Change SECRET_KEY, ALLOWED_HOSTS, and email settings in production)
   SECRET_KEY=xlS281FXikSG8e5lOzGeFAJZRg8GRsRD3iSBSfTOSo8kcI3LLAuZw4cByOawDwhgw786qsp_hkUv1swWxE-EEA
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   SECURE_SSL_REDIRECT=True
   SECURE_HSTS_SECONDS=31536000
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   DEFAULT_FROM_EMAIL=noreply@yourdomain.com
   ```

   **Security Notes:**
   - Generate a new `SECRET_KEY`:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(64))"
     ```
   - Set `ALLOWED_HOSTS` to your domain(s).
   - For email, configure SMTP settings via environment variables if using a custom backend.
   - HTTPS redirect and secure cookies are enabled by default in `.env.docker`.

### Build and Run

2. Build and start containers:

   ```bash
   docker compose up --build
   ```

   First run: migrations and static file collection run automatically.

3. Open the app:

   ```text
   http://127.0.0.1:8000
   ```

4. Seed demo data (optional):

   ```bash
   docker compose exec web python seed_data.py
   ```

5. Stop containers:
   ```bash
   docker compose down
   ```

### Production Notes

- The Dockerfile uses `python:3.14-slim` for a small image footprint.
- Gunicorn serves the app with 4 workers (adjust in `Dockerfile` for your load).
- Static and media files are mounted as volumes for persistence.
- For production, use a reverse proxy (Nginx) and a database (PostgreSQL/MySQL).
- Replace the console email backend with SMTP for real email delivery.

## Features

- Email-based authentication
- Role-based access control
- Stage offers management
- Student applications
- Document upload and review
- Defense scheduling with conflict checks
- Forgot-password flow with token-based reset
- Dashboard per role

## Test Accounts

If you run `seed_data.py`, these demo accounts are created:

- `admin@example.com` / `admin123`
- `representant@example.com` / `representant123`
- `encadrant@example.com` / `encadrant123`
- `student1@example.com` / `student123`
- `student2@example.com` / `student123`
- `student3@example.com` / `student123`

## Email in Development

Password-reset emails are sent through Django's console email backend in development. The reset link is printed in the terminal output.

## Project Structure

- [manage.py](manage.py) - Django entry point
- [gestion_stages/settings.py](gestion_stages/settings.py) - project settings
- [stages/](stages) - app models, views, forms, and URLs
- [templates/](templates) - shared and app templates
- [static/](static) - CSS and static assets
- [seed_data.py](seed_data.py) - demo data loader

## Notes

- The README and app are now Django-based; older Symfony instructions were removed.
- The password reset flow is available from the login page.
- If you load demo data, existing users and offers are cleared first.
