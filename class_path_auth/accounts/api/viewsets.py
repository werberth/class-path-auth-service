from django.shortcuts import get_object_or_404

from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import (
    Address, Class, Course, Profile,
    Institution, Program, Student, User, Teacher
)

from . import serializers, permissions as custom_permissions


class BaseProfileView(viewsets.ModelViewSet):
    user_actions = ['list', 'retrieve']

    def get_serializer_class(self):
        if self.action in self.user_actions:
            return serializers.UserSerializer
        return self.serializer_class


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ProgramSerializer
    permission_classes = permissions.IsAuthenticated, custom_permissions.OnlyAdmin

    def get_queryset(self):
        institution = self.request.user.admin.institution
        return institution.programs.all()


class ClassViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ClassSerializer
    permission_classes = permissions.IsAuthenticated, custom_permissions.OnlyAdmin

    def get_queryset(self):
        institution = self.request.user.admin.institution
        programs = institution.programs.values_list('id', flat=True)
        return Class.objects.filter(program__id__in=programs)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CourseSerializer
    permission_classes = permissions.IsAuthenticated, custom_permissions.OnlyAdmin,

    def get_queryset(self):
        institution = self.request.user.admin.institution
        teachers = institution.teachers.values_list('id')
        return Course.objects.filter(teacher__id__in=teachers)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.UserSerializer
    permission_classes = permissions.IsAuthenticated, custom_permissions.OnlyAdmin

    def get_queryset(self):
        institution = self.request.user.admin.institution
        teacher_users_ids = institution.teachers.values_list('user__id', flat=True)

        programs = institution.programs.values_list('id', flat=True)
        classes = Class.objects.filter(program__id__in=programs)
        students = Student.objects.filter(class_id__in=classes)
        student_users_ids = students.values_list('user__id', flat=True)

        return User.objects.filter(id__in=list(teacher_users_ids) + list(student_users_ids))


class TeacherViewSet(BaseProfileView, viewsets.ReadOnlyModelViewSet):
    lookup_field = 'teacher__id'
    serializer_class = serializers.TeacherSerializer
    permission_classes = permissions.IsAuthenticated, custom_permissions.OnlyAdmin

    def get_queryset(self):
        institution = self.request.user.admin.institution
        teachers = institution.teachers.all()

        if self.action in self.user_actions:
            users = teachers.values_list('user__id', flat=True)
            return User.objects.filter(id__in=users)

        return teachers


class StudentViewSet(BaseProfileView, viewsets.ReadOnlyModelViewSet):
    lookup_field = 'student__id'
    serializer_class = serializers.StudentSerializer
    permission_classes = permissions.IsAuthenticated, custom_permissions.OnlyAdmin

    def get_queryset(self):
        institution = self.request.user.admin.institution
        programs = institution.programs.values_list('id', flat=True)
        classes = Class.objects.filter(program__id__in=programs)
        students = Student.objects.filter(class_id__in=classes)

        if self.action in self.user_actions:
            users = students.values_list('user__id', flat=True)
            return User.objects.filter(id__in=users)

        return students


class MyClassesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ClassSerializer
    permission_classes = permissions.IsAuthenticated, custom_permissions.OnlyTeachers

    def get_queryset(self):
        courses = self.request.user.teacher.courses.all()
        classes_id = courses.values_list('class_id', flat=True)
        return Class.objects.filter(id__in=classes_id)


class MyProgramsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ProgramSerializer
    permission_classes = custom_permissions.OnlyTeachers,

    def get_queryset(self):
        teacher = self.request.user.teacher
        program_ids = teacher.courses.values_list('class_id__program', flat=True)
        return Program.objects.filter(institution__in=program_ids)


class MyCoursesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CourseSerializer
    permission_classes = permissions.IsAuthenticated, custom_permissions.OnlyTeachersOrStudents

    def get_queryset(self):
        user = self.request.user

        if user.is_teacher:
            courses = user.teacher.courses.all()
            return courses
        elif user.is_student:
            courses = user.student.class_id.courses.all()
            return courses
