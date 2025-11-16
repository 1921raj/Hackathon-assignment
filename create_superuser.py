#!/usr/bin/env python
"""Script to create or upgrade a user to superuser"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'competitor_monitor.settings')
django.setup()

from django.contrib.auth.models import User

def create_or_upgrade_superuser():
    username = input("Enter username (or press Enter to use 'admin'): ").strip() or 'admin'
    
    # Check if user exists
    try:
        user = User.objects.get(username=username)
        print(f"User '{username}' already exists. Upgrading to superuser...")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✓ User '{username}' is now a superuser!")
        print(f"  You can now login with username: {username}")
        print(f"  Use your existing password to login.")
    except User.DoesNotExist:
        # Create new superuser
        print(f"Creating new superuser '{username}'...")
        password = input("Enter password: ").strip()
        if not password:
            print("Password cannot be empty!")
            return
        
        email = input("Enter email (optional): ").strip() or ''
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        print(f"✓ Superuser '{username}' created successfully!")
        print(f"  Username: {username}")
        print(f"  Password: {password}")

if __name__ == '__main__':
    create_or_upgrade_superuser()

