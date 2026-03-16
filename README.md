# ICT University — Results Management System

A Django fullstack application for managing student examination results with anonymous coding/decoding.

## Stack
- **Backend**: Django 4.2 + PostgreSQL
- **Frontend**: Django Templates + Bootstrap 5
- **Export**: OpenPyXL (Excel files)
- **Import**: Pandas (CSV + Excel parsing)

## Setup

```bash
# 1. Clone and install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your DB credentials

# 3. Create PostgreSQL database
createdb ict_results_db

# 4. Run migrations
python manage.py migrate

# 5. Create superadmin
python manage.py createsuperuser_admin

# 6. Run server
python manage.py runserver
```

## User Roles

| Role | Access |
|------|--------|
| **Admin** | Import CSV, manage semesters, create users, assign professors |
| **Registra** | Code/decode student lists, download sheets, lookup codes |
| **Professor** | View anonymous codes, enter CC+SN grades, submit to registra |

## Workflow

```
Admin imports CSV → Students/Courses/Enrollments created automatically
Admin assigns professors to courses
Registra clicks "Code" → Anonymous codes (1,2,3...) assigned
Registra downloads Confidential Coding Sheet (matricule ↔ code)
Professor logs in → sees only anonymous codes → enters CC + SN → submits
Registra receives grades → decodes → downloads final Excel results
```

## CSV Format

Required columns (names auto-detected):
- `Matricule` or `student_id`
- `Nom & Prénom` or `full_name`
- `Course Code` or `code_mat`
- `Course Name` or `matiere`
- `Semester` or `semestre` (optional)
- `Level` or `niveau` (optional: bachelor/master/phd)
