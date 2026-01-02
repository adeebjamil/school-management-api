from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, RouteViewSet, TransportAssignmentViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'assignments', TransportAssignmentViewSet, basename='transport-assignment')

urlpatterns = [
    path('', include(router.urls)),
]
