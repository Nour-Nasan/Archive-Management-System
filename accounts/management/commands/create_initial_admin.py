"""
Management command: create_initial_admin

Creates the initial production System Administrator from environment variables.
Safe to run multiple times — exits cleanly if the username already exists.

Required environment variables:
    INITIAL_ADMIN_USERNAME  — the login username
    INITIAL_ADMIN_EMAIL     — the email address
    INITIAL_ADMIN_PASSWORD  — the password

The created user is:
    - is_staff=True, is_superuser=True
    - approval_status='approved'
    - role=Manager (the top-level role in this project)
"""

import os

from django.core.management.base import BaseCommand, CommandError

from accounts.models import Role, User


class Command(BaseCommand):
    help = (
        "Create the initial System Administrator from environment variables. "
        "No-ops safely if the username already exists."
    )

    def handle(self, *args, **options):
        # ── Read and validate environment variables ──────────────────────
        username = os.getenv("INITIAL_ADMIN_USERNAME", "").strip()
        email = os.getenv("INITIAL_ADMIN_EMAIL", "").strip()
        password = os.getenv("INITIAL_ADMIN_PASSWORD", "").strip()

        missing = [
            name
            for name, val in [
                ("INITIAL_ADMIN_USERNAME", username),
                ("INITIAL_ADMIN_EMAIL", email),
                ("INITIAL_ADMIN_PASSWORD", password),
            ]
            if not val
        ]
        if missing:
            raise CommandError(
                f"The following required environment variable(s) are not set or empty: "
                f"{', '.join(missing)}"
            )

        # ── Skip if user already exists ──────────────────────────────────
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"User '{username}' already exists — skipping creation."
                )
            )
            return

        # ── Resolve the Manager role ─────────────────────────────────────
        # 'Manager' is the top-level role in this project (has all permission
        # flags). A superuser assigned this role is the System Administrator.
        try:
            manager_role = Role.objects.get(name="Manager")
        except Role.DoesNotExist:
            raise CommandError(
                "Role 'Manager' does not exist in the database. "
                "Make sure migrations have been applied (python manage.py migrate) "
                "and the Role data is present before running this command."
            )

        # ── Create the user ──────────────────────────────────────────────
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        user.role = manager_role
        user.approval_status = User.APPROVAL_APPROVED
        user.save(update_fields=["role", "approval_status"])

        self.stdout.write(
            self.style.SUCCESS(
                f"System Administrator '{username}' created successfully "
                f"with role '{manager_role.name}'."
            )
        )
