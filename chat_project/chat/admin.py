from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'name', 'is_staff')  # ✅ updated
    search_fields = ('email', 'name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password', 'profile_pic')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
