"""
Management command to create a superuser from environment variables.
Designed for Render free-tier deployments where Shell access is unavailable.
Safely skips if the user already exists.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create a superuser from DJANGO_SUPERUSER_* env vars (idempotent — safe to run on every deploy)."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "[SKIP] DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD "
                "env vars not set -- skipping superuser creation."
            ))
            return

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            # Ensure the existing user is always superuser + staff
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f"[OK] User '{username}' already exists -- promoted to superuser."
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"[OK] Superuser '{username}' already exists -- no changes needed."
                ))
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(
                f"[OK] Superuser '{username}' created successfully!"
            ))
