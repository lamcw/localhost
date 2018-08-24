from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from placeholder.authentication.models import User


class UserAdmin(BaseUserAdmin):
    add_fieldsets = ((None, {
        'classes': ('wide', ),
        'fields': ('username', 'email', 'first_name', 'last_name', 'bio',
                   'password1', 'password2', 'dob', 'gender')
    }), )


admin.site.register(User, UserAdmin)
