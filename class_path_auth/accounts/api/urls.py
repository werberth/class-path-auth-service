from django.urls import path, include

from rest_framework import routers
from rest_framework.authtoken import views as auth_views

from . import viewsets, views

router = routers.SimpleRouter()
router.register(
    r'institutions',
    viewsets.InstitutionViewSet,
    basename="Institution"
)
router.register(
    r'users',
    viewsets.UserViewSet,
    basename="User"
)
router.register(
    r'addresses',
    viewsets.AddressViewSet,
    basename="Address"
)
router.register(
    r'student',
    viewsets.StudentViewSet,
    basename="Student"
)
router.register(
    r'my-classes',
    viewsets.MyClassesViewSet,
    basename='Class'
)
router.register(
    r'my-courses',
    viewsets.MyCoursesViewSet,
    basename='Course'
)
router.register(
    r'my-programs',
    viewsets.MyProgramsViewSet,
    basename='Program'
)
router.register(r'program', viewsets.ProgramViewSet)
router.register(r'class', viewsets.ClassViewSet)
router.register(r'course', viewsets.CourseViewSet)
router.register(r'teacher', viewsets.TeacherViewSet)
router.register(r'teacher', viewsets.TeacherViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', auth_views.obtain_auth_token),
    path('my-account/', views.my_user_view),
    path('my-profile/', views.my_profile_view),
    path('my-class/', views.my_class_view),
    path('my-institution/', views.my_institution_view)
]
