from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType

from django.db import models

from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class User(AbstractUser):
    registration_number = models.CharField(
        _('registration number'),
        max_length=25,
        unique=True
    )
    email = models.EmailField(_('email address'), unique=True)
    is_teacher = models.BooleanField(_('is teacher'), default=False)
    is_student = models.BooleanField(_('is student'), default=False)
    is_admin = models.BooleanField(_('is_admin'), default=False)

    objects = CustomUserManager()

    username = None

    USERNAME_FIELD = 'registration_number'

    class Meta:
        db_table = 'users'
        managed = False

    def __str__(self):
        return self.email


class Profile(models.Model):
    cpf = models.CharField(
        _('cpf'),
        max_length=100,
        default=None,
        null=True,
        blank=True
    )
    description = models.TextField(_('description'), blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.email


class Institution(models.Model):
    name = models.CharField(_('name'), max_length=250)
    description = models.TextField(_('description'), blank=True, null=True)
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified_at'), auto_now=True)

    class Meta:
        db_table = 'institution'
        managed = False

    def __str__(self):
        return self.name


class Program(models.Model):
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True, null=True)
    institution = models.ForeignKey(
        Institution,
        related_name="programs",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)

    class Meta:
        db_table = 'program'
        managed = False

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


class Admin(Profile):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="admin"
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="admins",
        null=True,
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)

    class Meta:
        db_table = 'admin'
        managed = False


class Teacher(Profile):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher"
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="teachers"
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)

    class Meta:
        db_table = 'teacher'
        managed = False


class Student(Profile):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student"
    )
    class_id = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="students"
    )

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)

    class Meta:
        db_table = 'student'
        managed = False


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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified_at'), auto_now=True)

    class Meta:
        db_table = 'address'
        managed = False

    def __str__(self):
       return f'{self.street} {self.number}, {self.postal_code}'


class Course(models.Model):
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True, null=True)
    class_id = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)

    class Meta:
        db_table = 'course'
        managed = False

    def __str__(self):
        return self.name


class Scores(models.Model):
    first_score = models.FloatField(_('first score'), null=True)
    second_score = models.FloatField(_('second score'), null=True)
    third_score = models.FloatField(_('third score'), null=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="scores"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="scores"
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)

    class Meta:
        db_table = 'scores'
        managed = False

    def __str__(self):
        return self.name
