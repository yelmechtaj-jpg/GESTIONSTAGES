#!/usr/bin/env python
"""Test authentication."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stages.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model

User = get_user_model()
u = User.objects.first()
print(f"First user: {u}")
print(f"Email: {u.email}")
print(f"Password check admin123: {u.check_password('admin123')}")

auth = authenticate(None, email="admin@example.com", password="admin123")
print(f"Authenticated user: {auth}")
