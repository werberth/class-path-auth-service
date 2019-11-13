from rest_framework import generics, permissions

from . import serializers

from ..models import (
    Profile, Student, User, Teacher
)


class CreateRetrieveUserView(generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    post_method_permissions = permissions.IsAdminUser,
    get_method_permissions = permissions.IsAuthenticated,

    def get_object(self):
        return self.request.user

    def get_permissions(self):
        if self.request.method == "GET":
            return [permission() for permission in self.get_method_permissions]
        return [permission() for permission in self.post_method_permissions]


class CreateRetrieveTeacherView(generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = serializers.TeacherSerializer
    permission_classes = permissions.IsAuthenticated,

    def get_object(self):
        return self.request.user.teacher


class CreateRetrieveStudentsView(generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = serializers.StudentSerializer
    permission_classes = permissions.IsAuthenticated,

    def get_object(self):
        return self.request.user.student


class CreateRetrieveInstitutionView(generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = serializers.InstitutionSerializer
    post_method_permissions = permissions.IsAdminUser,
    get_method_permissions = permissions.IsAuthenticated,

    def get_object(self):
        if self.request.user.is_student:
            related_instance = self.request.user.student.class_id.program
        elif self.request.user.is_teacher:
            related_instance = self.request.user.teacher
        elif self.request.user.is_superuser:
            related_instance = self.request.user.admin
        return related_instance.institution

    def get_permissions(self):
        if self.request.method == "GET":
            return [permission() for permission in self.get_method_permissions]
        return [permission() for permission in self.post_method_permissions]


# generics as views
create_and_retrieve_user_view = CreateRetrieveUserView.as_view()
create_and_retrieve_teacher_view = CreateRetrieveTeacherView.as_view()
create_and_retrieve_student_view = CreateRetrieveStudentsView.as_view()
create_and_retrieve_institution_view = CreateRetrieveInstitutionView.as_view()
