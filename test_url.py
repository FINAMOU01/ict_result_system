import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.template.loader import render_to_string
from django.urls import reverse
from academics.models import Semester

semester = Semester.objects.first()
if semester:
    print(f"Semester ID: {semester.id}")
    print(f"Semester Name: {semester.name}")
    
    url = reverse('export_report_pdf', args=[semester.id])
    print(f"Generated URL: {url}")
    
    # Check if URL is in urls.py
    from django.urls import get_resolver
    try:
        match = get_resolver().resolve(url)
        print(f"✅ URL resolves to: {match.func.__name__}")
    except Exception as e:
        print(f"❌ URL doesn't resolve: {e}")
