from django.core import exceptions
from django.contrib.auth import authenticate, password_validation as validators
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from ..models import (
    Address, Class, Course, Institution,
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
            'profile': {'write_only': True},
        }


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = (
            'id', 'addresses', 'cpf', 'full_name',
            'user', 'description', 'class_id',
            'created_at', 'modified_at'
        )

        extra_kwargs = {
            'user': {'write_only': True},
        }


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = (
            'id', 'cpf', 'full_name', 'user', 'institution',
            'description', 'created_at', 'modified_at'
        )

        extra_kwargs = {
            'user': {'write_only': True},
        }


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = (
            'id', 'class_id', 'cpf', 'description',
            'full_name', 'user', 'created_at', 'modified_at'
        )

        extra_kwargs = {
            'user': {'write_only': True},
        }


class UserSerializer(serializers.ModelSerializer):
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
            'id', 'addresses', 'confirm_password',
            'registration_number', 'email', 'profile',
            'password', 'is_teacher', 'token', 'is_student'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
            'is_teacher': {'default': False},
            'is_student': {'default': False}
        }

    def validate_password(self, value):
        try:
            # validate the password and catch the exception
            validators.validate_password(password=value, user=self.instance)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": _("Passwords don't match")
            })

        if data['is_teacher'] and data['is_student']:
            raise serializers.ValidationError({
                "is_teacher": _(
                    "An User cannot be a Teacher and a Student at same time."
                )
            })

        return super(UserSerializer, self).validate(data)

    def update(self, validated_data):
        user = super(UserSerializer, self).update(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return User.objects.create_user(**validated_data)

    def get_profile(self, obj):
        profile = None

        if obj.is_student and getattr(obj, 'student', None):
            profile = StudentSerializer(obj.student)
        elif obj.is_teacher and getattr(obj, 'teacher', None):
            profile = TeacherSerializer(obj.teacher)
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
            'name', 'description', 'program',
            'created_at', 'modified_at'
        )


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all()
    )

    class Meta:
        model = Course
        fields = (
            'name', 'description', 'class_id',
            'teacher', 'program', 'created_at',
            'modified_at'
        )


class ProgramSerializer(serializers.ModelSerializer):
    classes = ClassSerializer(many=True, read_only=True)
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = (
            'name', 'description', 'classes', 'institution',
            'courses', 'created_at', 'modified_at'
        )
