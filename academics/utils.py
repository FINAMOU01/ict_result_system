import pandas as pd
import re
from collections import defaultdict
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


def _validated_dataframe(file_obj):
    """Parse and validate the uploaded file columns."""
    df = parse_upload(file_obj)
    df = normalize_columns(df)

    required = ['matricule', 'first_name', 'last_name', 'course_name']
    missing = [r for r in required if r not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}. Found: {', '.join(df.columns.tolist())}")

    df = df.dropna(subset=['matricule', 'course_name'])
    return df


def _extract_row_record(row, row_num, has_email):
    """Normalize a dataframe row into a structured import record."""
    matricule = str(row['matricule']).strip()
    first_name = str(row['first_name']).strip().title()
    last_name = str(row['last_name']).strip().upper()
    course_full_str = str(row['course_name']).strip()
    email = str(row['email']).strip() if has_email else ''

    if ' ' in course_full_str:
        course_code, course_name = course_full_str.split(' ', 1)
    else:
        course_code = course_full_str
        course_name = course_full_str

    code_parts = course_code.split('-')
    level_code = None
    if len(code_parts) >= 2:
        level_idx = 2 if code_parts[0].upper() == 'FR' else 1
        if len(code_parts) > level_idx:
            level_code = code_parts[level_idx]

    level = map_level_code(level_code) if level_code else 'bachelor'

    return {
        'row_num': int(row_num),
        'matricule': matricule,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'course_code': course_code,
        'course_name': course_name,
        'level': level,
    }


def build_import_preview(file_obj):
    """Build preview data without writing to database."""
    df = _validated_dataframe(file_obj)
    has_email = 'email' in df.columns

    records = []
    errors = []
    course_summary = defaultdict(lambda: {'students': set(), 'count': 0, 'level': 'bachelor'})
    course_details = defaultdict(lambda: {'level': 'bachelor', 'rows': []})

    for idx, row in df.iterrows():
        row_num = int(idx) + 2
        try:
            record = _extract_row_record(row, row_num, has_email)
            records.append(record)

            key = (record['course_code'], record['course_name'])
            course_summary[key]['count'] += 1
            course_summary[key]['students'].add(record['matricule'])
            course_summary[key]['level'] = record['level']
            course_details[key]['level'] = record['level']
            if len(course_details[key]['rows']) < 120:
                course_details[key]['rows'].append({
                    'row_num': record['row_num'],
                    'matricule': record['matricule'],
                    'first_name': record['first_name'],
                    'last_name': record['last_name'],
                    'email': record['email'],
                })
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    summary_rows = []
    for (course_code, course_name), info in course_summary.items():
        summary_rows.append({
            'course_code': course_code,
            'course_name': course_name,
            'level': info['level'],
            'row_count': info['count'],
            'student_count': len(info['students']),
        })

    summary_rows.sort(key=lambda x: (x['course_code'], x['course_name']))

    detail_rows = []
    for (course_code, course_name), info in course_details.items():
        total_rows = course_summary[(course_code, course_name)]['count']
        total_students = len(course_summary[(course_code, course_name)]['students'])
        detail_rows.append({
            'course_code': course_code,
            'course_name': course_name,
            'level': info['level'],
            'total_rows': total_rows,
            'student_count': total_students,
            'rows': info['rows'],
            'rows_shown': len(info['rows']),
            'has_more': total_rows > len(info['rows']),
        })
    detail_rows.sort(key=lambda x: (x['course_code'], x['course_name']))

    return {
        'file_name': file_obj.name,
        'records': records,
        'preview_rows': records[:200],
        'course_summary': summary_rows,
        'course_details': detail_rows,
        'total_rows': len(records),
        'total_courses': len(summary_rows),
        'errors': errors,
    }


@transaction.atomic
def import_enrollment_records(records, semester_id, user, file_name):
    """Persist validated preview records into the database."""
    try:
        semester = Semester.objects.get(id=semester_id)
    except Semester.DoesNotExist:
        raise ValueError("Selected semester does not exist.")

    errors = []
    students_created = 0
    courses_created = 0
    enrollments_created = 0

    for record in records:
        try:
            student, s_created = Student.objects.get_or_create(
                matricule=record['matricule'],
                defaults={
                    'first_name': record['first_name'],
                    'last_name': record['last_name'],
                    'level': record['level'],
                    'email': record['email'],
                }
            )
            if s_created:
                students_created += 1

            course, c_created = Course.objects.get_or_create(
                code=record['course_code'],
                semester=semester,
                defaults={
                    'name': record['course_name'],
                    'level': record['level'],
                }
            )
            if c_created:
                courses_created += 1

            _, e_created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                semester=semester,
            )
            if e_created:
                enrollments_created += 1
        except Exception as e:
            errors.append(f"Row {record.get('row_num', '?')}: {str(e)}")

    log = ImportLog.objects.create(
        file_name=file_name,
        semester=semester,
        imported_by=user,
        students_created=students_created,
        courses_created=courses_created,
        enrollments_created=enrollments_created,
        errors='\n'.join(errors) if errors else '',
    )
    return log


@transaction.atomic
def import_enrollment_file(file_obj, semester_id, user):
    """
    Import enrollment file with format: Course Name | First Name | Last Name | Admission Number | Email
    Course Name format: SEMESTER-LEVEL-COURSECODE CourseName (e.g. FA25-MSC-ICT7114 IT Strategic Planning)
    
    Returns ImportLog instance.
    """
    preview = build_import_preview(file_obj)
    return import_enrollment_records(
        preview['records'],
        semester_id,
        user,
        preview['file_name'],
    )


# ============ STATISTICS & REPORTING ============

def get_grade(score):
    """Returns (grade_letter, gpa, is_pass) for a given score out of 100."""
    if score is None:
        return None, None, None
    score = float(score)
    if score >= 80:   return 'A',  4.0, True
    if score >= 70:   return 'B+', 3.5, True
    if score >= 60:   return 'B',  3.0, True
    if score >= 55:   return 'C+', 2.5, True
    if score >= 50:   return 'C',  2.0, True
    if score >= 45:   return 'D+', 1.5, False
    if score >= 40:   return 'D',  1.0, False
    return 'F', 0.0, False


def get_course_statistics(course):
    """
    Returns a dict of statistics for a single course.
    Only counts enrollments where final_score is not None.
    """
    enrollments = course.enrollments.select_related('grade')

    total = enrollments.count()
    graded = [e for e in enrollments if hasattr(e, 'grade') and e.grade.final_score is not None]
    graded_count = len(graded)

    grade_counts = {'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D+': 0, 'D': 0, 'F': 0}
    pass_count = 0
    fail_count = 0
    total_gpa = 0

    for enrollment in graded:
        score = float(enrollment.grade.final_score)
        letter, gpa, is_pass = get_grade(score)
        grade_counts[letter] += 1
        total_gpa += gpa
        if is_pass:
            pass_count += 1
        else:
            fail_count += 1

    def pct(n):
        return round((n / graded_count * 100), 1) if graded_count > 0 else 0

    return {
        'course': course,
        'total_enrolled': total,
        'total_graded': graded_count,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'pass_pct': pct(pass_count),
        'fail_pct': pct(fail_count),
        'average_gpa': round(total_gpa / graded_count, 2) if graded_count > 0 else 0,
        'grade_counts': grade_counts,
        'grade_pcts': {g: pct(c) for g, c in grade_counts.items()},
    }


def get_semester_statistics(semester):
    """
    Returns aggregated statistics for all decoded courses in a semester.
    """
    courses = semester.courses.filter(is_decoded=True)
    course_stats = [get_course_statistics(c) for c in courses]

    total_graded = sum(s['total_graded'] for s in course_stats)
    pass_count   = sum(s['pass_count']   for s in course_stats)
    fail_count   = sum(s['fail_count']   for s in course_stats)
    grade_counts = {'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D+': 0, 'D': 0, 'F': 0}
    for s in course_stats:
        for g in grade_counts:
            grade_counts[g] += s['grade_counts'][g]

    def pct(n):
        return round((n / total_graded * 100), 1) if total_graded > 0 else 0

    best_course  = max(course_stats, key=lambda s: s['pass_pct'],  default=None)
    worst_course = min(course_stats, key=lambda s: s['pass_pct'],  default=None)

    return {
        'semester': semester,
        'total_courses': len(course_stats),
        'total_graded': total_graded,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'pass_pct': pct(pass_count),
        'fail_pct': pct(fail_count),
        'grade_counts': grade_counts,
        'grade_pcts': {g: pct(c) for g, c in grade_counts.items()},
        'best_course': best_course,
        'worst_course': worst_course,
        'course_stats': course_stats,
    }
