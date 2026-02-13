"""
Example integration of fitness calculators with Django models.

This file shows best practices for integrating the utils.py calculations
into your models for automatic computation and caching.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import FitnessCalculator


# Signal to auto-create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a new User is created"""
    if created:
        from .models import UserProfile
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile whenever the User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


# Example: Enhanced methods you can add to your models
class UserProfileMethods:
    """
    Example methods to add to your UserProfile model.
    These demonstrate how to use the FitnessCalculator utilities.
    """
    
    def get_complete_metrics(self):
        """
        Get all calculated fitness metrics for the user.
        Returns a dictionary with BMI, BMR, TDEE, etc.
        """
        if not all([self.weight_kg, self.height_cm, self.date_of_birth]):
            return None
        
        bmi = FitnessCalculator.calculate_bmi(self.weight_kg, self.height_cm)
        age = FitnessCalculator.calculate_age(self.date_of_birth)
        
        bmr = FitnessCalculator.calculate_bmr(
            self.weight_kg,
            self.height_cm,
            age,
            self.gender or 'M'
        )
        
        tdee = FitnessCalculator.calculate_tdee(bmr, self.activity_level)
        
        ideal_weight = FitnessCalculator.calculate_ideal_weight_range(self.height_cm)
        
        water_target = FitnessCalculator.calculate_water_intake_target(
            self.weight_kg,
            self.activity_level
        )
        
        return {
            'bmi': bmi,
            'bmi_category': FitnessCalculator.get_bmi_category(bmi) if bmi else None,
            'age': age,
            'bmr': bmr,
            'tdee': tdee,
            'ideal_weight_min': ideal_weight['min'] if ideal_weight else None,
            'ideal_weight_max': ideal_weight['max'] if ideal_weight else None,
            'water_target_ml': water_target,
        }
    
    def get_recommended_macros(self, goal='MAINTAIN'):
        """Get recommended macro breakdown based on TDEE and goal"""
        metrics = self.get_complete_metrics()
        if not metrics or not metrics['tdee']:
            return None
        
        return FitnessCalculator.calculate_macros(metrics['tdee'], goal)
    
    def is_within_healthy_weight(self):
        """Check if current weight is within healthy BMI range"""
        bmi = self.bmi
        if bmi is None:
            return None
        return 18.5 <= bmi <= 24.9


class ActivityLogMethods:
    """
    Example methods to add to your ActivityLog model.
    """
    
    @classmethod
    def get_weekly_summary(cls, user, start_date=None):
        """
        Get summary of activities for the past week.
        Returns total duration, distance, and calories.
        """
        from datetime import datetime, timedelta
        
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        
        activities = cls.objects.filter(
            user=user,
            date_created__gte=start_date
        )
        
        total_duration = sum(a.duration_minutes for a in activities)
        total_distance = sum(
            float(a.distance_km or 0) for a in activities
        )
        total_calories = sum(a.calories_burned or 0 for a in activities)
        
        return {
            'count': activities.count(),
            'total_duration_minutes': total_duration,
            'total_distance_km': round(total_distance, 2),
            'total_calories_burned': total_calories,
            'average_calories_per_session': (
                total_calories // activities.count() if activities.count() > 0 else 0
            )
        }
    
    def recalculate_calories(self):
        """Recalculate calories burned based on current user weight"""
        if not self.user.profile.weight_kg:
            return None
        
        calories = FitnessCalculator.estimate_calories_burned(
            self.activity_type,
            self.duration_minutes,
            self.user.profile.weight_kg
        )
        return calories


class BiometricsLogMethods:
    """
    Example methods for BiometricsLog model.
    """
    
    @classmethod
    def get_weight_trend(cls, user, days=30):
        """
        Get weight trend for the specified number of days.
        Returns list of weights and average change.
        """
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        logs = cls.objects.filter(
            user=user,
            date_recorded__gte=start_date
        ).order_by('date_recorded')
        
        if logs.count() < 2:
            return None
        
        weights = [float(log.weight_kg) for log in logs]
        first_weight = weights[0]
        last_weight = weights[-1]
        change = last_weight - first_weight
        
        return {
            'logs_count': logs.count(),
            'starting_weight': first_weight,
            'current_weight': last_weight,
            'total_change': round(change, 2),
            'average_daily_change': round(change / days, 3),
            'weights': weights,
        }


class GoalMethods:
    """
    Example methods for Goal model.
    """
    
    def update_progress(self, new_value):
        """Update goal progress and check if achieved"""
        self.current_value = new_value
        
        if self.is_achieved and self.status == 'ACTIVE':
            self.status = 'COMPLETED'
        
        self.save()
        return self.progress_percentage
    
    @classmethod
    def get_active_goals_summary(cls, user):
        """Get summary of all active goals for a user"""
        active_goals = cls.objects.filter(user=user, status='ACTIVE')
        
        return {
            'total_active': active_goals.count(),
            'nearly_complete': active_goals.filter(
                current_value__gte=models.F('target_value') * 0.8
            ).count(),
            'on_track': [
                {
                    'title': goal.title,
                    'progress': goal.progress_percentage,
                    'remaining': float(goal.target_value - goal.current_value)
                }
                for goal in active_goals
            ]
        }


class WaterIntakeMethods:
    """
    Example methods for WaterIntake model.
    """
    
    @classmethod
    def get_today_progress(cls, user):
        """
        Get water intake progress for today.
        Compares actual intake to target.
        """
        from datetime import datetime
        
        today = datetime.now().date()
        total_today = cls.get_daily_total(user, today)
        
        # Get target from user profile
        if hasattr(user, 'profile') and user.profile.weight_kg:
            target = FitnessCalculator.calculate_water_intake_target(
                user.profile.weight_kg,
                user.profile.activity_level
            )
        else:
            target = 2500  # Default 2.5L
        
        percentage = (total_today / target * 100) if target > 0 else 0
        
        return {
            'total_ml': total_today,
            'target_ml': target,
            'percentage': round(percentage, 1),
            'remaining_ml': max(0, target - total_today),
            'goal_met': total_today >= target
        }
    
    @classmethod
    def get_weekly_average(cls, user):
        """Get average daily water intake for the past week"""
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=7)
        logs = cls.objects.filter(
            user=user,
            date_recorded__gte=start_date
        )
        
        # Group by date
        daily_totals = {}
        for log in logs:
            date_key = log.date_recorded.date()
            daily_totals[date_key] = daily_totals.get(date_key, 0) + log.milliliters
        
        if not daily_totals:
            return 0
        
        average = sum(daily_totals.values()) / len(daily_totals)
        return int(round(average))


# Example view integration
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile, ActivityLog, WaterIntake

@login_required
def dashboard(request):
    '''Main dashboard showing fitness metrics'''
    
    # Get user's complete metrics
    metrics = request.user.profile.get_complete_metrics()
    
    # Get activity summary
    activity_summary = ActivityLog.get_weekly_summary(request.user)
    
    # Get water intake progress
    water_progress = WaterIntake.get_today_progress(request.user)
    
    # Get active goals
    goals_summary = Goal.get_active_goals_summary(request.user)
    
    context = {
        'metrics': metrics,
        'activity_summary': activity_summary,
        'water_progress': water_progress,
        'goals_summary': goals_summary,
    }
    
    return render(request, 'dashboard.html', context)
"""


# Example template usage
"""
<!-- In your template -->
{% if metrics %}
<div class="card">
    <h3>Your Fitness Metrics</h3>
    <p>BMI: {{ metrics.bmi }} ({{ metrics.bmi_category }})</p>
    <p>Daily Calorie Needs: {{ metrics.tdee|floatformat:0 }} calories</p>
    <p>Recommended Water: {{ metrics.water_target_ml }}ml ({{ metrics.water_target_ml|divide:1000|floatformat:1 }}L)</p>
    <p>Ideal Weight Range: {{ metrics.ideal_weight_min }}-{{ metrics.ideal_weight_max }} kg</p>
</div>
{% endif %}

{% if water_progress %}
<div class="card">
    <h3>Today's Water Intake</h3>
    <div class="progress-bar" style="width: {{ water_progress.percentage }}%"></div>
    <p>{{ water_progress.total_ml }}ml / {{ water_progress.target_ml }}ml ({{ water_progress.percentage }}%)</p>
    {% if water_progress.goal_met %}
        <span class="badge success">Goal Met! 🎉</span>
    {% else %}
        <span>{{ water_progress.remaining_ml }}ml to go</span>
    {% endif %}
</div>
{% endif %}
"""
