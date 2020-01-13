from django.contrib.auth.models import UserManager, Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework.authtoken.models import Token


class CustomUserManager(UserManager):
    def create_user(self, registration_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(registration_number, email, password, **extra_fields)

    def create_superuser(self, registration_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(registration_number, email, password, **extra_fields)

    def define_permissions(self, instance):
        content_type = ContentType.objects.get_for_model(instance)
        if instance.is_student:
            permission_is_student, _ = Permission.objects.get_or_create(
                codename='is_student',
                name='Is student',
                content_type=content_type,
            )
            instance.user_permissions.add(permission_is_student.id)
        elif instance.is_teacher:
            permission_is_teacher, _ = Permission.objects.get_or_create(
                codename='is_teacher',
                name='Is teacher',
                content_type=content_type,
            )
            instance.user_permissions.add(permission_is_teacher.id)

    def _create_user(self, registration_number, email, password, **extra_fields):
        """
        Create and save a user with the given registration_number, email, and password.
        """

        from .models import Admin, Student, Teacher

        if not registration_number:
            raise ValueError('The given registration_number must be set')

        email = self.normalize_email(email)
        username = self.model.normalize_username(registration_number)
        user = self.model(registration_number=registration_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # create api token
        Token.objects.create(user=user)

        # define user permissions
        self.define_permissions(user)

        return user
