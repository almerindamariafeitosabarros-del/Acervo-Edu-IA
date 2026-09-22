from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['name']
    list_display = ['name', 'email', 'role', 'is_active', 'accepted_terms_at']
    list_filter = ['role', 'is_active', 'institution']
    search_fields = ['name', 'email']
    readonly_fields = ['accepted_terms_at', 'accepted_terms_version']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Dados pessoais', {'fields': ('name', 'institution')}),
        ('Permissões', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Consentimento (LGPD)', {'fields': ('accepted_terms_at', 'accepted_terms_version')}),
        ('Datas', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'password1', 'password2'),
        }),
    )
