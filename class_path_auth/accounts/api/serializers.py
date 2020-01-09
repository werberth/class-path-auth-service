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

        extra_kwargs = {
            'user': {'read_only': True},
        }

    def create(self, validated_data):
        validated_data.update({'user': self.context['request'].user})
        return super().create(validated_data)


class StudentSerializer(serializers.ModelSerializer):
    student_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = Student
        fields = (
            'student_id', 'cpf', 'user', 'description',
            'class_id', 'created_at', 'modified_at'
        )

        extra_kwargs = {
            'user': {'write_only': True},
        }


class TeacherSerializer(serializers.ModelSerializer):
    teacher_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = Teacher
        fields = (
            'teacher_id', 'user', 'description',
            'created_at', 'modified_at'
        )

        extra_kwargs = {
            'user': {'write_only': True},
        }

    def create(self, validated_data):
        admin = self.context['request'].user.admin
        validated_data.update({'institution': admin.institution})
        return super().create(validated_data)


class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = Admin
        fields = (
            'id', 'institution', 'cpf', 'description',
            'user', 'created_at', 'modified_at'
        )

        extra_kwargs = {
            'user': {'write_only': True},
        }


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

    def validate_password(self, value):
        try:
            # validate the password and catch the exception
            validators.validate_password(password=value, user=self.instance)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    # def validate(self, data):
    #     user = self.instance

    #     if data.get('password') != data.get('confirm_password'):
    #         raise serializers.ValidationError({
    #             "confirm_password": _("Passwords don't match")
    #         })

    #     if sum([
    #             data.get('is_admin', user.is_admin if user else None),
    #             data.get('is_student', user.is_student if user else None),
    #             data.get('is_teacher', user.is_teacher if user else None)
    #         ]) > 1:
    #         raise serializers.ValidationError({
    #             "is_teacher": _(
    #                 "An User can't have more then one profile."
    #             )
    #         })

    #     return super(UserSerializer, self).validate(data)

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)

    def get_profile(self, obj):
        profile = None

        if obj.is_student and getattr(obj, 'student', None):
            profile = StudentSerializer(obj.student)
        elif obj.is_teacher and getattr(obj, 'teacher', None):
            profile = TeacherSerializer(obj.teacher)
        elif obj.is_admin and getattr(obj, 'admin', None):
            profile = AdminSerializer(obj.admin)
        return profile.data if profile else {}


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'description',
            'created_at', 'modified_at'
        )

    def create(self, validated_data):
        institution = super(InstitutionSerializer, self).create(validated_data)

        # define the created institution instance as institution of admin
        admin = self.context['request'].user.admin
        admin.institution = institution
        admin.save()

        return institution


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = (
            'id', 'name', 'description', 'program',
            'created_at', 'modified_at'
        )


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all()
    )

    class Meta:
        model = Course
        fields = (
            'id', 'name', 'description', 'class_id',
            'teacher', 'created_at', 'modified_at'
        )


class ProgramSerializer(serializers.ModelSerializer):
    classes = ClassSerializer(many=True, read_only=True)
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = (
            'id', 'name', 'description', 'classes',
            'courses', 'created_at', 'modified_at'
        )

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.update({'institution': user.admin.institution})
        return super().create(validated_data)
