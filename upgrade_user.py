#!/usr/bin/env python
"""Script to upgrade existing user to superuser"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'competitor_monitor.settings')
django.setup()

from django.contrib.auth.models import User

# Upgrade the existing user to superuser
username = 'superbadshah1999'

try:
    user = User.objects.get(username=username)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"SUCCESS! User '{username}' is now a superuser!")
    print(f"\nYou can now login to admin panel with:")
    print(f"  Username: {username}")
    print(f"  Password: (your existing password)")
    print(f"\nAccess admin at: http://127.0.0.1:8000/admin/")
except User.DoesNotExist:
    print(f"User '{username}' not found. Creating new superuser...")
    # Create a default superuser
    user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123',
        is_staff=True,
        is_superuser=True
    )
    print(f"SUCCESS! Created new superuser!")
    print(f"\nLogin credentials:")
    print(f"  Username: admin")
    print(f"  Password: admin123")
    print(f"\nWARNING: Please change the password after first login!")

