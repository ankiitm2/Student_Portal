from django.urls import path
from . import views
from .api import get_courses
from .views import student_list, student_register, student_detail, student_edit, student_delete, teacher_list, teacher_register, teacher_detail, course_list, subject_list

urlpatterns = [
    # Authentication URLs
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API URLs
    path('api/get-courses/', get_courses, name='get_courses'),
    
    # Student URLs
    path('students/', views.student_list, name='student_list'),
    path('students/register/', views.student_register, name='student_register'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    
    # Teacher URLs
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/register/', views.teacher_register, name='teacher_register'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    
    # Course/Subject URLs
    path('courses/', views.course_list, name='course_list'),
    path('subjects/', views.subject_list, name='subject_list'),
]