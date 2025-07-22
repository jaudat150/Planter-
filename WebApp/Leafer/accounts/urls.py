# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views 

from . import views

urlpatterns = [
    path('register/', views.register_email_view, name='register'),
    path('verify-code/', views.verify_code_view, name='verify_code'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
 path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/change_password.html',
        success_url='/'
    ), name='change_password'),
    path('create-account/', views.create_account_view, name='create_account'),
]