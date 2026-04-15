from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'System Admin'),
        ('it_manager', 'IT Manager'),
        ('registra', 'Registra'),
        ('professor', 'Professor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='professor')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)

    def is_admin(self):
        return self.role == 'admin'

    def is_registra(self):
        return self.role == 'registra'

    def is_professor(self):
        return self.role == 'professor'

    def save(self, *args, **kwargs):
        # Automatically set role to 'admin' if user is superuser
        if self.is_superuser and self.role != 'admin':
            self.role = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


class ActivityLog(models.Model):
    """
    Comprehensive audit log for all system actions.
    Tracks user actions for admin review and system auditing.
    """
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('user_create', 'User Created'),
        ('user_update', 'User Updated'),
        ('user_deactivate', 'User Deactivated'),
        ('user_activate', 'User Activated'),
        ('semester_create', 'Semester Created'),
        ('semester_update', 'Semester Updated'),
        ('semester_delete', 'Semester Deleted'),
        ('course_create', 'Course Created'),
        ('course_update', 'Course Updated'),
        ('course_delete', 'Course Deleted'),
        ('enrollment_create', 'Enrollment Created'),
        ('enrollment_delete', 'Enrollment Deleted'),
        ('import_start', 'CSV Import Started'),
        ('import_success', 'CSV Import Completed'),
        ('import_error', 'CSV Import Failed'),
        ('grade_submit', 'Grade Submitted'),
        ('grade_update', 'Grade Updated'),
        ('result_decode', 'Result Decoded'),
        ('result_encode', 'Result Encoded'),
        ('permission_denied', 'Permission Denied'),
        ('profile_update', 'Profile Updated'),
        ('other', 'Other Action'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    description = models.TextField(help_text="Detailed description of the action")
    affected_entity = models.CharField(max_length=100, blank=True, help_text="What was affected (e.g., 'Student ABC123')")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('success', 'Success'), ('failed', 'Failed'), ('warning', 'Warning')],
        default='success'
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"

