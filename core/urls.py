
from django.urls import path
from . import views

urlpatterns = [

    # User home page
    path(
        '',
        views.home,
        name='home'
    ),

    # Admin dashboard
    path(
        'dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    # Admin user management
    path(
        'manage-users/',
        views.manage_users,
        name='manage_users'
    ),

    # Update TradeTron settings
    path(
        'update-tradetron/',
        views.update_tradetron_settings,
        name='update_tradetron_settings'
    ),

]
