from django.db import models
from accounts.models import CustomUser


class Semester(models.Model):
    name = models.CharField(max_length=50)  # e.g. "S1-2025"
    academic_year = models.CharField(max_length=20)  # e.g. "2024-2025"
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

    def save(self, *args, **kwargs):
        if self.is_active:
            Semester.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class Course(models.Model):
    LEVEL_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ]
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='bachelor')
    semester_code = models.CharField(max_length=10, blank=True, null=True)  # e.g., FA25, SP25
    level_code = models.CharField(max_length=10, blank=True, null=True)     # e.g., MSC, BSC, PHD
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='courses')
    professor = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_courses',
        limit_choices_to={'role': 'professor'}
    )
    is_coded = models.BooleanField(default=False)  # Whether anonymization has been done
    coding_done_at = models.DateTimeField(null=True, blank=True)
    grades_submitted = models.BooleanField(default=False)
    grades_submitted_at = models.DateTimeField(null=True, blank=True)
    is_decoded = models.BooleanField(default=False)  # Whether results have been decoded
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['code', 'semester']
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.semester})"

    def full_course_code(self):
        """Return the full course code like FA25-MSC-ICT7114 IT Strategic Planning and Management"""
        if self.semester_code and self.level_code:
            return f"{self.semester_code}-{self.level_code}-{self.code} {self.name}"
        return f"{self.code} {self.name}"

    def enrollment_count(self):
        return self.enrollments.count()


class Student(models.Model):
    LEVEL_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ]
    matricule = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='bachelor')
    email = models.EmailField(blank=True, default='')
    is_walkin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.matricule} - {self.last_name} {self.first_name}"

    def full_name(self):
        return f"{self.last_name} {self.first_name}"


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='enrollments')
    anonymous_code = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course', 'semester']
        ordering = ['anonymous_code', 'student__last_name']

    def __str__(self):
        return f"{self.student.matricule} → {self.course.code} (Code: {self.anonymous_code or 'N/A'})"


class ImportLog(models.Model):
    file_name = models.CharField(max_length=255)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    imported_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    students_created = models.IntegerField(default=0)
    courses_created = models.IntegerField(default=0)
    enrollments_created = models.IntegerField(default=0)
    errors = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Import {self.file_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class AdmittedStudent(models.Model):
    LEVEL_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ]
    ADMITTED_YEAR_CHOICES = [
        ('Fall 2020', 'Fall 2020'),
        ('Spring 2020', 'Spring 2020'),
        ('Summer 2020', 'Summer 2020'),
        ('Fall 2021', 'Fall 2021'),
        ('Spring 2021', 'Spring 2021'),
        ('Summer 2021', 'Summer 2021'),
        ('Fall 2022', 'Fall 2022'),
        ('Spring 2022', 'Spring 2022'),
        ('Summer 2022', 'Summer 2022'),
        ('Fall 2023', 'Fall 2023'),
        ('Spring 2023', 'Spring 2023'),
        ('Summer 2023', 'Summer 2023'),
        ('Fall 2024', 'Fall 2024'),
        ('Spring 2024', 'Spring 2024'),
        ('Summer 2024', 'Summer 2024'),
        ('Fall 2025', 'Fall 2025'),
        ('Spring 2025', 'Spring 2025'),
        ('Summer 2025', 'Summer 2025'),
        ('Fall 2026', 'Fall 2026'),
        ('Spring 2026', 'Spring 2026'),
        ('Summer 2026', 'Summer 2026'),
    ]
    
    matricule = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='bachelor')
    admitted_year = models.CharField(max_length=20, choices=ADMITTED_YEAR_CHOICES, default='Fall 2026')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-admitted_year', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['matricule']),
            models.Index(fields=['admitted_year']),
        ]

    def __str__(self):
        return f"{self.matricule} - {self.last_name} {self.first_name} ({self.admitted_year})"

    def full_name(self):
        return f"{self.last_name} {self.first_name}"
