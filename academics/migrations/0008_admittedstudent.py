# Generated migration for AdmittedStudent model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0007_student_is_walkin'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdmittedStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricule', models.CharField(max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('level', models.CharField(choices=[('bachelor', 'Bachelor'), ('master', 'Master'), ('phd', 'PhD')], default='bachelor', max_length=20)),
                ('admitted_year', models.IntegerField(choices=[(2020, '2020'), (2021, '2021'), (2022, '2022'), (2023, '2023'), (2024, '2024'), (2025, '2025'), (2026, '2026')], default=2026)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-admitted_year', 'last_name', 'first_name'],
            },
        ),
        migrations.AddIndex(
            model_name='admittedstudent',
            index=models.Index(fields=['matricule'], name='academics_a_matricu_idx'),
        ),
        migrations.AddIndex(
            model_name='admittedstudent',
            index=models.Index(fields=['admitted_year'], name='academics_a_admitte_idx'),
        ),
    ]
