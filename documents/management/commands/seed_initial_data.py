"""
Management command: seed_initial_data

Populates the database with the initial Department and DocumentType records
required for the Add Document form to work.

Safe to run multiple times — uses get_or_create so existing records are
never duplicated or modified.
"""

from django.core.management.base import BaseCommand

from documents.models import Department, DocumentType

DEPARTMENTS = [
    "Human Resources",
    "Finance",
    "Information Technology",
    "Administration",
    "Legal",
]

DOCUMENT_TYPES = [
    "Contract",
    "Invoice",
    "Report",
    "Letter",
    "Policy",
    "Other",
]


class Command(BaseCommand):
    help = (
        "Seed initial Department and DocumentType records. "
        "Safe to run multiple times — existing records are never modified."
    )

    def handle(self, *args, **options):
        self._seed(Department, DEPARTMENTS, "Department")
        self._seed(DocumentType, DOCUMENT_TYPES, "DocumentType")

    def _seed(self, model, names, label):
        created_count = 0
        for name in names:
            _, created = model.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(f"  Created {label}: {name}")
            else:
                self.stdout.write(f"  Skipped {label} (already exists): {name}")
        self.stdout.write(
            self.style.SUCCESS(
                f"{label}: {created_count} created, "
                f"{len(names) - created_count} already existed."
            )
        )
