from django.db import models
from academics.models import Enrollment, Course, Semester
from accounts.models import CustomUser


class Grade(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted to Registra'),
        ('decoded', 'Decoded & Finalized'),
    ]
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='grade')
    cc_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sn_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
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
        if self.cc_score is not None and self.sn_score is not None:
            self.final_score = round(self.cc_score + self.sn_score, 2)
        return self.final_score

    def __str__(self):
        return f"Grade for Code {self.enrollment.anonymous_code} in {self.enrollment.course.code}"
