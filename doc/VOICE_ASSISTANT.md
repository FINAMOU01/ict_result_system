# Voice Assistant for ICT Results System

A smart voice-controlled assistant that allows you to navigate the ICT University Results Management System hands-free and ask questions about the project.

## Features

✨ **Voice Navigation**
- Say commands like "Admin Dashboard", "Registra Dashboard", "Professor Dashboard"
- Automatically navigates based on your user role
- Works with role-based access control

🎤 **Voice Control**
- Click the microphone button to start listening
- Uses Web Speech API for speech recognition
- Real-time transcript display

🔊 **Voice Response**
- Assistant speaks responses using text-to-speech
- Answers common questions about the system
- Provides helpful feedback

❓ **Knowledge Base**
- Ask questions like "How does it work?"
- "What is admin?" "How to import data?"
- "What is anonymous coding?"

## Supported Voice Commands

### Admin Commands
```
"Admin Dashboard" → Go to admin panel
"Admin Panel" → Go to admin panel
"Import File" → Go to import CSV page
"Manage Courses" → List all courses
"Manage Students" → List all students
"Manage Semesters" → Manage academic semesters
"Activity Log" → View system activity log
```

### Registra Commands
```
"Registra Dashboard" → Go to registra dashboard
"Code Students" → Assign anonymous codes
"Download Sheet" → Download coding sheet
"Decode Results" → Decode anonymous grades
"Lookup Code" → Search for student by code
"Semester History" → View past semesters
```

### Professor Commands
```
"Professor Dashboard" → Go to professor workspace
"Grade Course" → View courses to grade
"Enter Grades" → Grade assignment
"My Courses" → List assigned courses
```

### Questions You Can Ask
```
"What is this system?" → System overview
"How does it work?" → Workflow explanation
"What are the roles?" → Role descriptions
"How to import?" → Import instructions
"What is anonymous coding?" → Anonymous coding explanation
```

## How to Use

1. **Click the Voice Button**
   - Look for the blue "🎤 Voice Assistant" button in the bottom-right corner
   - Click to activate microphone

2. **Speak Your Command**
   - Say a page name: "Admin Dashboard"
   - Or ask a question: "How does it work?"
   - Speak clearly and naturally

3. **Get Response**
   - The assistant will understand your command
   - Navigate to the page OR answer your question
   - You'll hear a voice response

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | Best support |
| Edge | ✅ Full | Works perfectly |
| Firefox | ⚠️ Limited | Some older versions limited |
| Safari | ⚠️ Limited | Mobile Safari has restrictions |

## Technical Details

### Backend (`voice_assistant/views.py`)
- `process_voice_command` - Processes voice and returns navigation or answers
- `get_help` - Returns available commands for user's role
- CSRF protected with Django authentication
- Role-based command filtering

### Frontend (`static/js/voice-assistant.js`)
- Uses Web Speech API for recognition
- Uses Web Speech Synthesis API for responses
- Real-time transcript display
- Error handling and fallbacks

### Components
- `templates/components/voice_assistant.html` - UI widget with animated button
- Bootstrap 5 styling with Font Awesome icons
- Responsive design for mobile and desktop

## Configuration

To add more commands, edit `VOICE_COMMANDS` dictionary in `voice_assistant/views.py`:

```python
VOICE_COMMANDS = {
    'your command': {'url': '/your-url/', 'role': 'admin'},  # admin only
    'general command': {'url': '/url/', 'role': None},  # all users
}
```

To add knowledge base answers, edit `PROJECT_KNOWLEDGE_BASE`:

```python
PROJECT_KNOWLEDGE_BASE = {
    'question keywords': 'Your answer here',
}
```

## Optional: Enable Command Logging

Commands are automatically logged in the database. View logs:

1. Go to Admin Panel → Voice Command Logs
2. Filter by user, action type, or date
3. Analyze usage patterns

## Troubleshooting

### Microphone not working
- Check browser permissions for microphone
- Ensure HTTPS if not on localhost
- Try Chrome or Edge browser

### Not understanding commands
- Speak clearly and naturally
- Use exact page names or question keywords
- Click "Help" button to see all available commands

### No voice response
- Check browser has audio output enabled
- Try saying something again
- Check browser console for errors (F12)

## Privacy & Security

✅ All voice processing happens in the browser (client-side)
✅ Commands sent as encrypted POST to backend only when processed
✅ Requires login - anonymous users cannot use
✅ Role-based access control enforced
✅ Optional logging for admin review only

## API Endpoints

### POST `/voice/process/`
Process a voice command
```json
{
  "command": "admin dashboard"
}
```

Response:
```json
{
  "type": "navigation",
  "url": "/admin-panel/",
  "message": "Navigating to admin dashboard",
  "action": "go"
}
```

### GET `/voice/help/`
Get available commands for current user
```json
{
  "commands": {"command": "url"},
  "knowledge_base": ["question", "question"],
  "user_role": "admin"
}
```

## Future Enhancements

- [ ] Natural language processing (NLP) for better understanding
- [ ] Command history and bookmarks
- [ ] Custom voice profiles
- [ ] Multi-language support
- [ ] Command shortcuts
- [ ] Integration with other systems
