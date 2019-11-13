from rest_framework import viewsets, permissions
from rest_framework import generics

from . import serializers

from ..models import (
    Address, Class, Course, Profile,
    Program, Student, User, Teacher
)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AddressSerializer
    permission_classes = permissions.IsAuthenticated,

    def get_queryset(self):
        return self.request.user.profile.addresses.all()


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = serializers.ProgramSerializer
    permission_classes = permissions.IsAuthenticated,


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = serializers.ClassSerializer
    permission_classes = permissions.IsAuthenticated,


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = serializers.CourseSerializer
