from django.db import models
from academics.models import Enrollment, Course, Semester
from accounts.models import CustomUser


class Grade(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted to Registra'),
        ('decoded', 'Decoded & Finalized'),
    ]
    
    GRADE_CHOICES = [
        ('A', 'A (4.0)'),
        ('B+', 'B+ (3.5)'),
        ('B', 'B (3.0)'),
        ('C+', 'C+ (2.5)'),
        ('C', 'C (2.0)'),
        ('D+', 'D+ (1.5)'),
        ('D', 'D (1.0)'),
        ('F', 'F (0.0)'),
    ]
    
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='grade')
    cc_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, 
                                   help_text="CA Score (0-30)")
    sn_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                   help_text="Final Score (0-70)")
    attendance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                          default=0, help_text="Attendance (0-10)")
    assignment_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                           default=0, help_text="Assignment (0-20)")
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    letter_grade = models.CharField(max_length=2, choices=GRADE_CHOICES, null=True, blank=True)
    cc_submitted = models.BooleanField(default=False)
    sn_submitted = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='submitted_grades'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['enrollment__anonymous_code']

    def calculate_final(self):
        """
        Calculate final score and letter grade.
        Final Score = CA (0-30) + Attendance (0-10) + Final (0-70) = 110 total, capped at 100
        """
        if self.cc_score is not None and self.sn_score is not None:
            attendance = self.attendance_score if self.attendance_score is not None else 0
            self.final_score = round(float(self.cc_score) + float(attendance) + float(self.sn_score), 2)
            self.letter_grade = self.get_letter_grade(self.final_score)
        return self.final_score

    def get_letter_grade(self, score):
        """Convert numerical score to letter grade"""
        if score is None:
            return None
        score = float(score)
        if 80 <= score <= 100:
            return 'A'
        elif 70 <= score < 80:
            return 'B+'
        elif 60 <= score < 70:
            return 'B'
        elif 55 <= score < 60:
            return 'C+'
        elif 50 <= score < 55:
            return 'C'
        elif 45 <= score < 50:
            return 'D+'
        elif 40 <= score < 45:
            return 'D'
        else:
            return 'F'

    def compute_final(self):
        """Compute final score from CA and Final scores, and assign letter grade."""
        if self.cc_score is not None and self.sn_score is not None:
            self.final_score = self.cc_score + self.sn_score
            self.letter_grade = self.get_letter_grade(self.final_score)
            self.save()

    def __str__(self):
        return f"Grade for Code {self.enrollment.anonymous_code} in {self.enrollment.course.code}"
