from rest_framework import serializers

from .models import Category, Course, Institution, Subject, Tag


class InstitutionSerializer(serializers.ModelSerializer):
    courses_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Institution
        fields = ['id', 'name', 'acronym', 'is_active', 'courses_count']


class CourseSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    subjects_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'institution', 'institution_name', 'is_active', 'subjects_count']


class SubjectSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    institution = serializers.IntegerField(source='course.institution_id', read_only=True)
    institution_name = serializers.CharField(source='course.institution.name', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'course', 'course_name', 'institution', 'institution_name', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']
