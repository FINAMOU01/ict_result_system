from django.urls import path
from . import views

urlpatterns = [
    path('process/', views.process_voice_command, name='process_voice_command'),
    path('help/', views.get_help, name='voice_help'),
    path('report/', views.get_system_report, name='system_report'),
]
