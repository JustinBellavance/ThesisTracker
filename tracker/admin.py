from django.contrib import admin
from .models import Thesis

@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = ("name", "upload_date", "word_change")
    list_filter = ("upload_date",)
    search_fields = ("name",)
    

    
