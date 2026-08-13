from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'can_view_documents',
        'can_add_documents',
        'can_edit_documents',
        'can_delete_documents',
        'can_manage_users',
        'can_view_reports',
        'can_manage_settings',
    )
    search_fields = ('name',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'department', 'is_staff', 'is_active')
    list_filter = ('role', 'department', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Archive System Info', {
            'fields': ('role', 'phone_number', 'department', 'job_title', 'profile_image')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Archive System Info', {
            'fields': ('email', 'role', 'phone_number', 'department', 'job_title')
        }),
    )