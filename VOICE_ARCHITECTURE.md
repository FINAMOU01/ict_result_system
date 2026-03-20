# Voice Assistant Architecture & Flow Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             Voice Assistant Widget                        │  │
│  │         (Floating Button in Bottom-Right)               │  │
│  │                                                          │  │
│  │  [🎤 Voice Assistant]  [❓ Help]                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │      Web Speech API (Client-Side Processing)            │  │
│  │                                                          │  │
│  │  • Speech Recognition (Audio → Text)                   │  │
│  │  • Text-to-Speech (Text → Audio)                       │  │
│  │  • Real-time Transcript Display                        │  │
│  │  • Error Handling                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              JavaScript (voice-assistant.js)            │  │
│  │                                                          │  │
│  │  • Command/Question Parsing                            │  │
│  │  • CSRF Token Management                               │  │
│  │  • UI State Management                                 │  │
│  │  • Navigation Handling                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓ (AJAX POST)
┌─────────────────────────────────────────────────────────────────┐
│                      DJANGO BACKEND                             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Voice Assistant App (views.py)                  │  │
│  │                                                          │  │
│  │  process_voice_command():                              │  │
│  │  • Receive command string                              │  │
│  │  • Check VOICE_COMMANDS dict                           │  │
│  │  • Check PROJECT_KNOWLEDGE_BASE dict                  │  │
│  │  • Verify user role/permissions                        │  │
│  │  • Return navigation URL or answer                     │  │
│  │                                                          │  │
│  │  get_help():                                            │  │
│  │  • List available commands for user role               │  │
│  │  • Return knowledge base questions                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          Voice Command Log Model (Optional)             │  │
│  │                                                          │  │
│  │  • Log user, command, action_type, timestamp           │  │
│  │  • Viewable in Admin Panel                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ↓                                   │
│           ┌─────────────────────────────────────┐               │
│           │          SQLite Database            │               │
│           │  (VoiceCommandLog Table)            │               │
│           └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓ (JSON Response)
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│                                                                  │
│  Response Handling:                                             │
│  • Navigation: window.location.href = url                       │
│  • Question: Display message, speak answer                      │
│  • Unknown: Show helpful message                                │
└─────────────────────────────────────────────────────────────────┘
```

## Voice Command Processing Flow

```
╔════════════════════════════════════════════════════════════════╗
║                    USER SPEAKS COMMAND                         ║
║                                                                ║
║        "Admin Dashboard" / "How does it work?"                ║
╚════════════════════════════════════════════════════════════════╝
                              │
                              ↓
╔════════════════════════════════════════════════════════════════╗
║            WEB SPEECH API - SPEECH RECOGNITION               ║
║                                                                ║
║    Audio (mic input) ──→ Convert to Text String              ║
║                                                                ║
║    OUTPUT: "admin dashboard" (lowercase, normalized)           ║
╚════════════════════════════════════════════════════════════════╝
                              │
                              ↓
╔════════════════════════════════════════════════════════════════╗
║      JAVASCRIPT - COMMAND PROCESSING & VALIDATION           ║
║                                                                ║
║    1. Display transcript in real-time                         ║
║    2. Create AJAX POST request with command                  ║
║    3. Send to /voice/process/ endpoint                       ║
╚════════════════════════════════════════════════════════════════╝
                              │
                              ↓
╔════════════════════════════════════════════════════════════════╗
║        DJANGO BACKEND - COMMAND LOOKUP & VALIDATION         ║
║                                                                ║
║    Check User: Authenticated? ✓                               ║
║    Get Role: admin / registra / professor                    ║
║                                                                ║
║    Search VOICE_COMMANDS:                                     ║
║    ┌─────────────────────────────────────┐                   ║
║    │ For each command in dictionary:      │                   ║
║    │   if command_key in user_input:      │                   ║
║    │     check user role access           │                   ║
║    │     return URL (NAVIGATION)          │                   ║
║    └─────────────────────────────────────┘                   ║
║                              │                                 ║
║                    If NOT found ↓                              ║
║    Search PROJECT_KNOWLEDGE_BASE:                             ║
║    ┌─────────────────────────────────────┐                   ║
║    │ For each question in dictionary:     │                   ║
║    │   if question_key in user_input:     │                   ║
║    │     return answer (QUESTION)         │                   ║
║    └─────────────────────────────────────┘                   ║
║                              │                                 ║
║                    If NOT found ↓                              ║
║    Return helpful message (UNKNOWN)                            ║
╚════════════════════════════════════════════════════════════════╝
                              │
                              ↓
╔════════════════════════════════════════════════════════════════╗
║              JSON RESPONSE (Back to Browser)                 ║
║                                                                ║
║  NAVIGATION Response:                                          ║
║  {                                                             ║
║    "type": "navigation",                                      ║
║    "url": "/admin-panel/",                                    ║
║    "message": "Navigating to admin dashboard",               ║
║    "action": "go"                                             ║
║  }                                                             ║
║                                                                ║
║  QUESTION Response:                                            ║
║  {                                                             ║
║    "type": "question",                                        ║
║    "message": "Detailed answer...",                           ║
║    "action": "speak"                                          ║
║  }                                                             ║
╚════════════════════════════════════════════════════════════════╝
                              │
                              ↓
╔════════════════════════════════════════════════════════════════╗
║         JAVASCRIPT - HANDLE RESPONSE & USER ACTION           ║
║                                                                ║
║    Display message to user                                     ║
║    Speak response using Web Speech Synthesis API             ║
║                                                                ║
║    If NAVIGATION:                                              ║
║    └─→ window.location.href = url  (Navigate page)            ║
║                                                                ║
║    If QUESTION:                                                ║
║    └─→ speechSynthesis.speak(answer)  (Speak answer)          ║
║                                                                ║
║    If UNKNOWN:                                                 ║
║    └─→ Show "Try 'Help' button" message                       ║
╚════════════════════════════════════════════════════════════════╝
                              │
                              ↓
╔════════════════════════════════════════════════════════════════╗
║                   USER FEEDBACK & RESPONSE                    ║
║                                                                ║
║    ✓ See transcript of what was heard                          ║
║    ✓ See message in voice panel                                ║
║    ✓ Hear spoken response                                      ║
║    ✓ Navigate to page OR get answer                            ║
╚════════════════════════════════════════════════════════════════╝
```

## Command & Access Control Flow

```
                    ┌─ Admin has access to ALL
                    │  - admin_dashboard
                    │  - import_file
                    │  - manage_courses
                    │  - manage_students
                    │  - manage_semesters
USER ROLE ──────────┼─ Registra has access to
                    │  - registra_dashboard
                    │  - code_students
                    │  - decode_results
                    │  - lookup_code
                    │
                    └─ Professor has access to
                       - professor_dashboard
                       - grade_course


   ALL USERS ACCESS:
   ├─ Home / Dashboard
   ├─ Login / Logout  
   └─ Knowledge Base Questions
       (How does it work?, What are roles?, etc.)


ROLE FILTERING LOGIC:
   
   For EACH command:
   IF required_role == None
      THEN all users can use
   
   ELSE IF required_role == user.role
      THEN user can use
      
   ELSE IF user.role == 'admin'
      THEN admin can use any command
      
   ELSE
      THEN show "unknown command" message
```

## UI Component Hierarchy

```
base.html
├── Include voice_assistant.html (component)
│
└── voice_assistant.html
    │
    ├── Voice Widget Container (bottom-right)
    │   ├── Microphone Button (#voice-mic-btn)
    │   │   ├── Icon: 🎤
    │   │   ├── Text: "Voice Assistant"
    │   │   └── Class: "listening" (when active)
    │   │
    │   └── Help Button (#voice-help-btn)
    │       ├── Icon: ❓
    │       └── Text: "Help"
    │
    ├── Voice Panel (hidden until listening)
    │   ├── Header
    │   │   ├── Title: "Voice Assistant"
    │   │   └── Close Button (X)
    │   │
    │   └── Body
    │       ├── Message Display (#voice-message)
    │       │   ├── Alert (success/error/warning)
    │       │   └── CSS: d-none (hidden by default)
    │       │
    │       ├── Transcript Container
    │       │   ├── Label: "You said:"
    │       │   └── Transcript Text (#voice-transcript)
    │       │       └── Color: gray (interim) → black (final)
    │       │
    │       └── Status Indicator
    │           └── Spinning Badge: "🔄 Listening..."
    │
    └── Inline CSS
        ├── .voice-widget (floating position)
        ├── .voice-btn (button styles)
        ├── .voice-panel (modal-like panel)
        ├── @keyframes pulse (animation)
        └── @keyframes slideIn (animation)
```

## Database Schema

```
VoiceCommandLog Table:
┌─────────────────────────────────────────┐
│ Columns:                                │
│ • id (PK)                               │
│ • user (FK → CustomUser)                │
│ • command (VARCHAR 255)                 │
│ • action_type (VARCHAR 20)              │
│   - 'navigation'                        │
│   - 'question'                          │
│   - 'unknown'                           │
│ • response_message (TEXT)               │
│ • timestamp (DATETIME auto)             │
│                                         │
│ Indexes:                                │
│ • user_id                               │
│ • action_type                           │
│ • timestamp (for ordering)              │
└─────────────────────────────────────────┘

Example Records:
┌──────┬──────────────────┬──────────────────┬────────────┐
│ user │ command          │ action_type      │ timestamp  │
├──────┼──────────────────┼──────────────────┼────────────┤
│ john │ admin dashboard  │ navigation       │ 2026-03-19 │
│ jane │ how does it work │ question         │ 2026-03-19 │
│ bob  │ xyz123nonsense   │ unknown          │ 2026-03-19 │
└──────┴──────────────────┴──────────────────┴────────────┘
```

## Security & Authentication Flow

```
Request Flow:
1. User clicks Voice Button
2. Microphone activation (browser asks permission)
3. User speaks command
4. JavaScript sends AJAX POST to /voice/process/
   
   Headers:
   • X-CSRFToken: ??? (from cookie or meta tag)
   • Content-Type: application/json
   
   Body:
   {
     "command": "admin dashboard"
   }

5. Django @login_required decorator
   ├─ Check: Is user logged in?
   │  └─ If NO: Redirect to /login
   │  └─ If YES: Continue
   │
   ├─ Check: Valid CSRF token?
   │  └─ If NO: Return 403 Forbidden
   │  └─ If YES: Continue
   │
   └─ Check: User has role?
      └─ Filter commands by role
      └─ Return allowed commands only

6. Return JSON response
7. JavaScript handles response
8. Browser performs action (navigate or speak)
```

---

This architecture ensures:
✅ **Security**: CSRF protection, login required, role-based access
✅ **Privacy**: No cloud APIs, all processing local
✅ **Performance**: Client-side speech processing
✅ **Scalability**: Stateless backend, no session management
✅ **Maintainability**: Modular design, easy to customize
