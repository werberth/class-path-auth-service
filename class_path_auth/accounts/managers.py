from django.db import models


class TeacherManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__is_teacher=True)


class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__is_student=True)
