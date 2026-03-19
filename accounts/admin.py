from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ActivityLog


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('ICT Role', {'fields': ('role', 'phone', 'department')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('ICT Role', {'fields': ('role', 'phone', 'department')}),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'affected_entity', 'status', 'ip_address']
    list_filter = ['action', 'status', 'timestamp', 'user']
    search_fields = ['description', 'affected_entity', 'user__username', 'ip_address']
    readonly_fields = ['timestamp', 'user', 'action', 'description', 'affected_entity', 'ip_address', 'status']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        # Activity logs are auto-generated, don't allow manual creation
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion of audit logs
        return False

