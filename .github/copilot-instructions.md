# Gestion des Stages - Copilot Instructions

## Project Stack
- Python 3.14+
- Django 6.0.5
- SQLite for local development
- Docker + Gunicorn for deployment

## Local Development
1. Create venv and activate.
2. Install dependencies from requirements.txt.
3. Run migrations.
4. Optionally load demo data with seed_data.py.
5. Start server on 127.0.0.1:8000.

## Testing
- Run: python manage.py test stages.tests
- Expected result: all tests pass.

## Security & Environment
- Keep secrets in environment variables.
- Development should use DEBUG=True.
- Docker/production should use DEBUG=False.
- Production settings are env-driven for:
  - SECRET_KEY
  - ALLOWED_HOSTS
  - SECURE_SSL_REDIRECT
  - SECURE_HSTS_SECONDS
  - SECURE_HSTS_INCLUDE_SUBDOMAINS
  - SECURE_HSTS_PRELOAD
  - SESSION_COOKIE_SECURE
  - CSRF_COOKIE_SECURE

## Docker
- Configure .env.docker before deployment.
- Build and run with docker compose up --build.
- App entrypoint runs migrations and collectstatic.

## Functional Scope
- Email-based authentication
- Role-based access control (admin, representant, encadrant, student)
- Offers, applications, documents, defense scheduling
- Password reset flow
- Defense reminder command

## Current Quality Gate
- Django deploy checks should pass: python manage.py check --deploy
- Test suite should pass before merge/deploy.
