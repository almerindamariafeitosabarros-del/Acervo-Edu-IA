from rest_framework import serializers

from .models import Category, Course, Institution, Subject, SubjectMember, Tag


class InstitutionSerializer(serializers.ModelSerializer):
    courses_count = serializers.IntegerField(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Institution
        fields = ['id', 'name', 'acronym', 'type', 'type_display', 'is_active', 'courses_count']


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


class SubjectMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = SubjectMember
        fields = ['id', 'subject', 'user', 'user_name', 'user_email', 'role', 'created_at']
        read_only_fields = ['subject']

    def validate_user(self, value):
        subject = self.context['subject']
        if value.institution_id != subject.course.institution_id:
            raise serializers.ValidationError(
                'O usuário precisa pertencer à mesma instituição da disciplina.'
            )
        return value

    def create(self, validated_data):
        validated_data['subject'] = self.context['subject']
        return super().create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']
