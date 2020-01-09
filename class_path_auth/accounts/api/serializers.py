from django.core import exceptions
from django.contrib.auth import password_validation as validators
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from ..models import (
    Admin, Address, Class, Course, Institution,
    Profile, Program, Student, User, Teacher,
)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id', 'state', 'city', 'street', 'neighborhood',
            'number', 'postal_code', 'complement', 'user',
            'created_at', 'modified_at'
        )


class StudentSerializer(serializers.ModelSerializer):
    student_id = serializers.ReadOnlyField(source='id')

    class Meta:
        depth = 2
        model = Student
        fields = (
            'student_id', 'cpf', 'user', 'description',
            'class_id', 'created_at', 'modified_at'
        )


class TeacherSerializer(serializers.ModelSerializer):
    teacher_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = Teacher
        fields = (
            'teacher_id', 'user', 'description',
            'created_at', 'modified_at'
        )


class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = Admin
        fields = (
            'id', 'institution', 'cpf', 'description', 'created_at', 'modified_at'
        )


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='id')
    profile = serializers.SerializerMethodField(read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    confirm_password = serializers.CharField(write_only=True)
    token = serializers.CharField(
        source='auth_token.key',
        read_only=True
    )

    class Meta:
        model = User
        depth = 2
        fields = (
            'user_id', 'email', 'registration_number', 'password',
            'confirm_password', 'addresses', 'profile',
            'is_teacher', 'is_student', 'is_admin', 'token'
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
            'confirm_password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
            'is_teacher': {'default': False},
            'is_student': {'default': False},
            'is_admin': {'default': False}
        }


    def get_profile(self, obj):
        profile = None

        if obj.is_student and getattr(obj, 'student', None):
            profile = StudentSerializer(obj.student)
        elif obj.is_teacher and getattr(obj, 'teacher', None):
            profile = TeacherSerializer(obj.teacher)
        elif obj.is_admin and getattr(obj, 'admin', None):
            profile = AdminSerializer(obj.admin)
        return profile.data if profile else {}


class ClassSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        depth = 2
        model = Class
        fields = (
            'id', 'name', 'description', 'program',
            'program_name', 'created_at', 'modified_at'
        )


class CourseSerializer(serializers.ModelSerializer):
    program = serializers.SerializerMethodField(read_only=True)

    def get_program(self, obj):
        return obj.class_id.program.name

    class Meta:
        depth = 2
        model = Course
        fields = (
            'id', 'name', 'description', 'class_id',
            'teacher', 'program', 'created_at', 'modified_at'
        )


class CourseSerializerReadOnly(CourseSerializer):
    class Meta:
        model = Course
        fields = (
            'id', 'name', 'description', 'class_id',
            'teacher', 'created_at', 'modified_at'
        )


class ClassSerializerReadOnly(ClassSerializer):
    class Meta:
        model = Class
        fields = (
            'id', 'name', 'description', 'created_at', 'modified_at'
        )


class ProgramSerializer(serializers.ModelSerializer):
    classes = ClassSerializerReadOnly(many=True, read_only=True)

    class Meta:
        model = Program
        fields = (
            'id', 'name', 'description', 'classes',
            'created_at', 'modified_at'
        )


class InstitutionSerializer(serializers.ModelSerializer):
    programs = ProgramSerializer(many=True, read_only=True)

    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'programs', 'description',
            'created_at', 'modified_at'
        )

    def create(self, validated_data):
        institution = super(InstitutionSerializer, self).create(validated_data)

        # define the created institution instance as institution of admin
        admin = self.context['request'].user.admin
        admin.institution = institution
        admin.save()

        return institution
