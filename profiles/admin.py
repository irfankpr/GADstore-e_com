from django.contrib import admin
from .models import userprofiles
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.admin import UserAdmin


class Accadmin(admin.ModelAdmin):
    ordering = ()
    list_display = (
    'id', 'first_name', 'last_name', 'phone', 'email', 'is_admin', 'is_superadmin', 'is_staff', 'is_active', 'blocked')
    list_display_links = ('id', 'email', 'phone')
    search_fields = ('id', 'phone', 'email')
    readonly_fields = ('last_login', 'date_joined',)
    ordering = ('id', 'date_joined')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (
            'Fields',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'phone',
                    'email',
                    'password',
                    'is_admin',
                    'is_superadmin',
                    'is_active',
                    'is_staff',

                )
            },
        ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name',
                       'last_name',
                       'phone',
                       'email',
                       'password',
                       'is_admin',
                       'is_superadmin',
                       'is_active',
                       'is_staff',),
        }),
    )


admin.site.register(userprofiles, Accadmin)
