from django.core.management.base import BaseCommand
from academics.models import AdmittedStudent
import re


class Command(BaseCommand):
    help = 'Seed 100 admitted Cameroonian students across different admission years and levels'

    def handle(self, *args, **options):
        # Cameroonian first names and last names
        first_names = [
            'Jean', 'Marie', 'Paul', 'Pierre', 'Philippe', 'Michel', 'Andre', 'Claude', 'Marc', 'Luc',
            'Francois', 'Bernard', 'Daniel', 'Thomas', 'Christian', 'David', 'Guy', 'Joseph', 'Jacques', 'Charles',
            'Sophie', 'Anne', 'Francine', 'Nicole', 'Martine', 'Catherine', 'Danielle', 'Sandrine', 'Sylvie', 'Veronique',
            'Diane', 'Florence', 'Monique', 'Chantal', 'Sylvain', 'Fabienne', 'Christine', 'Pascale', 'Fernande', 'Helene',
        ]

        last_names = [
            'Nkomo', 'Ndongo', 'Ateba', 'Mbarga', 'Epee', 'Tambe', 'Njikam', 'Kembe', 'Kah', 'Ayuk',
            'Sieuve', 'Ako', 'Fohofung', 'Mandoum', 'Tezembapeme', 'Asako', 'Essama', 'Abong', 'Aminkeng', 'Achter',
            'Bayiha', 'Tagne', 'Noumssi', 'Mokoondeke', 'Nzukam', 'Njinah', 'Emah', 'Fongdung', 'Ngum', 'Sevidzem',
            'Tebah', 'Kamga', 'Tekam', 'Kumput', 'Sontah', 'Njiokah', 'Mbohi', 'Moteng', 'Temben', 'Ngong',
            'Sounouvou', 'Zam', 'Fomena', 'Bonabebe', 'Tchonang', 'Tagne', 'Mbuah', 'Ndola', 'Ketcha', 'Fobissi',
            'Kemtche', 'Njeumeni', 'Togalo', 'Kamkum', 'Ebot', 'Araba', 'Kem', 'Nembot', 'Tsaffo', 'Angong',
        ]

        # Term-based academic years in requested format
        admission_data = {
            'Fall 2020': {'count': 12, 'levels': ['bachelor'] * 8 + ['master'] * 3 + ['phd'] * 1},
            'Spring 2021': {'count': 10, 'levels': ['bachelor'] * 7 + ['master'] * 2 + ['phd'] * 1},
            'Summer 2021': {'count': 8, 'levels': ['bachelor'] * 5 + ['master'] * 2 + ['phd'] * 1},
            'Fall 2022': {'count': 14, 'levels': ['bachelor'] * 9 + ['master'] * 4 + ['phd'] * 1},
            'Spring 2023': {'count': 12, 'levels': ['bachelor'] * 8 + ['master'] * 3 + ['phd'] * 1},
            'Summer 2023': {'count': 8, 'levels': ['bachelor'] * 5 + ['master'] * 3},
            'Fall 2024': {'count': 14, 'levels': ['bachelor'] * 9 + ['master'] * 4 + ['phd'] * 1},
            'Spring 2025': {'count': 12, 'levels': ['bachelor'] * 8 + ['master'] * 3 + ['phd'] * 1},
            'Summer 2025': {'count': 5, 'levels': ['bachelor'] * 3 + ['master'] * 2},
            'Fall 2026': {'count': 5, 'levels': ['bachelor'] * 3 + ['master'] * 2},
        }

        students_to_create = []
        matricule_counter = 2020001

        AdmittedStudent.objects.all().delete()

        for term_year, data in admission_data.items():
            for i in range(data['count']):
                first_name = first_names[(i + len(term_year)) % len(first_names)]
                last_name = last_names[(i * 2 + len(term_year) * 3) % len(last_names)]
                level = data['levels'][i]
                matricule = f"{matricule_counter}"
                clean_first = re.sub(r'[^a-z0-9]', '', first_name.lower())
                clean_last = re.sub(r'[^a-z0-9]', '', last_name.lower())
                email = f"{clean_first}.{clean_last}.{matricule}@ictuniversity.cm"
                matricule_counter += 1

                students_to_create.append(
                    AdmittedStudent(
                        matricule=matricule,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        level=level,
                        admitted_year=term_year,
                    )
                )

        # Bulk create all students
        AdmittedStudent.objects.bulk_create(students_to_create, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(students_to_create)} admitted students')
        )
