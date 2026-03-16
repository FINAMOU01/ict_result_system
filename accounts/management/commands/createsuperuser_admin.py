from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create the initial system admin user'

    def handle(self, *args, **kwargs):
        if CustomUser.objects.filter(role='admin').exists():
            self.stdout.write(self.style.WARNING('An admin user already exists.'))
            return
        username = input("Admin username [admin]: ").strip() or 'admin'
        email = input("Admin email: ").strip()
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        import getpass
        password = getpass.getpass("Password: ")
        user = CustomUser.objects.create_superuser(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name, role='admin'
        )
        self.stdout.write(self.style.SUCCESS(f'Admin "{username}" created successfully.'))
