from django.urls import path, include
from .api.urls import urlpatterns as api_urls

urlpatterns = [
    path('', include(api_urls)),
]
