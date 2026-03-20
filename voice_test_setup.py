"""
Voice Assistant Integration Demo
This file shows how to test the voice assistant locally
"""

# Quick test script - run with: python manage.py shell < voice_test.py

# Example 1: Set up test users for voice assistant
from accounts.models import CustomUser

# Create test users if they don't exist
if not CustomUser.objects.filter(username='voice_admin').exists():
    admin = CustomUser.objects.create_superuser(
        username='voice_admin',
        email='admin@voice.test',
        password='voice123',
        first_name='Voice',
        last_name='Admin',
        role='admin'
    )
    print(f"✅ Created admin user: {admin.username}")

if not CustomUser.objects.filter(username='voice_registra').exists():
    registra = CustomUser.objects.create_user(
        username='voice_registra',
        email='registra@voice.test',
        password='voice123',
        first_name='Voice',
        last_name='Registra',
        role='registra'
    )
    print(f"✅ Created registra user: {registra.username}")

if not CustomUser.objects.filter(username='voice_professor').exists():
    prof = CustomUser.objects.create_user(
        username='voice_professor',
        email='prof@voice.test',
        password='voice123',
        first_name='Voice',
        last_name='Professor',
        role='professor'
    )
    print(f"✅ Created professor user: {prof.username}")

print("\n✅ Voice assistant test users ready!")
print("\nLogin credentials:")
print("  Admin:     voice_admin / voice123")
print("  Registra:  voice_registra / voice123")
print("  Professor: voice_professor / voice123")

# Example 2: Check voice endpoints
print("\n🔌 Available Voice API Endpoints:")
print("  POST   /voice/process/   - Process voice commands")
print("  GET    /voice/help/      - Get available commands for user role")

# Example 3: Example voice command flow
print("\n💬 Example Voice Commands:")
commands = [
    ('Admin', 'admin dashboard', '/admin-panel/'),
    ('Registra', 'code students', '/registra/'),
    ('Professor', 'grade course', '/professor/'),
    ('Any', 'how does it work', 'Answer: Workflow explanation...'),
]

for role, command, result in commands:
    print(f"  [{role}] Say: '{command}'")
    print(f"           → {result}")

print("\n📖 Check these files for more info:")
print("  - voice_assistant/README.md          (Full documentation)")
print("  - VOICE_ASSISTANT_SETUP.md           (Quick start guide)")
print("  - templates/components/voice_assistant.html  (UI component)")
print("  - templates/static/js/voice-assistant.js     (JavaScript logic)")
