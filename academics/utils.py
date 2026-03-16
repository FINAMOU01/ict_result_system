import pandas as pd
import re
from django.db import transaction
from .models import Student, Course, Enrollment, Semester, ImportLog


def parse_upload(file_obj):
    """Parse CSV or Excel file, return DataFrame."""
    name = file_obj.name.lower()
    if name.endswith('.csv'):
        df = pd.read_csv(file_obj)
    elif name.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_obj)
    else:
        raise ValueError("Unsupported file format. Use CSV or Excel.")
    return df


def parse_course_name(course_string):
    """
    Parse course name string with format: SEMESTER-LEVEL-COURSECODE CourseName
    Example: FA25-MSC-ICT7114 IT Strategic Planning and Management
    
    Returns: (semester, level_code, course_code, course_name)
    """
    pattern = r'^([A-Z]{2}\d{2})-([A-Z]+)-([A-Z]+\d+)\s+(.+)$'
    match = re.match(pattern, course_string.strip())
    
    if not match:
        raise ValueError(f"Invalid course format: {course_string}. Expected: SEMESTER-LEVEL-CODE Name")
    
    semester_prefix = match.group(1)  # e.g. FA25
    level_code = match.group(2)       # e.g. MSC
    course_code = match.group(3)      # e.g. ICT7114
    course_name = match.group(4)      # e.g. IT Strategic Planning and Management
    
    return semester_prefix, level_code, course_code, course_name


def map_level_code(level_code):
    """
    Map level code to level name.
    MSC/MA/MBA → master
    BSC/BA/BBA/HND → bachelor
    PHD/DBA → phd
    """
    level_code = level_code.upper()
    
    if level_code in ['MSC', 'MA', 'MBA']:
        return 'master'
    elif level_code in ['PHD', 'DBA']:
        return 'phd'
    elif level_code in ['BSC', 'BA', 'BBA', 'HND']:
        return 'bachelor'
    else:
        return 'bachelor'  # Default to bachelor


def normalize_columns(df):
    """Normalize column names to internal keys."""
    mapping = {}
    for col in df.columns:
        c = col.strip().lower()
        if any(x in c for x in ['admission', 'matric', 'student_id', 'id']):
            mapping[col] = 'matricule'
        elif any(x in c for x in ['first', 'prenom', 'first_name']):
            mapping[col] = 'first_name'
        elif any(x in c for x in ['last', 'nom', 'last_name', 'surname']):
            mapping[col] = 'last_name'
        elif any(x in c for x in ['course_name', 'course name']):
            mapping[col] = 'course_name'
        elif any(x in c for x in ['email', 'mail']):
            mapping[col] = 'email'
    df = df.rename(columns=mapping)
    return df


@transaction.atomic
def import_enrollment_file(file_obj, semester_id, user):
    """
    Import enrollment file with format: Course Name | First Name | Last Name | Admission Number | Email
    Course Name format: SEMESTER-LEVEL-COURSECODE CourseName (e.g. FA25-MSC-ICT7114 IT Strategic Planning)
    
    Returns ImportLog instance.
    """
    errors = []
    students_created = 0
    courses_created = 0
    enrollments_created = 0

    try:
        semester = Semester.objects.get(id=semester_id)
    except Semester.DoesNotExist:
        raise ValueError("Selected semester does not exist.")

    df = parse_upload(file_obj)
    df = normalize_columns(df)

    # Validate required columns
    required = ['matricule', 'first_name', 'last_name', 'course_name']
    missing = [r for r in required if r not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}. Found: {', '.join(df.columns.tolist())}")

    df = df.dropna(subset=['matricule', 'course_name'])

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed + header
        try:
            matricule = str(row['matricule']).strip()
            first_name = str(row['first_name']).strip().title()
            last_name = str(row['last_name']).strip().upper()
            course_full_str = str(row['course_name']).strip()
            email = str(row['email']).strip() if 'email' in df.columns else ''

            # Split course string on first space: code | name
            # Example: "FA25-MSC-ICT7114 IT Strategic Planning and Management"
            # becomes: code="FA25-MSC-ICT7114", name="IT Strategic Planning and Management"
            # French example: "FR-FA25-MSC-ICT7114 IT Strategic Planning and Management"
            # becomes: code="FR-FA25-MSC-ICT7114", name="IT Strategic Planning and Management"
            if ' ' in course_full_str:
                course_code, course_name = course_full_str.split(' ', 1)
            else:
                course_code = course_full_str
                course_name = course_full_str
            
            # Extract level code from course code (handles both FR- and non-FR- prefixed codes)
            # Example: "FA25-MSC-ICT7114" → extract "MSC" at index [1]
            # French example: "FR-FA25-MSC-ICT7114" → extract "MSC" at index [2]
            code_parts = course_code.split('-')
            level_code = None
            if len(code_parts) >= 2:
                # If first part is 'FR', level code is at index 2, else at index 1
                level_idx = 2 if code_parts[0].upper() == 'FR' else 1
                if len(code_parts) > level_idx:
                    level_code = code_parts[level_idx]
            
            level = map_level_code(level_code) if level_code else 'bachelor'

            # Get or create student
            student, s_created = Student.objects.get_or_create(
                matricule=matricule,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'level': level,
                    'email': email
                }
            )
            if s_created:
                students_created += 1

            # Get or create course
            # Store full course code (e.g. FA25-MSC-ICT7114) and full name separately
            course, c_created = Course.objects.get_or_create(
                code=course_code,
                semester=semester,
                defaults={
                    'name': course_name,
                    'level': level
                }
            )
            if c_created:
                courses_created += 1

            # Get or create enrollment
            enrollment, e_created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                semester=semester
            )
            if e_created:
                enrollments_created += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    log = ImportLog.objects.create(
        file_name=file_obj.name,
        semester=semester,
        imported_by=user,
        students_created=students_created,
        courses_created=courses_created,
        enrollments_created=enrollments_created,
        errors='\n'.join(errors) if errors else ''
    )
    return log
