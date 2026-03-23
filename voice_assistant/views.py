import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from academics.models import Semester, Course, Student, Enrollment
from accounts.models import CustomUser


# Language translations
LANGUAGES = {
    'en': {
        'admin_dashboard': ['admin dashboard', 'admin panel'],
        'import_file': ['import file', 'import data'],
        'manage_courses': ['manage courses'],
        'manage_students': ['manage students'],
        'manage_semesters': ['manage semesters'],
        'activity_log': ['activity log'],
        'registra_dashboard': ['registra dashboard', 'registra home'],
        'code_students': ['code students'],
        'download_sheet': ['download sheet'],
        'decode_results': ['decode results'],
        'lookup_code': ['lookup code'],
        'professor_dashboard': ['professor dashboard'],
        'grade_course': ['grade course', 'enter grades'],
        'my_courses': ['my courses'],
        'home': ['home', 'dashboard'],
        'login': ['login'],
        'logout': ['logout'],
        'help': ['help'],
    },
    'fr': {
        'admin_dashboard': ['tableau de bord admin', 'panneau admin'],
        'import_file': ['importer fichier', 'importer données'],
        'manage_courses': ['gérer cours'],
        'manage_students': ['gérer étudiants'],
        'manage_semesters': ['gérer semestres'],
        'activity_log': ['journal activité'],
        'registra_dashboard': ['tableau registra', 'accueil registra'],
        'code_students': ['coder étudiants'],
        'download_sheet': ['télécharger feuille'],
        'decode_results': ['décoder résultats'],
        'lookup_code': ['rechercher code'],
        'professor_dashboard': ['tableau professeur'],
        'grade_course': ['noter cours', 'saisir notes'],
        'my_courses': ['mes cours'],
        'home': ['accueil', 'tableau de bord'],
        'login': ['connexion'],
        'logout': ['déconnexion'],
        'help': ['aide'],
    }
}

# Command mappings: what the user says -> where to navigate
VOICE_COMMANDS = {
    # Admin commands
    'admin dashboard': {'url': '/admin-panel/', 'role': 'admin'},
    'admin panel': {'url': '/admin-panel/', 'role': 'admin'},
    'import file': {'url': '/admin-panel/import/', 'role': 'admin'},
    'import data': {'url': '/admin-panel/import/', 'role': 'admin'},
    'manage courses': {'url': '/admin-panel/courses/', 'role': 'admin'},
    'manage students': {'url': '/admin-panel/students/', 'role': 'admin'},
    'manage semesters': {'url': '/admin-panel/semesters/', 'role': 'admin'},
    'activity log': {'url': '/admin-panel/activity-log/', 'role': 'admin'},
    'admissions': {'url': '/admin-panel/admissions/', 'role': 'admin'},
    'report': {'url': '#report', 'role': 'admin'},  # Special handler for report
    'statistics': {'url': '#report', 'role': 'admin'},
    'overview': {'url': '#report', 'role': 'admin'},
    'rapport': {'url': '#report', 'role': 'admin'},  # French
    'statistique': {'url': '#report', 'role': 'admin'},  # French
    
    # Registra commands
    'registra dashboard': {'url': '/registra/', 'role': 'registra'},
    'registra home': {'url': '/registra/', 'role': 'registra'},
    'code students': {'url': '/registra/', 'role': 'registra'},
    'download sheet': {'url': '/registra/', 'role': 'registra'},
    'decode results': {'url': '/registra/', 'role': 'registra'},
    'lookup code': {'url': '/registra/lookup/', 'role': 'registra'},
    'semester history': {'url': '/registra/semester-history/', 'role': 'registra'},
    
    # Professor commands
    'professor dashboard': {'url': '/professor/', 'role': 'professor'},
    'grade course': {'url': '/professor/', 'role': 'professor'},
    'enter grades': {'url': '/professor/', 'role': 'professor'},
    'my courses': {'url': '/professor/', 'role': 'professor'},
    
    # General commands
    'home': {'url': '/', 'role': None},
    'login': {'url': '/accounts/login/', 'role': None},
    'logout': {'url': '/accounts/logout/', 'role': None},
    'dashboard': {'url': '/', 'role': None},
    'user list': {'url': '/accounts/users/', 'role': 'admin'},
    'create user': {'url': '/accounts/create/', 'role': 'admin'},
}

# Answers to common questions about the system
PROJECT_KNOWLEDGE_BASE = {
    'en': {
        'what is this system': 'This is the ICT University Results Management System. It manages student examination results with anonymous coding for secure grading.',
        'how does it work': 'Students are assigned anonymous codes. Professors enter grades using codes. Registra decodes results to get student names.',
        'what are the roles': 'Admin imports data and manages users. Registra codes students and decodes results. Professor enters grades anonymously.',
        'what is admin': 'Admin users can import CSV files, manage courses, students, semesters, and assign professors.',
        'what is registra': 'Registra users code students anonymously, download coding sheets, and decode final results.',
        'what is professor': 'Professors view anonymous codes and enter course scores and semester notes.',
        'how to import': 'Go to Admin Panel > Import File. Upload a CSV with student and course data.',
        'how to code students': 'In Registra area, select a course and click Code to generate anonymous codes.',
        'how to decode results': 'After professors submit grades, Registra clicks Decode to see student names with their grades.',
        'what is anonymous coding': 'A security feature where students get random codes (1,2,3...) instead of using names during grading.',
    },
    'fr': {
        'what is this system': 'Ceci est le Système de Gestion des Résultats de l\'Université ICT. Il gère les résultats d\'examens avec codage anonyme pour une notation sécurisée.',
        'how does it work': 'Les étudiants reçoivent des codes anonymes. Les professeurs entrent les notes en utilisant les codes. Le Registraire décode pour obtenir les noms.',
        'what are the roles': 'Admin importe les données et gère les utilisateurs. Registraire code les étudiants et décode les résultats. Professeur entre les notes anonymement.',
        'what is admin': 'Les utilisateurs Admin peuvent importer des fichiers CSV, gérer les cours, les étudiants et les semestres.',
        'what is registra': 'Les utilisateurs Registraire codent les étudiants, téléchargent les feuilles de codage et décodent les résultats finaux.',
        'what is professor': 'Les professeurs voient les codes anonymes et entrent les scores de cours et les notes du semestre.',
        'how to import': 'Allez à Panneau Admin > Importer Fichier. Téléchargez un CSV avec les données étudiants et cours.',
        'how to code students': 'Dans la zone Registraire, sélectionnez un cours et cliquez sur Coder pour générer des codes anonymes.',
        'how to decode results': 'Une fois que les professeurs ont soumis les notes, le Registraire clique sur Décoder pour voir les noms des étudiants avec leurs notes.',
        'what is anonymous coding': 'Une fonctionnalité de sécurité où les étudiants reçoivent des codes aléatoires (1,2,3...) à la place des noms pendant la notation.',
    }
}


@login_required
@require_POST
@csrf_exempt
def process_voice_command(request):
    """Process voice commands and return navigation or answers"""
    try:
        data = json.loads(request.body)
        command = data.get('command', '').lower().strip()
        language = data.get('language', 'en')  # Get language from request, default to English
        
        if not command:
            return JsonResponse({'error': 'No command provided'}, status=400)
        
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # First check if it's a navigation command
        for key, value in VOICE_COMMANDS.items():
            if key in command:
                required_role = value['role']
                
                # Check if user has permission
                if required_role is None or user_role == required_role or user_role == 'admin':
                    return JsonResponse({
                        'type': 'navigation',
                        'url': value['url'],
                        'message': f"Navigating to {key}" if language == 'en' else f"Navigation vers {key}",
                        'action': 'go'
                    })
        
        # Check if it's a knowledge base question (check current language's KB)
        kb_current_lang = PROJECT_KNOWLEDGE_BASE.get(language, PROJECT_KNOWLEDGE_BASE.get('en', {}))
        
        for question, answer in kb_current_lang.items():
            if question in command:
                return JsonResponse({
                    'type': 'question',
                    'message': answer,
                    'action': 'speak'
                })
        
        # If no exact match, try fuzzy matching
        for question, answer in kb_current_lang.items():
            keywords = question.split()
            if any(keyword in command for keyword in keywords):
                return JsonResponse({
                    'type': 'question',
                    'message': answer,
                    'action': 'speak'
                })
        
        # Default response
        unknown_msg = "I didn't understand this" if language == 'en' else "Je n'ai pas compris cela"
        suggest_msg = "Try asking about pages or questions from Help" if language == 'en' else "Essayez de poser une question depuis l'aide"
        
        return JsonResponse({
            'type': 'unknown',
            'message': f"{unknown_msg}. {suggest_msg}",
            'action': 'speak'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_help(request):
    """Return available voice commands for the user's role"""
    language = request.GET.get('language', 'en')
    user = request.user
    user_role = getattr(user, 'role', None)
    
    # Filter commands based on user role
    available_commands = {}
    
    for command, details in VOICE_COMMANDS.items():
        required_role = details['role']
        if required_role is None or user_role == required_role or user_role == 'admin':
            available_commands[command] = details['url']
    
    kb_current_lang = PROJECT_KNOWLEDGE_BASE.get(language, PROJECT_KNOWLEDGE_BASE.get('en', {}))
    
    return JsonResponse({
        'commands': available_commands,
        'knowledge_base': list(kb_current_lang.keys()),
        'user_role': user_role,
        'language': language,
        'available_languages': ['en', 'fr']
    })


@login_required
def get_system_report(request):
    """Get system statistics for the report dashboard"""
    try:
        # Get total counts
        total_semesters = Semester.objects.count()
        total_students = Student.objects.count()
        total_courses = Course.objects.count()
        total_professors = CustomUser.objects.filter(role='professor').count()
        total_enrollments = Enrollment.objects.count()
        
        # Get active semester
        active_semester = Semester.objects.filter(is_active=True).first()
        active_semester_name = active_semester.name if active_semester else 'None'
        
        # Get pending assignments (courses without professors)
        pending_assignments = Course.objects.filter(professor__isnull=True).count()
        
        # Get grades submitted
        grades_submitted = Course.objects.filter(grades_submitted=True).count()
        
        # Get courses coded
        courses_coded = Course.objects.filter(is_coded=True).count()
        
        # Get courses decoded
        courses_decoded = Course.objects.filter(is_decoded=True).count()
        
        # Get active courses this semester
        active_courses = Course.objects.filter(semester=active_semester).count() if active_semester else 0
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'total_semesters': total_semesters,
                'total_students': total_students,
                'total_courses': total_courses,
                'total_professors': total_professors,
                'total_enrollments': total_enrollments,
                'pending_assignments': pending_assignments,
                'grades_submitted': grades_submitted,
                'courses_coded': courses_coded,
                'courses_decoded': courses_decoded,
                'active_semester': active_semester_name,
                'active_courses': active_courses,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
