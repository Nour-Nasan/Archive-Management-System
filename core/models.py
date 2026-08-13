from django.conf import settings
from django.db import models


class GeneralSettings(models.Model):
    organization_name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    max_file_size_mb = models.PositiveIntegerField(default=10)
    allowed_file_types = models.CharField(
        max_length=255,
        default='pdf,doc,docx,jpg,jpeg,png'
    )

    backup_enabled = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'General Settings'
        verbose_name_plural = 'General Settings'

    def __str__(self):
        return self.organization_name


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('download', 'Download'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    object_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else 'System'
        return f"{username} - {self.action} - {self.created_at}"