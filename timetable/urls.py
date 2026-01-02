from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimeSlotViewSet, TimetableViewSet

router = DefaultRouter()
router.register(r'time-slots', TimeSlotViewSet, basename='time-slot')
router.register(r'entries', TimetableViewSet, basename='timetable')

urlpatterns = [
    path('', include(router.urls)),
]
