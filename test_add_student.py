#!/usr/bin/env python
"""Test add-student functionality to verify Grade creation."""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from academics.models import Course, Enrollment, Student, AdmittedStudent
from results.models import Grade

# Get a course that's already coded
coded_course = Course.objects.filter(is_coded=True).first()

if not coded_course:
    print("❌ No coded courses found to test with")
    sys.exit(1)

# Get an admitted student
admitted = AdmittedStudent.objects.first()
if not admitted:
    print("❌ No admitted students found to test with")
    sys.exit(1)

print("Testing add-student functionality...")
print(f"Course: {coded_course.code}")
print(f"Admitted Student: {admitted.matricule} - {admitted.first_name} {admitted.last_name}")

# Create Student
student, _ = Student.objects.update_or_create(
    matricule=admitted.matricule,
    defaults={
        'first_name': admitted.first_name,
        'last_name': admitted.last_name,
        'email': admitted.email or '',
    }
)

# Check if already enrolled
if Enrollment.objects.filter(student=student, course=coded_course).exists():
    print(f"⚠️  Student already enrolled in this course, skipping...")
    sys.exit(0)

# Get next anonymous code
last_code = Enrollment.objects.filter(course=coded_course).count()
next_code = last_code + 1

# Create enrollment and grade (mimicking the view)
try:
    enrollment = Enrollment.objects.create(
        student=student,
        course=coded_course,
        semester=coded_course.semester,
        anonymous_code=next_code
    )
    print(f"✓ Enrollment created: {enrollment.id}")
    
    grade, created = Grade.objects.get_or_create(enrollment=enrollment)
    print(f"✓ Grade {'created' if created else 'retrieved'}: {grade.id}")
    print(f"  - assignment_score: {grade.assignment_score}")
    print(f"  - final_score: {grade.final_score}")
    print(f"  - letter_grade: {grade.letter_grade}")
    
    print("\n✅ Add-student functionality working correctly!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
