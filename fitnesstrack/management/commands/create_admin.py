from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser for the fitness tracker application'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Username for the superuser')
        parser.add_argument('--email', type=str, default='admin@fitness.com', help='Email for the superuser')
        parser.add_argument('--password', type=str, default='admin123', help='Password for the superuser')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists!'))
            return

        # Create the superuser
        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS(f'Successfully created superuser:'))
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Email: {email}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(self.style.WARNING('⚠️  Change this password in production!'))
