from django.contrib import admin

from .models import Category, Course, Institution, Subject, SubjectMember, Tag


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'acronym', 'type', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'acronym']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution', 'is_active']
    list_filter = ['institution', 'is_active']
    search_fields = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'is_active']
    list_filter = ['course__institution', 'is_active']
    search_fields = ['name']


@admin.register(SubjectMember)
class SubjectMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'role', 'created_at']
    list_filter = ['role', 'subject__course__institution']
    search_fields = ['user__name', 'user__email', 'subject__name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
