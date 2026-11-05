
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'username',
        'email',
        'role',
        'is_approved',
        'is_active',
        'is_staff',
    )

    list_filter = (
        'role',
        'is_approved',
        'is_active',
    )

    search_fields = (
        'username',
        'email',
    )

    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Access Management', {
            'fields': (
                'role',
                'is_approved',
            ),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Access Management', {
            'fields': (
                'role',
                'is_approved',
            ),
        }),
    )
