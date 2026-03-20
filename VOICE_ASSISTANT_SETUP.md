# Voice Assistant - Quick Start Guide

Your ICT Results System now has a **Voice Assistant**! 🎤

## What's New?

A floating microphone button in the bottom-right corner allows you to:
- 🗣️ **Control pages with voice** - Say "Admin Dashboard" to navigate
- ❓ **Ask questions** - Ask "How does it work?" for instant answers  
- 🔊 **Get voice responses** - The assistant speaks answers back to you
- 🔐 **Role-based access** - Only see commands for your role

---

## Getting Started

### 1. Create an Admin User
```bash
python manage.py createsuperuser_admin
```

### 2. Start the Server
```bash
python manage.py runserver
```

### 3. Login and Find the Voice Button
- Go to http://localhost:8000
- Login with your credentials
- Look for the **blue microphone button** 🎤 in the bottom-right corner

---

## Try These Commands

### As Admin:
```
"Admin dashboard"           → Go to admin panel
"Import file"               → Go to import page
"Manage courses"            → List courses
"Manage students"           → List students
"How to import?"            → Get import instructions
```

### As Registra:
```
"Registra dashboard"        → Registra workspace
"Code students"             → Assign anonymous codes
"Decode results"            → Decode grades
"Lookup code"               → Search by code
"What is anonymous coding?" → Learn about coding
```

### As Professor:
```
"Professor dashboard"       → Professor workspace
"Grade course"              → Grade assignment
"My courses"                → View courses
"How does it work?"         → System overview
```

### General Questions:
```
"What is this system?"      → System overview
"What are the roles?"       → Learn about roles
"How does it work?"         → Workflow explanation
"What is registra?"         → Registra role explanation
```

---

## How It Works

1. **Click** the 🎤 **Voice Assistant** button
2. **Speak** clearly (your language browser default)
3. See your words appear in real-time
4. Get a response - either **navigate to a page** or **hear an answer**
5. **Done!** The assistant takes action

---

## Features Included

✅ **Voice Recognition** - Web Speech API support  
✅ **Text-to-Speech** - Hear responses read aloud  
✅ **Role-Based Access** - Commands filtered by user role  
✅ **Knowledge Base** - Answers to common questions  
✅ **Android/iOS Support** - Works on mobile too  
✅ **Command Logging** - Optional tracking in admin panel  
✅ **No server processing** - Speech happens in your browser  

---

## What If It Doesn't Work?

### Microphone permission needed?
- Check browser permission for microphone
- Try Chrome, Edge, or newer Firefox
- Allow microphone access when prompted

### Browser compatibility?
| Browser | Support |
|---------|---------|
| Chrome | ✅ Best |
| Edge | ✅ Full |
| Firefox | ⚠️ Limited |
| Safari | ⚠️ Limited |

### For troubleshooting:
1. Open browser console (F12 → Console tab)
2. Click the voice button and try a command
3. Check for error messages
4. Try a simpler command like "home"

---

## Admin Features

### View Voice Command Logs
```
Admin Panel → Voice Command Logs
```

See:
- Which users used voice commands
- What they said
- When they used it
- Success rate

---

## Customize Commands

Edit `/voice_assistant/views.py` and modify:

```python
VOICE_COMMANDS = {
    'your new command': {'url': '/your-url/', 'role': 'admin'},
    'general command': {'url': '/url/', 'role': None},
}
```

Then restart: `python manage.py runserver`

---

## Add Knowledge Base Answers

In `/voice_assistant/views.py`, edit:

```python
PROJECT_KNOWLEDGE_BASE = {
    'question keyword here': 'Your answer text here',
}
```

Example:
```python
'how long is semester': 'A semester lasts approximately 14-16 weeks.',
```

---

## Files Created

```
voice_assistant/
  ├── views.py              # Command processing logic
  ├── urls.py               # API endpoints
  ├── models.py             # VoiceCommandLog model
  ├── admin.py              # Admin panel integration
  ├── tests.py              # Unit tests
  ├── README.md             # Full documentation
  └── migrations/           # Database migrations

templates/
  ├── components/
  │   └── voice_assistant.html   # UI widget
  └── static/js/
      └── voice-assistant.js      # Frontend logic

database:
  └── VoiceCommandLog        # Track all voice commands
```

---

## Test It Now

Run the test suite:
```bash
python manage.py test voice_assistant
```

Expected output: ✅ All tests pass

---

## Next Steps

1. ✅ Create an admin account
2. ✅ Login and try voice commands
3. ✅ Check Admin Panel → Voice Command Logs
4. ✅ Customize commands for your needs
5. ✅ Share with team and gather feedback

---

## Questions or Issues?

Check:
- `voice_assistant/README.md` - Full technical docs
- `voice_assistant/views.py` - Command definitions
- `templates/components/voice_assistant.html` - UI code
- Browser console (F12) for errors

---

## Privacy Note

✅ **Your speech stays private:**
- No audio sent to server
- Speech recognition happens locally
- Only processed keywords sent
- Optional logging available to admin only

---

**Enjoy your hands-free ICT Results System!** 🚀
