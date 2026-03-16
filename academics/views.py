from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Semester, Course, Student, Enrollment, ImportLog
from .forms import SemesterForm, ImportFileForm, AssignProfessorForm
from .utils import import_enrollment_file
from accounts.models import CustomUser
from results.models import Grade


def role_required(roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                messages.error(request, "Access denied.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        wrapper.__name__ = view_func.__name__
        return wrapper
    return decorator


@login_required
def dashboard_redirect(request):
    from accounts.views import dashboard_redirect as acc_redirect
    return acc_redirect(request)


# ─── ADMIN VIEWS ──────────────────────────────────────────────────────────────

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    active_semester = Semester.objects.filter(is_active=True).first()
    stats = {
        'semesters': Semester.objects.count(),
        'students': Student.objects.count(),
        'courses': Course.objects.filter(semester=active_semester).count() if active_semester else 0,
        'professors': CustomUser.objects.filter(role='professor', is_active=True).count(),
        'enrollments': Enrollment.objects.filter(semester=active_semester).count() if active_semester else 0,
        'import_logs': ImportLog.objects.order_by('-created_at')[:5],
        'pending_assignments': Course.objects.filter(semester=active_semester, professor__isnull=True).count() if active_semester else 0,
    }
    return render(request, 'admin_panel/dashboard.html', {
        'active_semester': active_semester,
        'stats': stats,
    })


@login_required
@role_required(['admin'])
def semester_list(request):
    semesters = Semester.objects.annotate(
        course_count=Count('courses'),
        enrollment_count=Count('enrollments')
    ).order_by('-created_at')
    form = SemesterForm()
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Semester created successfully.")
            return redirect('semester_list')
    return render(request, 'admin_panel/semesters.html', {'semesters': semesters, 'form': form})


@login_required
@role_required(['admin'])
def import_file(request):
    form = ImportFileForm()
    if request.method == 'POST':
        form = ImportFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                log = import_enrollment_file(
                    request.FILES['file'],
                    form.cleaned_data['semester'].id,
                    request.user
                )
                messages.success(request,
                    f"Import successful! {log.students_created} new students, "
                    f"{log.courses_created} new courses, {log.enrollments_created} enrollments created."
                )
                if log.errors:
                    messages.warning(request, f"Some rows had errors:\n{log.errors[:500]}")
                return redirect('admin_dashboard')
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Import failed: {str(e)}")
    return render(request, 'admin_panel/import_file.html', {'form': form})


@login_required
@role_required(['admin'])
def course_list(request):
    semester_id = request.GET.get('semester')
    level_filter = request.GET.get('level')
    semesters = Semester.objects.all().order_by('-created_at')
    active_semester = Semester.objects.filter(is_active=True).first()
    selected_semester = None

    courses = Course.objects.select_related('professor', 'semester').annotate(
        student_count=Count('enrollments')
    )
    if semester_id:
        courses = courses.filter(semester_id=semester_id)
        selected_semester = get_object_or_404(Semester, id=semester_id)
    elif active_semester:
        courses = courses.filter(semester=active_semester)
        selected_semester = active_semester
    if level_filter:
        courses = courses.filter(level=level_filter)

    return render(request, 'admin_panel/courses.html', {
        'courses': courses.order_by('name'),
        'semesters': semesters,
        'selected_semester': selected_semester,
        'level_filter': level_filter,
    })


@login_required
@role_required(['admin'])
def assign_professor(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = AssignProfessorForm(request.POST or None, instance=course)
    if request.method == 'POST' and form.is_valid():
        form.save()
        prof = course.professor
        msg = f"Professor {prof.get_full_name()} assigned to {course.code}." if prof else f"Professor unassigned from {course.code}."
        messages.success(request, msg)
        return redirect('course_list')
    return render(request, 'admin_panel/assign_professor.html', {'form': form, 'course': course})


@login_required
@role_required(['admin'])
def student_list(request):
    query = request.GET.get('q', '')
    level_filter = request.GET.get('level', '')
    students = Student.objects.annotate(enrollment_count=Count('enrollments'))
    if query:
        students = students.filter(
            Q(matricule__icontains=query) |
            Q(last_name__icontains=query) |
            Q(first_name__icontains=query)
        )
    if level_filter:
        students = students.filter(level=level_filter)
    return render(request, 'admin_panel/students.html', {
        'students': students.order_by('last_name'),
        'query': query,
        'level_filter': level_filter,
    })


# ─── REGISTRA VIEWS ──────────────────────────────────────────────────────────

@login_required
@role_required(['registra'])
def registra_dashboard(request):
    active_semester = Semester.objects.filter(is_active=True).first()
    if active_semester:
        courses = Course.objects.filter(semester=active_semester).annotate(
            student_count=Count('enrollments')
        ).order_by('name')
    else:
        courses = Course.objects.none()
    return render(request, 'registra/dashboard.html', {
        'active_semester': active_semester,
        'courses': courses,
    })


@login_required
@role_required(['registra'])
def registra_semester_history(request):
    from django.db.models import Count, Q
    
    # Fetch all semesters with courses
    query = request.GET.get('q', '').strip()
    
    all_semesters = Semester.objects.filter(
        courses__isnull=False
    ).distinct().order_by('-created_at')
    
    # Filter by search query if provided
    if query:
        all_semesters = all_semesters.filter(
            Q(name__icontains=query) |
            Q(academic_year__icontains=query)
        )
    
    # Collect data for each semester
    semesters_with_data = []
    total_all_courses = 0
    total_all_graded = 0
    total_all_decoded = 0
    
    active_semester = Semester.objects.filter(is_active=True).first()
    
    for semester in all_semesters:
        courses = Course.objects.filter(semester=semester).annotate(
            student_count=Count('enrollments')
        ).order_by('name')
        
        # Count graded and decoded for this semester
        graded_count = courses.filter(grades_submitted=True).count()
        decoded_count = courses.filter(is_decoded=True).count()
        
        semesters_with_data.append({
            'semester': semester,
            'courses': courses,
            'graded_count': graded_count,
            'decoded_count': decoded_count,
        })
        
        # Accumulate totals
        total_all_courses += courses.count()
        total_all_graded += graded_count
        total_all_decoded += decoded_count
    
    return render(request, 'registra/semester_history.html', {
        'active_semester': active_semester,
        'semesters_with_data': semesters_with_data,
        'query': query,
        'total_courses': total_all_courses,
        'total_graded': total_all_graded,
        'total_decoded': total_all_decoded,
    })


@login_required
@role_required(['registra'])
def registra_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = course.enrollments.select_related('student').order_by('student__last_name')
    query = request.GET.get('q', '')
    if query:
        enrollments = enrollments.filter(
            Q(student__matricule__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__first_name__icontains=query)
        )
    return render(request, 'registra/course_detail.html', {
        'course': course,
        'enrollments': enrollments,
        'query': query,
    })


@login_required
@role_required(['registra'])
def add_walkin_student(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if course is already coded
    if course.is_coded:
        messages.error(request, "Cannot add students after coding has started.")
        return redirect('registra_course_detail', course_id=course_id)
    
    if request.method == 'POST':
        from .forms import WalkInStudentForm
        form = WalkInStudentForm(request.POST)
        if form.is_valid():
            matricule = form.cleaned_data['matricule'].strip()
            first_name = form.cleaned_data['first_name'].strip().title()
            last_name = form.cleaned_data['last_name'].strip().upper()
            
            # Check if student exists
            try:
                student = Student.objects.get(matricule=matricule)
            except Student.DoesNotExist:
                # Create new walk-in student
                student = Student.objects.create(
                    matricule=matricule,
                    first_name=first_name,
                    last_name=last_name,
                    level='bachelor',  # Default level for walk-ins
                    is_walkin=True
                )
            
            # Check if already enrolled in this course
            enrollment_exists = Enrollment.objects.filter(
                student=student,
                course=course,
                semester=course.semester
            ).exists()
            
            if enrollment_exists:
                messages.error(request, f"This student ({student.matricule}) is already enrolled in this course.")
                return redirect('add_walkin_student', course_id=course_id)
            
            # Create enrollment
            Enrollment.objects.create(
                student=student,
                course=course,
                semester=course.semester
            )
            
            messages.success(request, f"✅ {student.full_name()} ({student.matricule}) added to {course.code}.")
            return redirect('registra_course_detail', course_id=course_id)
    else:
        from .forms import WalkInStudentForm
        form = WalkInStudentForm()
    
    return render(request, 'registra/add_walkin_student.html', {
        'form': form,
        'course': course,
    })


@login_required
@role_required(['registra'])
def generate_codes(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.is_coded:
        messages.warning(request, f"Codes already generated for {course.code}. Cannot re-code.")
        return redirect('registra_course_detail', course_id=course_id)
    if request.method == 'POST':
        from results.utils import generate_codes_for_course
        count = generate_codes_for_course(course)
        messages.success(request, f"✅ {count} anonymous codes generated for {course.code} - {course.name}.")
        return redirect('registra_course_detail', course_id=course_id)
    return render(request, 'registra/confirm_code.html', {'course': course})


@login_required
@role_required(['registra'])
def download_coding_sheet(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not course.is_coded:
        messages.error(request, "Generate codes first before downloading.")
        return redirect('registra_course_detail', course_id=course_id)
    from results.utils import generate_coding_sheet
    from django.http import HttpResponse
    buffer = generate_coding_sheet(course)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="CONFIDENTIAL_{course.code}_coding_sheet.xlsx"'
    return response


@login_required
@role_required(['registra'])
def lookup_code(request):
    """Registra can look up a matricule to find the student's code."""
    result = None
    active_semester = Semester.objects.filter(is_active=True).first()
    if request.method == 'GET' and request.GET.get('matricule'):
        matricule = request.GET.get('matricule', '').strip()
        course_id = request.GET.get('course_id')
        try:
            if course_id:
                enrollment = Enrollment.objects.select_related('student', 'course').get(
                    student__matricule__iexact=matricule,
                    course_id=course_id
                )
            else:
                enrollment = Enrollment.objects.select_related('student', 'course').filter(
                    student__matricule__iexact=matricule,
                    course__semester=active_semester
                ).first()
            result = enrollment
        except Enrollment.DoesNotExist:
            messages.error(request, f"No enrollment found for matricule '{matricule}'.")
    courses = Course.objects.filter(semester=active_semester, is_coded=True).order_by('name') if active_semester else []
    return render(request, 'registra/lookup_code.html', {
        'result': result,
        'courses': courses,
        'active_semester': active_semester,
    })


@login_required
@role_required(['registra'])
def download_decoded_results(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not course.grades_submitted:
        messages.error(request, "Professor has not submitted grades yet.")
        return redirect('registra_dashboard')
    from results.utils import generate_results_excel
    from django.http import HttpResponse
    buffer = generate_results_excel(course)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{course.code}_results_{course.semester.name}.xlsx"'
    return response


# ─── PROFESSOR VIEWS ──────────────────────────────────────────────────────────

@login_required
@role_required(['professor'])
def professor_dashboard(request):
    active_semester = Semester.objects.filter(is_active=True).first()
    if active_semester:
        courses = Course.objects.filter(
            professor=request.user,
            semester=active_semester
        ).annotate(student_count=Count('enrollments')).order_by('name')
    else:
        courses = Course.objects.none()
    return render(request, 'professor/dashboard.html', {
        'active_semester': active_semester,
        'courses': courses,
    })


@login_required
@role_required(['professor'])
def professor_grade_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, professor=request.user)
    if not course.is_coded:
        messages.warning(request, "The registra has not coded this course yet. Please wait.")
        return redirect('professor_dashboard')

    from results.models import Grade
    enrollments = course.enrollments.select_related('grade').order_by('anonymous_code')

    if request.method == 'POST':
        if course.grades_submitted:
            messages.error(request, "Grades already submitted. Cannot modify.")
            return redirect('professor_dashboard')
        errors = []
        for enrollment in enrollments:
            cc_key = f'cc_{enrollment.id}'
            sn_key = f'sn_{enrollment.id}'
            cc_val = request.POST.get(cc_key, '').strip()
            sn_val = request.POST.get(sn_key, '').strip()
            try:
                grade, _ = Grade.objects.get_or_create(enrollment=enrollment)
                if cc_val:
                    cc = float(cc_val)
                    if not 0 <= cc <= 30:
                        raise ValueError("CC score must be between 0 and 30")
                    grade.cc_score = cc
                if sn_val:
                    sn = float(sn_val)
                    if not 0 <= sn <= 70:
                        raise ValueError("SN score must be between 0 and 70")
                    grade.sn_score = sn
                grade.calculate_final()
                grade.save()
            except ValueError as e:
                errors.append(f"Code {enrollment.anonymous_code}: {e}")

        if 'submit_final' in request.POST and not errors:
            from django.utils import timezone
            Grade.objects.filter(enrollment__course=course).update(
                status='submitted',
                submitted_by=request.user,
                submitted_at=timezone.now()
            )
            course.grades_submitted = True
            course.grades_submitted_at = timezone.now()
            course.save()
            messages.success(request, f"✅ Grades for {course.code} submitted to Registra successfully!")
            return redirect('professor_dashboard')
        elif errors:
            for e in errors:
                messages.error(request, e)
        else:
            messages.success(request, "Grades saved. Review and click 'Submit to Registra' when ready.")

    return render(request, 'professor/grade_course.html', {
        'course': course,
        'enrollments': enrollments,
    })


# ─── REGISTRA VIEWS ───────────────────────────────────────────────────────────

@login_required
@role_required(['registra'])
def registra_view_anonymous_results(request, course_id):
    """View anonymous results (code, CC, SN, Final) before decoding."""
    course = get_object_or_404(Course, id=course_id)
    
    if not course.grades_submitted:
        messages.error(request, "Grades have not been submitted for this course yet.")
        return redirect('registra_dashboard')
    
    enrollments = course.enrollments.select_related('grade').order_by('anonymous_code')
    
    return render(request, 'registra/anonymous_results.html', {
        'course': course,
        'enrollments': enrollments,
    })


@login_required
@role_required(['registra'])
def registra_decode_results(request, course_id):
    """Decode results (POST only)."""
    course = get_object_or_404(Course, id=course_id)
    
    if not course.grades_submitted:
        messages.error(request, "Grades have not been submitted for this course yet.")
        return redirect('registra_dashboard')
    
    course.is_decoded = True
    course.save()
    
    messages.success(request, f"✅ Results for {course.code} have been decoded successfully!")
    return redirect('registra_decoded_results', course_id=course.id)


@login_required
@role_required(['registra'])
def registra_decoded_results(request, course_id):
    """View decoded results with student information."""
    course = get_object_or_404(Course, id=course_id)
    
    if not course.is_decoded:
        messages.error(request, "Results have not been decoded for this course yet.")
        return redirect('registra_dashboard')
    
    enrollments = course.enrollments.select_related('student', 'grade').order_by('student__last_name', 'student__first_name')
    
    # Add remarks to each enrollment
    for enrollment in enrollments:
        if enrollment.grade and enrollment.grade.final_score is not None:
            enrollment.remarks = 'PASS' if enrollment.grade.final_score >= 10 else 'FAIL'
        else:
            enrollment.remarks = 'N/A'
    
    return render(request, 'registra/decoded_results.html', {
        'course': course,
        'enrollments': enrollments,
    })
