from django.urls import path, include

from rest_framework import routers
from rest_framework.authtoken import views as auth_views

from . import viewsets, views

router = routers.SimpleRouter()
router.register(r'address', viewsets.AddressViewSet, basename="Address")
router.register(r'program', viewsets.ProgramViewSet)
router.register(r'class', viewsets.ClassViewSet)
router.register(r'course', viewsets.CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-login/', auth_views.obtain_auth_token),
    path('user/', views.create_and_retrieve_user_view),
    path('teacher/', views.create_and_retrieve_teacher_view),
    path('student/', views.create_and_retrieve_student_view),
    path('institution/', views.create_and_retrieve_institution_view)
]
