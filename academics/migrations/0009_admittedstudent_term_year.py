from django.db import migrations, models


def forward_convert_admitted_year(apps, schema_editor):
    AdmittedStudent = apps.get_model('academics', 'AdmittedStudent')
    for student in AdmittedStudent.objects.all().only('id', 'admitted_year'):
        raw = str(student.admitted_year)
        year = ''.join(ch for ch in raw if ch.isdigit())[:4]
        if len(year) != 4:
            year = '2026'
        student.admitted_year = f'Fall {year}'
        student.save(update_fields=['admitted_year'])


def reverse_convert_admitted_year(apps, schema_editor):
    AdmittedStudent = apps.get_model('academics', 'AdmittedStudent')
    for student in AdmittedStudent.objects.all().only('id', 'admitted_year'):
        raw = str(student.admitted_year)
        year = ''.join(ch for ch in raw if ch.isdigit())[:4]
        if len(year) != 4:
            year = '2026'
        student.admitted_year = year
        student.save(update_fields=['admitted_year'])


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0008_admittedstudent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admittedstudent',
            name='admitted_year',
            field=models.CharField(
                choices=[
                    ('Fall 2020', 'Fall 2020'),
                    ('Spring 2020', 'Spring 2020'),
                    ('Summer 2020', 'Summer 2020'),
                    ('Fall 2021', 'Fall 2021'),
                    ('Spring 2021', 'Spring 2021'),
                    ('Summer 2021', 'Summer 2021'),
                    ('Fall 2022', 'Fall 2022'),
                    ('Spring 2022', 'Spring 2022'),
                    ('Summer 2022', 'Summer 2022'),
                    ('Fall 2023', 'Fall 2023'),
                    ('Spring 2023', 'Spring 2023'),
                    ('Summer 2023', 'Summer 2023'),
                    ('Fall 2024', 'Fall 2024'),
                    ('Spring 2024', 'Spring 2024'),
                    ('Summer 2024', 'Summer 2024'),
                    ('Fall 2025', 'Fall 2025'),
                    ('Spring 2025', 'Spring 2025'),
                    ('Summer 2025', 'Summer 2025'),
                    ('Fall 2026', 'Fall 2026'),
                    ('Spring 2026', 'Spring 2026'),
                    ('Summer 2026', 'Summer 2026'),
                ],
                default='Fall 2026',
                max_length=20,
            ),
        ),
        migrations.RunPython(forward_convert_admitted_year, reverse_convert_admitted_year),
    ]
