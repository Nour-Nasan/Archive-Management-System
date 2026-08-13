"""
Audit-trail helpers for the documents module.
Import log_action wherever a loggable event occurs in views.
"""
from .models import DocumentLog


def log_action(document, user, action, details=''):
    """Create a DocumentLog entry. Safe to call even if user is None."""
    DocumentLog.objects.create(
        document=document,
        document_number=document.document_number,
        document_title=document.title,
        user=user,
        action=action,
        details=details,
    )


def _label(val, choices):
    """Return the human-readable label for a choices value."""
    return dict(choices).get(val, val)


def diff_document(old, new_form_data, document):
    """
    Compare a Document instance *before* save with the cleaned form data
    *after* save.  Returns (changes_list, status_changed).

    old              – dict snapshot of the document before form.save()
    new_form_data    – form.cleaned_data  (or the refreshed instance fields)
    document         – the saved Document instance (for FK labels)
    """
    from .models import Document

    watched = [
        ('title',           'Title'),
        ('document_number', 'Document Number'),
        ('description',     'Description'),
        ('document_date',   'Document Date'),
        ('status',          'Status'),
    ]
    fk_watched = [
        ('document_type_id', 'document_type', 'Document Type'),
        ('department_id',    'department',    'Department'),
    ]

    changes = []
    status_changed = False

    for field, label in watched:
        old_val = old.get(field, '')
        new_val = new_form_data.get(field, '')
        if str(old_val) != str(new_val):
            if field == 'status':
                status_changed = True
                old_label = _label(old_val, Document.STATUS_CHOICES)
                new_label = _label(new_val, Document.STATUS_CHOICES)
                changes.append(f'Status: "{old_label}" → "{new_label}"')
            else:
                changes.append(f'{label}: "{old_val}" → "{new_val}"')

    for id_field, obj_field, label in fk_watched:
        old_id = old.get(id_field)
        new_obj = new_form_data.get(obj_field)
        new_id = new_obj.pk if new_obj else None
        if old_id != new_id:
            old_name = old.get(f'__{obj_field}_name', '—')
            new_name = str(new_obj) if new_obj else '—'
            changes.append(f'{label}: "{old_name}" → "{new_name}"')

    return changes, status_changed
