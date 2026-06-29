from django.urls import path
from . import views

urlpatterns = [
    path('arena/', views.study_arena_view, name='study_arena'),
    path('api/subject-details/<int:subject_id>/', views.get_subject_matrix_details, name='sub_details'),
    path('api/save-config/', views.save_configuration_matrix, name='save_config'),
    path('api/add-topic/', views.append_topic_node, name='add_topic'),
    path('api/add-subtopic/', views.append_subtopic_node, name='add_subtopic'),
    path('api/toggle-subtopic/', views.toggle_subtopic_node, name='toggle_subtopic'),
    path('api/save-mins/', views.commit_timer_minutes, name='save_mins'),
]