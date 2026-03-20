from django.contrib import admin
from .models import VoiceCommandLog


@admin.register(VoiceCommandLog)
class VoiceCommandLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'command', 'action_type', 'timestamp')
    list_filter = ('action_type', 'timestamp', 'user')
    search_fields = ('command', 'user__username')
    readonly_fields = ('timestamp',)
    ordering = ['-timestamp']
