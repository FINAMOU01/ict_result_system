import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from academics.models import Semester

client = Client()

# Try to login first
from accounts.models import CustomUser
user = CustomUser.objects.filter(username='admin').first()
if user:
    logged_in = client.login(username='admin', password='admin')
    print(f"✅ Logged in as admin: {logged_in}")
else:
    print("❌ No admin user found")

# Get first semester
semester = Semester.objects.first()
if semester:
    print(f"Testing PDF for semester: {semester.id}")
    response = client.get(f'/registra/semesters/{semester.id}/report/pdf/')
    print(f"Response status: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type')}")
    print(f"Content-Disposition: {response.get('Content-Disposition')}")
    print(f"Content length: {len(response.content)}")
    
    if response.status_code == 200:
        print("✅ PDF response is successful")
        if response.get('Content-Type') == 'application/pdf':
            print("✅ Content-Type is correct")
        else:
            print(f"⚠️ Content-Type is wrong: {response.get('Content-Type')}")
    else:
        print(f"❌ Error response: {response.content[:500]}")
