from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Membuat akun admin Sani Laundry untuk Admin Center."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Username admin, contoh: admin")
        parser.add_argument("--name", default="", help="Nama admin")

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"].strip()
        if User.objects.filter(username=username).exists():
            raise CommandError(f"Username '{username}' sudah digunakan.")

        while True:
            password = getpass("Password: ")
            password2 = getpass("Ulangi password: ")
            if password != password2:
                self.stderr.write(self.style.ERROR("Password tidak sama. Coba lagi."))
                continue
            try:
                validate_password(password)
            except ValidationError as exc:
                for message in exc.messages:
                    self.stderr.write(self.style.ERROR(message))
                continue
            break

        name = options["name"].strip()
        first_name, _, last_name = name.partition(" ")
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Akun admin '{user.username}' berhasil dibuat."))
