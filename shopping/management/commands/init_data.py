import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from shopping.models import Category, Product


class Command(BaseCommand):
    help = "Initializes default seed data and creates admin superuser if configured."

    def handle(self, *args, **options):
        # 1. Seed Categories & Products if database is empty
        if Category.objects.count() == 0 and Product.objects.count() == 0:
            self.stdout.write("Loading initial store categories and products...")
            try:
                call_command("loaddata", "shopping/fixtures/initial_data.json")
                self.stdout.write(self.style.SUCCESS("Successfully loaded initial store data."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not load fixture: {e}"))
        else:
            self.stdout.write("Database already contains product/category data. Skipping fixture load.")

        # 2. Create superuser if environment variables are set
        admin_username = os.environ.get("ADMIN_USERNAME", "").strip()
        admin_password = os.environ.get("ADMIN_PASSWORD", "").strip()
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com").strip()

        if admin_username and admin_password:
            if not User.objects.filter(username=admin_username).exists():
                self.stdout.write(f"Creating superuser '{admin_username}'...")
                User.objects.create_superuser(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password
                )
                self.stdout.write(self.style.SUCCESS(f"Superuser '{admin_username}' created successfully."))
            else:
                self.stdout.write(f"Superuser '{admin_username}' already exists.")
        else:
            self.stdout.write("No ADMIN_USERNAME/ADMIN_PASSWORD provided in env. Skipping superuser creation.")
