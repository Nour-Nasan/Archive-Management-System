"""
Data migration: align Role permission flags with the enforced permission model.
  Manager  → can_delete_documents=False  (delete is superuser-only)
  Employee → can_add_documents=False     (employees are read-only)
"""
from django.db import migrations


def fix_role_permissions(apps, schema_editor):
    Role = apps.get_model('accounts', 'Role')
    Role.objects.filter(name='Manager').update(can_delete_documents=False)
    Role.objects.filter(name='Employee').update(can_add_documents=False)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_approval_status'),
    ]

    operations = [
        migrations.RunPython(fix_role_permissions, migrations.RunPython.noop),
    ]
