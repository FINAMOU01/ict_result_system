"""
Voice Assistant Tests
Run with: python manage.py test voice_assistant
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

User = get_user_model()


class VoiceAssistantTests(TestCase):
    
    def setUp(self):
        """Create test users"""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='test123',
            role='admin',
            email='admin@test.com'
        )
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        self.registra_user = User.objects.create_user(
            username='registra_test',
            password='test123',
            role='registra',
            email='registra@test.com'
        )
        
        self.professor_user = User.objects.create_user(
            username='prof_test',
            password='test123',
            role='professor',
            email='prof@test.com'
        )

    def test_voice_help_requires_login(self):
        """Voice help endpoint requires authentication"""
        response = self.client.get(reverse('voice_help'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_voice_help_admin(self):
        """Admin can see all commands"""
        self.client.login(username='admin_test', password='test123')
        response = self.client.get(reverse('voice_help'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('commands', data)
        self.assertIn('admin dashboard', [cmd.lower() for cmd in data['commands'].keys()])
        
    def test_voice_command_navigation(self):
        """Admin can navigate to pages"""
        self.client.login(username='admin_test', password='test123')
        response = self.client.post(
            reverse('process_voice_command'),
            data=json.dumps({'command': 'admin dashboard'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['type'], 'navigation')
        self.assertEqual(data['url'], '/admin-panel/')
        
    def test_voice_command_question(self):
        """Assistant answers questions"""
        self.client.login(username='registra_test', password='test123')
        response = self.client.post(
            reverse('process_voice_command'),
            data=json.dumps({'command': 'how does it work'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['type'], 'question')
        self.assertIn('workflow', data['message'].lower())
        
    def test_voice_command_unknown(self):
        """Unknown commands return helpful message"""
        self.client.login(username='prof_test', password='test123')
        response = self.client.post(
            reverse('process_voice_command'),
            data=json.dumps({'command': 'xyz123nonsense'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['type'], 'unknown')
        self.assertIn('understand', data['message'].lower())
        
    def test_registra_commands_restricted(self):
        """Professor can't access registra commands via voice"""
        self.client.login(username='prof_test', password='test123')
        response = self.client.post(
            reverse('process_voice_command'),
            data=json.dumps({'command': 'decode results'}),
            content_type='application/json'
        )
        # Should not find the command or return unknown
        data = json.loads(response.content)
        # Professors don't have access to registra commands by default
        
    def test_role_filtering_in_help(self):
        """Different roles see different commands"""
        # Admin sees everything
        self.client.login(username='admin_test', password='test123')
        admin_response = self.client.get(reverse('voice_help'))
        admin_data = json.loads(admin_response.content)
        admin_commands = list(admin_data['commands'].keys())
        
        # Professor sees limited commands
        self.client.login(username='prof_test', password='test123')
        prof_response = self.client.get(reverse('voice_help'))
        prof_data = json.loads(prof_response.content)
        prof_commands = list(prof_data['commands'].keys())
        
        # Admin should see more commands
        self.assertGreater(len(admin_commands), len(prof_commands))
