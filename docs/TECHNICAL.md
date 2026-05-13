# Technical Documentation - Gestion des Stages (Django)

## Architecture Overview

**Gestion des Stages** is a Django 6.0.5 web application for managing internship placements at EMSI Casablanca. It follows the **MVT (Model-View-Template)** pattern:

- **Models**: Django ORM definitions (User, Offer, Application, Defense, Document)
- **Views**: Request handlers and business logic (auth, offers, applications, defenses, documents)
- **Templates**: Django template engine with role-based rendering

## Functional Modules

- Email-based authentication with custom User model
- Role-based access control (RBAC)
- Stage offer management
- Student applications
- Document upload and review
- Role-aware dashboard
- Defense scheduling with conflict detection
- Password reset flow
- Email notifications for defenses

## Data Model

Main entities:

- `User`: Email-based custom user model with role support (admin, representant, encadrant, student)
- `Offer`: Stage offerings (title, description, company, status)
- `Application`: Student applications to offers
- `Document`: File uploads (reports, checklists, reviews)
- `Defense`: Scheduled defenses (date, time, room, jury)

Key relationships:

- A student can have multiple applications, documents, and defenses
- An application references an offer and a student
- A defense references a student and an encadrant
- A document can be linked to an application

## Security

- Email-based authentication via custom backend
- Passwords hashed with Django's password validators
- CSRF protection on all forms
- Role-based access control (decorators + queryset filtering)
- Secure password reset flow with time-limited tokens
- HTTPS redirect, HSTS, secure cookies (production)

## Configuration

### Key Environment Variables

- `DEBUG`: Enable development mode (True/False)
- `SECRET_KEY`: Django secret key (strong random value in production)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames
- `DATABASE_URL`: Database connection string (SQLite by default)
- `EMAIL_BACKEND`: Email transport (console for dev, SMTP for production)
- `SECURE_SSL_REDIRECT`: Force HTTPS (disabled in dev, enabled in production)
- `SESSION_COOKIE_SECURE`: Secure-only session cookies (production)
- `CSRF_COOKIE_SECURE`: Secure-only CSRF cookies (production)

### Useful Django Commands

```bash
python manage.py migrate                          # Apply database migrations
python manage.py makemigrations                   # Create new migrations
python manage.py createsuperuser                  # Create admin user
python manage.py send_defense_reminders           # Send reminder emails
python manage.py check                            # Verify configuration
python manage.py check --deploy                   # Check production readiness
python manage.py test stages.tests                # Run test suite
python manage.py runserver 127.0.0.1:8000         # Start dev server
```

## Configuration Files

- `gestion_stages/settings.py`: Django settings (env-driven security)
- `gestion_stages/urls.py`: URL routing
- `stages/models.py`: Data model definitions
- `stages/views.py`: Request handlers and business logic
- `stages/forms.py`: Django forms (with validation)
- `stages/admin.py`: Django admin customization
- `stages/decorators.py`: RBAC decorators
- `stages/backends.py`: Email authentication backend
- `requirements.txt`: Python dependencies
- `Dockerfile`: Container image definition
- `docker-compose.yml`: Multi-container orchestration

## Local Deployment

1. Create virtual environment:
   ```bash
   python -m venv .venv
   . .venv\Scripts\Activate.ps1  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create admin user:
   ```bash
   python manage.py createsuperuser
   ```

5. Load demo data (optional):
   ```bash
   python seed_data.py
   ```

6. Start development server:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

7. Access at `http://localhost:8000`

## Docker Deployment

1. Update `.env.docker` with production values
2. Build and start containers:
   ```bash
   docker compose up --build
   ```

## Important Notes

- Always run `python manage.py check --deploy` before production deployments
- Configure SMTP credentials for email delivery in production
- Use a persistent database (PostgreSQL/MySQL) in production
- Set up HTTPS/SSL with a reverse proxy (Nginx)
- Regularly backup database and uploaded files
- Monitor logs and set up alerting
