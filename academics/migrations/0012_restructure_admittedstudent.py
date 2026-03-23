# Migration to restructure AdmittedStudent model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0011_rename_academics_a_matricu_idx_academics_a_matricu_d5c67a_idx_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name='AdmittedStudent',
        ),
        migrations.CreateModel(
            name='AdmittedStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricule', models.CharField(max_length=50)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('program', models.CharField(blank=True, max_length=100, null=True)),
                ('level', models.CharField(blank=True, choices=[('bachelor', 'Bachelor'), ('master', 'Master'), ('phd', 'PhD')], max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admitted_students', to='academics.semester')),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.AddConstraint(
            model_name='admittedstudent',
            constraint=models.UniqueConstraint(fields=['semester', 'matricule'], name='unique_semester_matricule'),
        ),
        migrations.AddIndex(
            model_name='admittedstudent',
            index=models.Index(fields=['matricule'], name='academics_a_matricu_idx'),
        ),
    ]
