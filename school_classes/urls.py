from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolClassViewSet

router = DefaultRouter()
router.register(r'', SchoolClassViewSet, basename='school-class')

urlpatterns = [
    path('', include(router.urls)),
]
