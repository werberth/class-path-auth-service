from rest_framework import generics, permissions

from . import serializers

from ..models import (
    Profile, Student, User, Teacher
)


class CreateRetrieveUserView(generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    post_method_permissions = permissions.AllowAny,
    get_method_permissions = permissions.IsAuthenticated,

    def get_object(self):
        return self.request.user

    def get_permissions(self):
        if self.request.method == "GET":
            return [permission() for permission in self.get_method_permissions]
        return [permission() for permission in self.post_method_permissions]


class CreateRetrieveProfileView(generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = serializers.ProfileSerializer
    permission_classes = permissions.IsAuthenticated,

    def get_object(self):
        return self.request.user.profile


# generics as views
create_and_retrieve_user_view = CreateRetrieveUserView.as_view()
create_and_retrieve_profile_view = CreateRetrieveProfileView.as_view()
