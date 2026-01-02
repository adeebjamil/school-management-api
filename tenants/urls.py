from django.urls import path
from . import views

urlpatterns = [
    path('', views.tenant_list_create, name='tenant_list_create'),
    path('by-school-code/', views.get_tenant_by_school_code, name='get_tenant_by_school_code'),
    path('<uuid:tenant_id>/', views.tenant_detail, name='tenant_detail'),
    path('<uuid:tenant_id>/users/', views.tenant_users, name='tenant_users'),
    path('<uuid:tenant_id>/features/', views.tenant_features, name='tenant_features'),
    path('<uuid:tenant_id>/features/<str:feature>/toggle/', views.toggle_feature, name='toggle_feature'),
]
