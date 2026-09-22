from django.contrib import admin

from .models import MuralAttachment, MuralPost, MuralReport


class MuralAttachmentInline(admin.TabularInline):
    model = MuralAttachment
    extra = 0


@admin.register(MuralPost)
class MuralPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'is_comment', 'status', 'report_count', 'created_at']
    list_filter = ['status']
    search_fields = ['text', 'author__name', 'author__email']
    inlines = [MuralAttachmentInline]


@admin.register(MuralReport)
class MuralReportAdmin(admin.ModelAdmin):
    list_display = ['post', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status']
    search_fields = ['post__text', 'reporter__name', 'reporter__email']
