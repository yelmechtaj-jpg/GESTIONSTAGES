#!/usr/bin/env python
"""Seed database with test data."""
import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stages.settings')
django.setup()

from django.contrib.auth import get_user_model
from stages.models import StageOffer, Application, Defense

User = get_user_model()

# Clear existing data
User.objects.all().delete()
StageOffer.objects.all().delete()

print("Creating users...")
admin_user = User.objects.create_superuser(
    email='admin@example.com',
    password='admin123',
    full_name='Admin User',
    role='admin'
)

representant_user = User.objects.create_user(
    email='representant@example.com',
    password='representant123',
    full_name='Representant User',
    role='representant'
)

encadrant_user = User.objects.create_user(
    email='encadrant@example.com',
    password='encadrant123',
    full_name='Encadrant User',
    role='encadrant'
)

student1 = User.objects.create_user(
    email='student1@example.com',
    password='student123',
    full_name='Student One',
    role='etudiant'
)

student2 = User.objects.create_user(
    email='student2@example.com',
    password='student123',
    full_name='Student Two',
    role='etudiant'
)

student3 = User.objects.create_user(
    email='student3@example.com',
    password='student123',
    full_name='Student Three',
    role='etudiant'
)

print("Creating offers...")
offer1 = StageOffer.objects.create(
    title='Web Development Internship',
    description='Build web applications with Django and React',
    status='published'
)

offer2 = StageOffer.objects.create(
    title='Data Science Internship',
    description='Work with data analysis and machine learning',
    status='published'
)

offer3 = StageOffer.objects.create(
    title='Mobile Development Internship',
    description='Develop mobile applications (iOS/Android)',
    status='draft'
)

print("Creating applications...")
app1 = Application.objects.create(
    student=student1,
    offer=offer1,
    status='pending'
)

app2 = Application.objects.create(
    student=student2,
    offer=offer1,
    status='accepted'
)

app3 = Application.objects.create(
    student=student3,
    offer=offer2,
    status='rejected'
)

print("Creating defenses...")
tomorrow = timezone.now() + timedelta(days=1)
next_week = timezone.now() + timedelta(days=7)

defense1 = Defense.objects.create(
    application=app2,
    student=student2,
    encadrant=encadrant_user,
    scheduled_at=tomorrow.replace(hour=10, minute=0),
    room='Room A',
    status='planned'
)

defense2 = Defense.objects.create(
    application=app1,
    student=student1,
    encadrant=encadrant_user,
    scheduled_at=next_week.replace(hour=14, minute=0),
    room='Room B',
    status='confirmed'
)

print("\n✓ Superuser created: admin@example.com / admin123")
print("✓ 6 users created (1 admin, 1 representant, 1 encadrant, 3 students)")
print("✓ 3 offers created (2 published, 1 draft)")
print("✓ 3 applications created (mixed statuses)")
print("✓ 2 defenses created (scheduled)\n")
