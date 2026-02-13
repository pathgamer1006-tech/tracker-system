from django.contrib import admin
from .models import (
    UserProfile,
    ActivityLog,
    BiometricsLog,
    Goal,
    WaterIntake,
    Badge,
    MealLog
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'age', 'bmi']
    list_filter = ['gender', 'activity_level']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'duration_minutes', 'distance_km', 'calories_burned', 'date_created']
    list_filter = ['activity_type', 'date_created']
    search_fields = ['user__username', 'notes']
    date_hierarchy = 'date_created'
    readonly_fields = ['calories_burned']


@admin.register(BiometricsLog)
class BiometricsLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'weight_kg', 'body_fat_percentage', 'muscle_mass_kg', 'date_recorded', 'bmi']
    list_filter = ['date_recorded']
    search_fields = ['user__username']
    date_hierarchy = 'date_recorded'


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'goal_type', 'target_value', 'current_value', 'progress_percentage', 'status', 'target_date']
    list_filter = ['goal_type', 'status', 'target_date']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WaterIntake)
class WaterIntakeAdmin(admin.ModelAdmin):
    list_display = ['user', 'milliliters', 'date_recorded']
    list_filter = ['date_recorded']
    search_fields = ['user__username']
    date_hierarchy = 'date_recorded'


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge_type', 'earned_date']
    list_filter = ['badge_type', 'earned_date']
    search_fields = ['user__username']
    date_hierarchy = 'earned_date'
    readonly_fields = ['earned_date']


@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'meal_type', 'food_name', 'calories', 'protein_g', 'carbs_g', 'fats_g', 'date_logged']
    list_filter = ['meal_type', 'date_logged']
    search_fields = ['user__username', 'food_name']
    date_hierarchy = 'date_logged'
    readonly_fields = ['date_logged']

