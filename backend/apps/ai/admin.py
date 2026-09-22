from django.contrib import admin

from .models import AIQuery


@admin.register(AIQuery)
class AIQueryAdmin(admin.ModelAdmin):
    list_display = ['user', 'document_label', 'model', 'response_time_ms', 'created_at']
    list_filter = ['model', 'created_at']
    search_fields = ['prompt', 'answer', 'user__email']
