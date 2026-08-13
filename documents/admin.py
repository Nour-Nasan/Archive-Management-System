from django.contrib import admin
from .models import Department, DocumentType, Document, DocumentFile


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class DocumentFileInline(admin.TabularInline):
    model = DocumentFile
    extra = 1
    readonly_fields = ('file_size', 'file_type', 'uploaded_at')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_number', 'title', 'document_type', 'department', 'status', 'created_by', 'created_at')
    list_filter = ('document_type', 'department', 'status', 'created_at')
    search_fields = ('document_number', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DocumentFileInline]


@admin.register(DocumentFile)
class DocumentFileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'document', 'version', 'file_type', 'file_size', 'uploaded_by', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('original_name', 'document__title', 'document__document_number')
    readonly_fields = ('uploaded_at',)