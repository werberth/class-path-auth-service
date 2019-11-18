from django.shortcuts import get_object_or_404

from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action

from ..models import (
    Address, Class, Course, Profile,
    Institution, Program, Student, User, Teacher
)

from . import serializers, permissions as custom_permissions


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = serializers.AddressSerializer
    permission_classes = permissions.IsAuthenticated,

    def get_queryset(self):
        return self.request.user.addresses.all()


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = serializers.ProgramSerializer
    permission_classes = permissions.IsAdminUser,


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = serializers.ClassSerializer
    permission_classes = permissions.IsAdminUser,


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = serializers.CourseSerializer
    permission_classes = permissions.IsAdminUser


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = permissions.IsAdminUser,


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer
    permission_classes = permissions.IsAdminUser,


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = serializers.StudentSerializer
    permission_classes = permissions.IsAdminUser,


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = serializers.InstitutionSerializer
    permission_classes = permissions.IsAdminUser,


class MyClassesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ClassSerializer
    permission_classes = custom_permissions.OnlyTeachers,

    def get_queryset(self):
        courses = self.request.user.teacher.courses.all()
        classes_id = courses.values_list('class_id', flat=True)
        return Class.objects.filter(id__in=classes_id)


class MyProgramsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ProgramSerializer
    permission_classes = custom_permissions.OnlyTeachers,

    def get_queryset(self):
        courses = self.request.user.teacher.courses.all()
        program_ids = courses.values_list('program', flat=True)
        return Program.objects.filter(id__in=program_ids)


class MyCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CourseSerializer
    permission_classes = custom_permissions.OnlyTeachersOrStudents,

    def get_queryset(self):
        user = self.request.user

        if user.is_teacher:
            courses = user.teacher.courses.all()
            return courses
        elif user.is_student:
            courses = user.student.class_id.courses.all()
            return courses
