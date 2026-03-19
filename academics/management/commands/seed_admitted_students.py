from django.core.management.base import BaseCommand
from academics.models import AdmittedStudent


class Command(BaseCommand):
    help = 'Seed admitted students with hardcoded ICTU data provided by registrar/admin'

    def _normalize_matricule(self, matricule):
        raw = str(matricule).strip().upper()
        if raw.startswith('ICTU'):
            return raw
        return f'ICTU{raw}'

    def _normalize_level(self, level):
        value = str(level).strip().lower()
        if value == 'master':
            return 'master'
        if value == 'phd':
            return 'phd'
        return 'bachelor'

    def handle(self, *args, **options):
        # Hardcoded admitted students shared by the user
        rows = [
            ('2020090', 'Francine', 'Araba', 'francine.araba.2020090@ictuniversity.cm', 'PhD', 'Spring 2025'),
            ('2020084', 'Guy', 'Bonabebe', 'guy.bonabebe.2020084@ictuniversity.cm', 'Bachelor', 'Spring 2025'),
            ('2020087', 'Charles', 'Fobissi', 'charles.fobissi.2020087@ictuniversity.cm', 'Master', 'Spring 2025'),
            ('2020089', 'Anne', 'Kamkum', 'anne.kamkum.2020089@ictuniversity.cm', 'Master', 'Spring 2025'),
            ('2020079', 'Bernard', 'Kumput', 'bernard.kumput.2020079@ictuniversity.cm', 'Bachelor', 'Spring 2025'),
            ('2020081', 'Thomas', 'Moteng', 'thomas.moteng.2020081@ictuniversity.cm', 'Bachelor', 'Spring 2025'),
            ('2020086', 'Jacques', 'Ndola', 'jacques.ndola.2020086@ictuniversity.cm', 'Bachelor', 'Spring 2025'),
            ('2020082', 'Christian', 'Ngong', 'christian.ngong.2020082@ictuniversity.cm', 'Bachelor', 'Spring 2025'),
            ('2020088', 'Sophie', 'Njeumeni', 'sophie.njeumeni.2020088@ictuniversity.cm', 'Master', 'Spring 2025'),
            ('2020080', 'Daniel', 'Njiokah', 'daniel.njiokah.2020080@ictuniversity.cm', 'Bachelor', 'Spring 2025'),
            ('2020085', 'Joseph', 'Tagne', 'joseph.tagne.2020085@ictuniversity.cm', 'Bachelor', 'Spring 2025'),
            ('2020083', 'David', 'Zam', 'david.zam.2020083@ictuniversity.cm', 'Bachelor', 'Spring 2025'),
            ('2020028', 'Guy', 'Bonabebe', 'guy.bonabebe.2020028@ictuniversity.cm', 'Master', 'Summer 2021'),
            ('2020023', 'Bernard', 'Kumput', 'bernard.kumput.2020023@ictuniversity.cm', 'Bachelor', 'Summer 2021'),
            ('2020025', 'Thomas', 'Moteng', 'thomas.moteng.2020025@ictuniversity.cm', 'Bachelor', 'Summer 2021'),
            ('2020030', 'Jacques', 'Ndola', 'jacques.ndola.2020030@ictuniversity.cm', 'PhD', 'Summer 2021'),
            ('2020026', 'Christian', 'Ngong', 'christian.ngong.2020026@ictuniversity.cm', 'Bachelor', 'Summer 2021'),
            ('2020024', 'Daniel', 'Njiokah', 'daniel.njiokah.2020024@ictuniversity.cm', 'Bachelor', 'Summer 2021'),
            ('2020029', 'Joseph', 'Tagne', 'joseph.tagne.2020029@ictuniversity.cm', 'Master', 'Summer 2021'),
            ('2020027', 'David', 'Zam', 'david.zam.2020027@ictuniversity.cm', 'Bachelor', 'Summer 2021'),
            ('2020062', 'Guy', 'Bonabebe', 'guy.bonabebe.2020062@ictuniversity.cm', 'Master', 'Summer 2023'),
            ('2020057', 'Bernard', 'Kumput', 'bernard.kumput.2020057@ictuniversity.cm', 'Bachelor', 'Summer 2023'),
            ('2020059', 'Thomas', 'Moteng', 'thomas.moteng.2020059@ictuniversity.cm', 'Bachelor', 'Summer 2023'),
            ('2020064', 'Jacques', 'Ndola', 'jacques.ndola.2020064@ictuniversity.cm', 'Master', 'Summer 2023'),
            ('2020060', 'Christian', 'Ngong', 'christian.ngong.2020060@ictuniversity.cm', 'Bachelor', 'Summer 2023'),
            ('2020058', 'Daniel', 'Njiokah', 'daniel.njiokah.2020058@ictuniversity.cm', 'Bachelor', 'Summer 2023'),
            ('2020063', 'Joseph', 'Tagne', 'joseph.tagne.2020063@ictuniversity.cm', 'Master', 'Summer 2023'),
            ('2020061', 'David', 'Zam', 'david.zam.2020061@ictuniversity.cm', 'Bachelor', 'Summer 2023'),
            ('2020091', 'Bernard', 'Kumput', 'bernard.kumput.2020091@ictuniversity.cm', 'Bachelor', 'Summer 2025'),
            ('2020093', 'Thomas', 'Moteng', 'thomas.moteng.2020093@ictuniversity.cm', 'Bachelor', 'Summer 2025'),
            ('2020094', 'Christian', 'Ngong', 'christian.ngong.2020094@ictuniversity.cm', 'Master', 'Summer 2025'),
            ('2020092', 'Daniel', 'Njiokah', 'daniel.njiokah.2020092@ictuniversity.cm', 'Bachelor', 'Summer 2025'),
            ('2020095', 'David', 'Zam', 'david.zam.2020095@ictuniversity.cm', 'Master', 'Summer 2025'),
        ]

        AdmittedStudent.objects.all().delete()

        students_to_create = []
        for matricule, first_name, last_name, email, level, admitted_year in rows:
            students_to_create.append(
                AdmittedStudent(
                    matricule=self._normalize_matricule(matricule),
                    first_name=str(first_name).strip().title(),
                    last_name=str(last_name).strip().title(),
                    email=str(email).strip().lower(),
                    level=self._normalize_level(level),
                    admitted_year=str(admitted_year).strip(),
                )
            )

        AdmittedStudent.objects.bulk_create(students_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(students_to_create)} admitted students'))
