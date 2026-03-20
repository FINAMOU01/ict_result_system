from django.db import models

# Voice Assistant models can be added here if you need to store voice command history
# For now, it's a simple stateless system

class VoiceCommandLog(models.Model):
    """Optional: Log all voice commands for analytics"""
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    command = models.CharField(max_length=255)
    action_type = models.CharField(max_length=20, choices=[
        ('navigation', 'Navigation'),
        ('question', 'Question'),
        ('unknown', 'Unknown'),
    ])
    response_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Voice Command Logs'

    def __str__(self):
        return f"{self.user.username} - {self.command} ({self.timestamp})"
