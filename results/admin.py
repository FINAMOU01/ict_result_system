from django.contrib import admin
from .models import Grade

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'cc_score', 'sn_score', 'final_score', 'status']
    list_filter = ['status', 'enrollment__course__semester']
    search_fields = ['enrollment__student__matricule']
