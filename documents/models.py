from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class DocumentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    document_number = models.CharField(max_length=100, unique=True)
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    document_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_documents'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.document_number} - {self.title}"


class DocumentFile(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='documents/')
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_files'
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.original_name} - v{self.version}"


class DocumentLog(models.Model):
    """Audit trail for all document activity."""

    ACTION_CREATED = 'created'
    ACTION_EDITED = 'edited'
    ACTION_STATUS_CHANGED = 'status_changed'
    ACTION_FILE_UPLOADED = 'file_uploaded'
    ACTION_DELETED = 'deleted'

    ACTION_CHOICES = [
        (ACTION_CREATED, 'Created'),
        (ACTION_EDITED, 'Edited'),
        (ACTION_STATUS_CHANGED, 'Status Changed'),
        (ACTION_FILE_UPLOADED, 'File Uploaded'),
        (ACTION_DELETED, 'Deleted'),
    ]

    # SET_NULL so log entries survive document deletion
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
    )
    # Snapshot fields — preserved even after the document is deleted
    document_number = models.CharField(max_length=100, blank=True)
    document_title = models.CharField(max_length=255, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_logs',
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.get_action_display()}] {self.document_number} by {self.user} at {self.timestamp:%Y-%m-%d %H:%M}"

    # ── Convenience colours for templates ────────────────────────────────
    @property
    def badge_class(self):
        return {
            self.ACTION_CREATED: 'bg-success',
            self.ACTION_EDITED: 'bg-primary',
            self.ACTION_STATUS_CHANGED: 'bg-warning text-dark',
            self.ACTION_FILE_UPLOADED: 'bg-info text-dark',
            self.ACTION_DELETED: 'bg-danger',
        }.get(self.action, 'bg-secondary')
