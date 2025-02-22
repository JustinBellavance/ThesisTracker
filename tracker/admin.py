from django.contrib import admin
from .models import Thesis, CustomUser

@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = ("username", "upload_date", "word_change")

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'university')
    fieldsets = (
        (None, {'fields': ('email',)}),  # Removed 'password' from here
        ('Personal info', {'fields': ('username', 'university', 'thesis_title')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'username', 'university', 'thesis_title', 'password1', 'password2')}),
    )
    readonly_fields = ('password',)  # Prevent password from being changed manually
