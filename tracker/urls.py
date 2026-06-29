from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('verify/', views.verify_view, name='verify_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('select-exam/', views.select_or_create_exam, name='select_exam'),
    path('arena/', views.study_arena_view, name='study_arena'),
    path('subject/<int:subject_id>/', views.subject_detail_view, name='subject_detail'),
    
    # Core Application Endpoint APIs
    path('api/subject-details/<int:subject_id>/', views.get_subject_matrix_details, name='sub_details'),
    path('api/save-config/', views.save_configuration_matrix, name='save_config'),
    path('api/add-topic/', views.append_topic_node, name='add_topic'),
    path('api/add-subtopic/', views.append_subtopic_node, name='add_subtopic'),
    path('api/toggle-subtopic/', views.toggle_subtopic_node, name='toggle_subtopic'),
    path('api/save-mins/', views.commit_timer_minutes, name='save_mins'),
]