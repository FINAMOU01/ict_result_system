#!/usr/bin/env python
"""Recalculate final scores and letter grades for all grades."""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from results.models import Grade

# Recalculate final scores and grades for all existing grades
updated = 0
fixed = 0

for grade in Grade.objects.all():
    if grade.cc_score is not None and grade.sn_score is not None:
        old_final = grade.final_score
        grade.calculate_final()
        grade.save()
        updated += 1
        
        if old_final is None or old_final != grade.final_score:
            fixed += 1
            print(f"✓ {grade.enrollment.student.matricule} | Final: {old_final} → {grade.final_score} | Grade: {grade.letter_grade}")

print(f"\n✅ Processed: {updated} grades")
print(f"✅ Fixed: {fixed} grades with missing/incorrect finals")
