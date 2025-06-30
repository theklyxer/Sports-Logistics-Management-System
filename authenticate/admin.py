from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Fields to display in the user list in the admin panel
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')

    # Add role to the fieldsets and add_fieldsets to appear in edit/create forms
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'age', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone', 'age', 'role')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
