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

If the Manager role does not yet exist (e.g. a fresh production database),
it is created with the exact permission flags used in this project. An already-
existing Manager role is never modified.
"""

import os

from django.core.management.base import BaseCommand, CommandError

from accounts.models import Role, User

# Exact Manager role permission values as configured in this project.
# Sourced from the live role data (can_delete_documents is False per
# migration 0003 which explicitly sets it to False for Manager).
_MANAGER_PERMISSION_DEFAULTS = {
    "can_view_documents":   True,
    "can_add_documents":    True,
    "can_edit_documents":   True,
    "can_delete_documents": False,
    "can_manage_users":     True,
    "can_view_reports":     True,
    "can_manage_settings":  True,
}


class Command(BaseCommand):
    help = (
        "Create the initial System Administrator from environment variables. "
        "No-ops safely if the username already exists."
    )

    def handle(self, *args, **options):
        # ── Read and validate environment variables ──────────────────────
        username = os.getenv("INITIAL_ADMIN_USERNAME", "").strip()
        email    = os.getenv("INITIAL_ADMIN_EMAIL",    "").strip()
        password = os.getenv("INITIAL_ADMIN_PASSWORD", "").strip()

        missing = [
            name
            for name, val in [
                ("INITIAL_ADMIN_USERNAME", username),
                ("INITIAL_ADMIN_EMAIL",    email),
                ("INITIAL_ADMIN_PASSWORD", password),
            ]
            if not val
        ]
        if missing:
            raise CommandError(
                "The following required environment variable(s) are not set or "
                f"empty: {', '.join(missing)}"
            )

        # ── Skip if user already exists ──────────────────────────────────
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"User '{username}' already exists — skipping creation."
                )
            )
            return

        # ── Ensure the Manager role exists ───────────────────────────────
        # get_or_create only applies the defaults when the row is absent,
        # so an existing Manager role's permissions are never overwritten.
        manager_role, created = Role.objects.get_or_create(
            name="Manager",
            defaults=_MANAGER_PERMISSION_DEFAULTS,
        )
        if created:
            self.stdout.write(
                self.style.WARNING(
                    "Role 'Manager' did not exist and was created with default "
                    "project permissions."
                )
            )

        # ── Create the superuser ─────────────────────────────────────────
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
