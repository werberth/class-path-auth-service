from django.core import exceptions
from django.contrib.auth import authenticate, password_validation as validators
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from ..models import (
    Address, Class, Course, Profile,
    Program, Student, User, Teacher
)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id', 'state', 'city', 'street', 'neighborhood',
            'number', 'postal_code', 'complement', 'profile',
            'created_at', 'modified_at'
        )

        extra_kwargs = {
            'profile': {'write_only': True},
        }


class ProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'addresses', 'cpf', 'full_name', 'user',
            'description', 'created_at', 'modified_at'
        )

        extra_kwargs = {
            'user': {'write_only': True},
        }


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True,)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        depth = 2
        fields = (
            'id', 'confirm_password', 'registration_number',
            'email', 'profile', 'password', 'is_teacher', 'is_student'
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
        password = validated_data.pop('confirm_password')
        user = super(UserSerializer, self).create(validated_data)

        if 'password' in validated_data:
            user.set_password(validated_data['password'])
            user.save()

        token = Token.objects.create(user=user)

        return user

    def to_representation(self, instance):
        ret = super(UserSerializer, self).to_representation(instance)

        if self.context['request'].method == "POST":
            ret['token'] = Token.objects.get(user=instance).key

        return ret


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = (
            'name', 'description', 'program',
            'created_at', 'modified_at'
        )


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'name', 'description', 'class_ref',
            'teacher', 'program', 'created_at',
            'modified_at'
        )


class ProgramSerializer(serializers.ModelSerializer):
    classes = ClassSerializer(many=True, read_only=True)
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = (
            'name', 'description', 'classes',
            'courses', 'created_at', 'modified_at'
        )
