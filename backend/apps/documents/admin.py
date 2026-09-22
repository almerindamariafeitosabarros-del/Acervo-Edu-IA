from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'owner', 'institution', 'category', 'subject', 'visibility',
        'published_at', 'created_at',
    ]
    list_filter = ['visibility', 'institution', 'category']
    search_fields = ['title', 'description', 'material_author', 'owner__name', 'owner__email']
    autocomplete_fields = ['tags']
