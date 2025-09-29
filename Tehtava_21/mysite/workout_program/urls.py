# workout_program/urls.py
# workout_program/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('programs/', views.program_list, name='program_list'),
    path('program/<int:program_id>/', views.program_detail, name='program_detail'),
    path('program/<int:program_id>/day/<int:day_id>/', views.workout_day_detail, name='workout_day_detail'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('log-workout/<int:session_id>/', views.log_workout, name='log_workout'),
    path('exercises/', views.exercise_list, name='exercise_list'),
    path('api/progress/', views.api_workout_progress, name='api_progress'),
]
