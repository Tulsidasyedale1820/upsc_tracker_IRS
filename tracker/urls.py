from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login_route'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_action, name='logout'),
]