"""
URLs for authentication (login, logout).
Signup disabled - accounts created via admin panel only.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from leads import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('signup/', views.signup_view, name='signup'),  # Disabled - use admin panel to create users
]




