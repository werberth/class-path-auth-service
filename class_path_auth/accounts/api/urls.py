from django.urls import path, include

from rest_framework import routers
from rest_framework.authtoken import views as auth_views

from . import viewsets, views

router = routers.SimpleRouter()
router.register(r'address', viewsets.AddressViewSet)
router.register(r'program', viewsets.ProgramViewSet)
router.register(r'class', viewsets.ClassViewSet)
router.register(r'course', viewsets.CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-login/', auth_views.obtain_auth_token),
    path('user/', views.create_and_retrieve_user_view),
    path('profile/', views.create_and_retrieve_profile_view)
]
