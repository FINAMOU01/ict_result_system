from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.create_user, name='create_user'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/toggle/', views.toggle_user_active, name='toggle_user_active'),
]
