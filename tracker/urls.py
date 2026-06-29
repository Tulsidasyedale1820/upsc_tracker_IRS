from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('select-exam/', views.select_or_create_exam, name='select_exam'),
    path('arena/', views.study_arena_view, name='study_arena'),
    path('api/save-time/', views.save_time_spent, name='save_time'),
    path('api/add-subject/', views.add_custom_subject, name='add_subject'),
    path('api/topics/<int:subject_id>/', views.get_subject_topics, name='get_topics'),
    path('api/update-weightage/', views.update_subject_weightage, name='update_weightage'),
    path('api/add-topic/', views.add_custom_topic, name='add_topic'),
]