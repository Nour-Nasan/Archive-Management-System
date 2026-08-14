from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Public
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # All authenticated users — profile & password
    path('profile/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),

    # System Administrator — user management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/approve/', views.user_approve, name='user_approve'),
    path('users/<int:pk>/reject/', views.user_reject, name='user_reject'),
    path('users/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:pk>/set-role/', views.user_set_role, name='user_set_role'),
]
