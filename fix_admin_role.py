#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import CustomUser

# Find the superuser and set their role to admin
superusers = CustomUser.objects.filter(is_superuser=True)
for user in superusers:
    user.role = 'admin'
    user.save()
    print(f"✅ Updated {user.username} to admin role")

if not superusers.exists():
    print("❌ No superusers found")
