from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('verify/', views.verify_view, name='verify_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('select-exam/', views.select_or_create_exam, name='select_exam'),
    path('arena/', views.study_arena_view, name='study_arena'),
    
    # Core Global Tracker APIs
    path('api/global-details/', views.get_global_matrix_details, name='global_details'),
    path('api/save-config/', views.save_configuration_matrix, name='save_config'),
    path('api/add-topic/', views.append_topic_node, name='add_topic'),
    path('api/update-topic-metrics/', views.update_topic_metrics, name='update_topic_metrics'),
    path('api/sync-timer/', views.sync_chronometer_seconds, name='sync_timer'),
    path('api/delete-topic/', views.delete_topic_node, name='delete_topic'),
    path('api/add-subtopic/', views.append_subtopic_node, name='add_subtopic'),
    path('api/toggle-subtopic/', views.toggle_subtopic_node, name='toggle_subtopic'),
]