from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('select-exam/', views.select_or_create_exam, name='select_exam'),
    path('arena/', views.study_arena_view, name='study_arena'),
]