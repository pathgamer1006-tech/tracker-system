from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from fitnesstrack import views as fitnesstrack_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='fitnesstrack/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/register/', fitnesstrack_views.register, name='register'),
    path('', include('fitnesstrack.urls')),  # All app URLs
]
