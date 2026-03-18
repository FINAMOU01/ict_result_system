from django.contrib import admin
from .models import Semester, Course, Student, Enrollment, ImportLog, AdmittedStudent

@admin.register(AdmittedStudent)
class AdmittedStudentAdmin(admin.ModelAdmin):
    list_display = ['matricule', 'last_name', 'first_name', 'email', 'level', 'admitted_year', 'created_at']
    list_filter = ['level', 'admitted_year']
    search_fields = ['matricule', 'last_name', 'first_name', 'email']
    readonly_fields = ['created_at']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_year', 'is_active', 'created_at']
    list_filter = ['is_active']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'level', 'semester', 'professor', 'is_coded', 'grades_submitted']
    list_filter = ['level', 'semester', 'is_coded', 'grades_submitted']
    search_fields = ['code', 'name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['matricule', 'last_name', 'first_name', 'level']
    search_fields = ['matricule', 'last_name', 'first_name']
    list_filter = ['level']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'semester', 'anonymous_code']
    list_filter = ['semester', 'course']
    search_fields = ['student__matricule', 'student__last_name']

@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'semester', 'imported_by', 'students_created', 'enrollments_created', 'created_at']
    readonly_fields = ['file_name', 'semester', 'imported_by', 'students_created', 'courses_created', 'enrollments_created', 'errors', 'created_at']
