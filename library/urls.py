from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, BookIssueViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'issues', BookIssueViewSet, basename='bookissue')

urlpatterns = [
    path('', include(router.urls)),
]
