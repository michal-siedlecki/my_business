from django.contrib.auth import views as auth_views
from django.urls import path

from .views import register, profile

urlpatterns = [
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/users_login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/users_logout.html'), name='logout')
]
