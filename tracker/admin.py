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
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'university')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'username', 'university', 'password1', 'password2',)}),
    )
    

    
