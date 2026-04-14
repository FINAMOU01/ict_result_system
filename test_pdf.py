import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from academics.models import Semester
from academics.utils import get_semester_statistics
from io import BytesIO

# Test with first semester
semester = Semester.objects.first()
if semester:
    try:
        stats = get_semester_statistics(semester)
        print(f"✅ Semester: {semester.name}")
        print(f"✅ Stats generated: {stats.get('total_courses')} courses")
        print(f"✅ Grade counts: {stats.get('grade_counts')}")
        
        # Test ReportLab import
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table
        print("✅ ReportLab imported successfully")
        
        # Try to generate a simple PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        data = [['Test', 'Data'], ['1', '2']]
        table = Table(data)
        doc.build([table])
        print(f"✅ PDF generated, size: {len(buffer.getvalue())} bytes")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("No semesters found")
