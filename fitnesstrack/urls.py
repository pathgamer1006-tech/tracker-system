from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Activity Management
    path('activities/', views.ActivityListView.as_view(), name='activity_list'),
    path('activity/log/', views.log_activity, name='log_activity'),
    path('activity/<int:pk>/edit/', views.edit_activity, name='edit_activity'),
    path('activity/<int:pk>/delete/', views.delete_activity, name='delete_activity'),
    path('activity/<int:pk>/', views.fit_detail, name='activity_detail'),
    
    # API Endpoints
    path('api/log-activity/', views.api_log_activity, name='api_log_activity'),
    path('api/log-water/', views.log_water_quick, name='api_log_water'),
    path('api/log-meal/', views.log_meal_quick, name='api_log_meal'),
    
    # Biometrics Management
    path('biometrics/', views.BiometricsListView.as_view(), name='biometrics_list'),
    path('biometrics/update/', views.update_biometrics, name='update_biometrics'),
    
    # Profile Management
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Water Intake
    path('water/log/', views.log_water, name='log_water'),
    path('api/log-water/', views.log_water_quick, name='api_log_water'),
    
    # Progress & Charts
    path('progress/', views.progress_charts, name='progress_charts'),
    path('badges/', views.badges_view, name='badges'),
    
    # Legacy URLs (for backward compatibility)
    path('list/', views.fit_list, name='fit_list'),
    path('detail/<int:pk>/', views.fit_detail, name='fit_detail'),
    path('form/', views.fit_form, name='fit_form'),
    path('form/<int:pk>/', views.fit_form, name='fit_form_edit'),
    path('delete/<int:pk>/', views.fit_confirm_delete, name='fit_confirm_delete'),
]
