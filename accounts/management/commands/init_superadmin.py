from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import User


class Command(BaseCommand):
    help = 'Initialize Super Admin user'

    def handle(self, *args, **options):
        email = settings.SUPER_ADMIN_EMAIL
        password = settings.SUPER_ADMIN_PASSWORD
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Super Admin {email} already exists'))
            return
        
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name='Super',
            last_name='Admin'
        )
        
        self.stdout.write(self.style.SUCCESS(f'Super Admin created successfully: {email}'))
