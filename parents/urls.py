from django.urls import path
from . import views
from . import student_parent_views
from . import parent_dashboard_views

urlpatterns = [
    # Parent CRUD
    path('', views.parent_list_create, name='parent-list-create'),
    path('<uuid:pk>/', views.parent_detail, name='parent-detail'),
    
    # Student-Parent Linking
    path('link-student/', student_parent_views.link_student_to_parent, name='link-student-parent'),
    path('student/<uuid:student_id>/parents/', student_parent_views.get_student_parents, name='student-parents'),
    path('parent/<uuid:parent_id>/children/', student_parent_views.get_parent_children, name='parent-children'),
    path('my-children/', student_parent_views.get_my_children, name='my-children'),
    path('unlink/<uuid:link_id>/', student_parent_views.unlink_student_from_parent, name='unlink-student-parent'),
    
    # Parent Dashboard - View Children's Data
    path('child/<uuid:student_id>/attendance/', parent_dashboard_views.get_child_attendance, name='child-attendance'),
    path('dashboard/attendance/', parent_dashboard_views.get_my_children_attendance, name='my-children-attendance'),
]
