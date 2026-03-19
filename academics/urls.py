from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard'),
    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/reset-demo-data/', views.reset_demo_data, name='reset_demo_data'),
    path('admin-panel/activity-log/', views.activity_log, name='activity_log'),
    path('admin-panel/semesters/', views.semester_list, name='semester_list'),
    path('admin-panel/semesters/<int:semester_id>/edit/', views.semester_edit, name='semester_edit'),
    path('admin-panel/import/', views.import_file, name='import_file'),
    path('admin-panel/courses/', views.course_list, name='course_list'),
    path('admin-panel/courses/<int:course_id>/students/', views.admin_course_students, name='admin_course_students'),
    path('admin-panel/courses/<int:course_id>/assign/', views.assign_professor, name='assign_professor'),
    path('admin-panel/students/', views.student_list, name='student_list'),
    path('admin-panel/admissions/', views.admissions_registry, name='admissions_registry_admin'),
    # Registra
    path('registra/', views.registra_dashboard, name='registra_dashboard'),
    path('registra/semester-history/', views.registra_semester_history, name='registra_semester_history'),
    path('registra/admissions/', views.admissions_registry, name='admissions_registry_registra'),
    path('registra/course/<int:course_id>/', views.registra_course_detail, name='registra_course_detail'),
    path('registra/course/<int:course_id>/add-from-admissions/', views.add_from_admissions, name='add_from_admissions'),
    path('registra/course/<int:course_id>/add-walkin/', views.add_walkin_student, name='add_walkin_student'),
    path('registra/course/<int:course_id>/code/', views.generate_codes, name='generate_codes'),
    path('registra/course/<int:course_id>/coding-sheet/', views.download_coding_sheet, name='download_coding_sheet'),
    path('registra/course/<int:course_id>/anonymous-results/', views.registra_view_anonymous_results, name='registra_anonymous_results'),
    path('registra/course/<int:course_id>/decode/', views.registra_decode_results, name='registra_decode_results'),
    path('registra/course/<int:course_id>/decoded-results/', views.registra_decoded_results, name='registra_decoded_results'),
    path('registra/lookup/', views.lookup_code, name='lookup_code'),
    path('registra/course/<int:course_id>/download/', views.download_decoded_results, name='download_decoded_results'),
    # Professor
    path('professor/', views.professor_dashboard, name='professor_dashboard'),
    path('professor/course/<int:course_id>/grades/', views.professor_grade_course, name='professor_grade_course'),
]
