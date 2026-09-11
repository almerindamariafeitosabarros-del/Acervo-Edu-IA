from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'category', 'subject', 'visibility', 'created_at']
    list_filter = ['visibility', 'category', 'subject__course__institution']
    search_fields = ['title', 'description', 'material_author', 'owner__name', 'owner__email']
    autocomplete_fields = ['tags']
