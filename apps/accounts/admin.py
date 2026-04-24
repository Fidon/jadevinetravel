from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, MiniAdminProfile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('phone', 'nationality', 'preferred_language', 'profile_photo')}),
    )

@admin.register(MiniAdminProfile)
class MiniAdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_by', 'created_at']