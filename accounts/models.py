from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'System Admin'),
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

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
