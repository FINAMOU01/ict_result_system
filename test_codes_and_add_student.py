#!/usr/bin/env python
"""Test add-student and anonymous code ordering."""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from academics.models import Course, Enrollment, Student, AdmittedStudent
from results.models import Grade
from django.db.models import Max

print("=" * 70)
print("TESTING ADD-STUDENT AND ANONYMOUS CODE ORDERING")
print("=" * 70)

# Get a coded course
coded_course = Course.objects.filter(is_coded=True).first()

if not coded_course:
    print("\n❌ No coded courses found")
    sys.exit(1)

print(f"\n📋 Testing with course: {coded_course.code}")

# Check current codes
enrollments = Enrollment.objects.filter(course=coded_course).order_by('anonymous_code')
print(f"\n✓ Current enrollments in this course:")
for e in enrollments[:5]:
    print(f"  - Code {e.anonymous_code}: {e.student.matricule}")
if enrollments.count() > 5:
    print(f"  ... and {enrollments.count() - 5} more")

# Get max code
max_code = Enrollment.objects.filter(
    course=coded_course
).aggregate(Max('anonymous_code'))['anonymous_code__max'] or 0
print(f"\n✓ Current max anonymous code: {max_code}")

# Get an admitted student not yet enrolled
admitted = AdmittedStudent.objects.exclude(
    matricule__in=Enrollment.objects.filter(
        course=coded_course
    ).values_list('student__matricule', flat=True)
).first()

if admitted:
    print(f"\n✓ Found admitted student: {admitted.matricule} - {admitted.first_name} {admitted.last_name}")
    
    # Simulate what add_student_to_coded_course does
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
        print(f"  ⚠️  Already enrolled, skipping test")
    else:
        # Get next code
        max_code_current = Enrollment.objects.filter(
            course=coded_course
        ).aggregate(Max('anonymous_code'))['anonymous_code__max'] or 0
        next_code = max_code_current + 1
        
        print(f"\n✓ Assigning next code: {next_code}")
        
        try:
            enrollment = Enrollment.objects.create(
                student=student,
                course=coded_course,
                semester=coded_course.semester,
                anonymous_code=next_code
            )
            print(f"  ✓ Enrollment created with code {enrollment.anonymous_code}")
            
            grade, created = Grade.objects.get_or_create(enrollment=enrollment)
            print(f"  ✓ Grade {'created' if created else 'found'}")
            
            # Verify the code sequence
            enrolled_codes = sorted(Enrollment.objects.filter(
                course=coded_course
            ).values_list('anonymous_code', flat=True))
            
            print(f"\n✓ All codes in course (first 10): {enrolled_codes[:10]}")
            
            # Check if codes are sequential from start
            expected_codes = list(range(1, len(enrolled_codes) + 1))
            if enrolled_codes == expected_codes:
                print(f"  ✅ Codes are properly sequential (1, 2, 3...)")
            else:
                print(f"  ⚠️  Codes not sequential. Expected: {expected_codes[:10]}, Got: {enrolled_codes[:10]}")
            
        except Exception as e:
            print(f"\n  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
else:
    print(f"❌ No unrolled admitted students found")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
