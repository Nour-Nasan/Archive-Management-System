from django.contrib import admin
from .models import GeneralSettings, AuditLog


@admin.register(GeneralSettings)
class GeneralSettingsAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'email', 'phone', 'max_file_size_mb', 'backup_enabled', 'updated_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'created_at')
    list_filter = ('action', 'model_name', 'created_at')
    search_fields = ('user__username', 'model_name', 'object_id', 'description')
    readonly_fields = ('created_at',)