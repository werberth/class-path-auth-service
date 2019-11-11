from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils.translation import gettext_lazy as _

from .managers import TeacherManager, StudentManager


class User(AbstractUser):
    registration_number = models.CharField(
        _('registration number'),
        max_length=25,
        unique=True
    )
    is_teacher = models.BooleanField(_('is teacher'), default=False)
    is_student = models.BooleanField(_('is student'), default=False)

    username = None

    USERNAME_FIELD = 'registration_number'

    class Meta:
        db_table = 'users'
        managed = False


class Profile(models.Model):
    cpf = models.CharField(
        _('cpf'),
        max_length=100,
        unique=True
    )
    full_name = models.CharField(
        _('full name'),
        max_length=250,
        blank=True,
        null=True
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(_('description'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)

    class Meta:
        db_table = 'profile'
        managed = False


class Teacher(Profile):
    objects = TeacherManager()

    class Meta:
        proxy = True


class Student(Profile):
    objects = StudentManager()

    class Meta:
        proxy = True


class Address(models.Model):
    state = models.CharField(_('state'), max_length=2)
    city = models.CharField(_('city'), max_length=100)
    street = models.CharField(_('street'), max_length=250)
    neighborhood = models.CharField(_('neighborhood'), max_length=100)
    number = models.IntegerField(_('number'))
    postal_code = models.CharField(_('postal_code'), max_length=250)
    complement = models.CharField(
        _('complement'),
        max_length=250,
        blank=True,
        null=True
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified_at'), auto_now=True)

    class Meta:
        db_table = 'address'
        managed = False


class Program(models.Model):
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True, null=True)
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified_at'), auto_now=True)

    class Meta:
        db_table = 'program'
        managed = False


class Class(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="classes"
    )
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified_at'), auto_now=True)

    class Meta:
        db_table = 'class'
        managed = False


class Course(models.Model):
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True, null=True)
    class_ref = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    teacher = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified_at'), auto_now=True)

    class Meta:
        db_table = 'course'
        managed = False
