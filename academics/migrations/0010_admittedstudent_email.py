from django.db import migrations, models
import re


def forward_populate_email(apps, schema_editor):
    AdmittedStudent = apps.get_model('academics', 'AdmittedStudent')
    for student in AdmittedStudent.objects.all().only('id', 'first_name', 'last_name', 'matricule'):
        clean_first = re.sub(r'[^a-z0-9]', '', (student.first_name or '').lower()) or 'student'
        clean_last = re.sub(r'[^a-z0-9]', '', (student.last_name or '').lower()) or 'admitted'
        matricule = str(student.matricule)
        student.email = f"{clean_first}.{clean_last}.{matricule}@ictuniversity.cm"
        student.save(update_fields=['email'])


def reverse_clear_email(apps, schema_editor):
    AdmittedStudent = apps.get_model('academics', 'AdmittedStudent')
    AdmittedStudent.objects.all().update(email=None)


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0009_admittedstudent_term_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='admittedstudent',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.RunPython(forward_populate_email, reverse_clear_email),
        migrations.AlterField(
            model_name='admittedstudent',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
