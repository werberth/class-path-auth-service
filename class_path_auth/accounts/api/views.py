from rest_framework import permissions, generics

from ..models import Class

from . import serializers, permissions as custom_permissions


class MyAccountView(generics.RetrieveAPIView, generics.UpdateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = permissions.IsAuthenticated,

    def get_object(self):
        return self.request.user


class MyProfileView(generics.RetrieveAPIView, generics.UpdateAPIView):
    permission_classes = permissions.IsAuthenticated,

    def get_object(self):
        if self.request.user.is_student:
            return self.request.user.student
        elif self.request.user.is_teacher:
            return self.request.user.teacher
        else:
            return self.request.user.admin

    def get_serializer_class(self):
        if self.request.user.is_student:
            return serializers.StudentSerializer
        elif self.request.user.is_teacher:
            return serializers.TeacherSerializer
        else:
            return serializers.AdminSerializer


class MyInstitutionView(generics.RetrieveAPIView):
    serializer_class = serializers.InstitutionSerializer
    permission_classes = permissions.IsAuthenticated,

    def get_object(self):
        if self.request.user.is_student:
            student = self.request.user.student
            return student.class_id.program.institution
        elif self.request.user.is_teacher:
            return self.request.user.teacher.institution
        else:
            return self.request.user.admin.institution


class MyProgramView(generics.RetrieveAPIView):
    serializers = serializers.ProgramSerializer
    permission_classes = custom_permissions.OnlyStudents,

    def get_object(self):
        return self.request.user.student.class_id.program


class MyClassView(generics.RetrieveAPIView):
    serializer_class = serializers.ClassSerializer
    permission_classes = custom_permissions.OnlyStudents,

    def get_object(self):
        return self.request.user.student.class_id


# Generics as views
my_class_view = MyClassView.as_view()
my_user_view = MyAccountView.as_view()
my_profile_view = MyProfileView.as_view()
my_institution_view = MyInstitutionView.as_view()
