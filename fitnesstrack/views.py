from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
import json
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    UserProfile, 
    ActivityLog, 
    BiometricsLog, 
    Goal, 
    WaterIntake,
    Badge,
    MealLog
)
from .forms import (
    ActivityLogForm,
    BiometricsLogForm,
    WaterIntakeForm,
    GoalForm,
    UserProfileForm,
    MealLogForm
)
from .utils import FitnessCalculator


# ============================================================================
# DASHBOARD VIEW
# ============================================================================

@login_required
def dashboard(request):
    """
    Main dashboard displaying user's fitness metrics and daily summary.
    
    Displays:
    - Current weight and BMI
    - Total calories burned today
    - Water intake progress for today
    - Recent activities
    - Active goals
    - Quick stats
    """
    try:
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Get today's date range
        today = timezone.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_start = timezone.make_aware(today_start)
        
        # Calculate user's fitness metrics
        metrics = {}
        if profile.weight_kg and profile.height_cm:
            metrics['bmi'] = FitnessCalculator.calculate_bmi(
                profile.weight_kg, 
                profile.height_cm
            )
            metrics['bmi_category'] = FitnessCalculator.get_bmi_category(
                metrics['bmi']
            ) if metrics.get('bmi') else None
            
            # Calculate BMR and TDEE if we have enough info
            if profile.date_of_birth:
                age = FitnessCalculator.calculate_age(profile.date_of_birth)
                if age:
                    metrics['age'] = age
                    metrics['bmr'] = FitnessCalculator.calculate_bmr(
                        profile.weight_kg,
                        profile.height_cm,
                        age,
                        profile.gender or 'M'
                    )
                    if metrics.get('bmr'):
                        metrics['tdee'] = FitnessCalculator.calculate_tdee(
                            metrics['bmr'],
                            profile.activity_level
                        )
        
        # Get current weight (most recent biometrics log)
        latest_biometrics = BiometricsLog.objects.filter(
            user=request.user
        ).order_by('-date_recorded').first()
        
        current_weight = latest_biometrics.weight_kg if latest_biometrics else profile.weight_kg
        
        # Calculate total calories burned today
        today_activities = ActivityLog.objects.filter(
            user=request.user,
            date_created__gte=today_start
        )
        total_calories_today = sum(
            activity.calories_burned or 0 for activity in today_activities
        )
        
        # Get water intake for today
        today_water = WaterIntake.objects.filter(
            user=request.user,
            date_recorded__gte=today_start
        )
        total_water_today = sum(log.milliliters for log in today_water)
        
        # Calculate water target
        water_target = 2500  # Default 2.5L
        if profile.weight_kg:
            water_target = FitnessCalculator.calculate_water_intake_target(
                profile.weight_kg,
                profile.activity_level
            ) or 2500
        
        water_percentage = (total_water_today / water_target * 100) if water_target > 0 else 0
        
        # Get recent activities (last 5)
        recent_activities = ActivityLog.objects.filter(
            user=request.user
        ).order_by('-date_created')[:5]
        
        # Get active goals
        active_goals = Goal.objects.filter(
            user=request.user,
            status='ACTIVE'
        ).order_by('-created_at')[:3]
        
        # Weekly summary
        week_ago = timezone.now() - timedelta(days=7)
        weekly_activities = ActivityLog.objects.filter(
            user=request.user,
            date_created__gte=week_ago
        )
        weekly_stats = {
            'total_workouts': weekly_activities.count(),
            'total_calories': sum(a.calories_burned or 0 for a in weekly_activities),
            'total_duration': sum(a.duration_minutes for a in weekly_activities),
        }
        
        # Monthly summary
        month_start = today.replace(day=1)
        month_start_dt = datetime.combine(month_start, datetime.min.time())
        month_start_dt = timezone.make_aware(month_start_dt)
        monthly_activities = ActivityLog.objects.filter(
            user=request.user,
            date_created__gte=month_start_dt
        )
        monthly_workouts_count = monthly_activities.count()
        
        # Convert water intake to glasses (1 glass = 250ml)
        water_glasses = total_water_today // 250
        water_target_glasses = 8  # Standard 8 glasses target
        
        # Get today's nutrition data
        today_meals = MealLog.objects.filter(
            user=request.user,
            date_logged__gte=today_start
        )
        nutrition_data = {
            'calories': sum(meal.calories for meal in today_meals),
            'protein': sum(meal.protein_g for meal in today_meals),
            'carbs': sum(meal.carbs_g for meal in today_meals),
            'fats': sum(meal.fats_g for meal in today_meals),
            'meals_count': today_meals.count()
        }
        
        # Generate daily tip based on yesterday's data
        from .utils import generate_daily_tip
        daily_tip = generate_daily_tip(request.user)
        
        context = {
            'profile': profile,
            'current_weight': current_weight,
            'metrics': metrics,
            'total_calories_today': total_calories_today,
            'today_activities_count': today_activities.count(),
            'total_water_today': total_water_today,
            'water_target': water_target,
            'water_percentage': round(water_percentage, 1),
            'water_glasses': water_glasses,
            'water_target_glasses': water_target_glasses,
            'monthly_workouts_count': monthly_workouts_count,
            'nutrition_data': nutrition_data,
            'recent_activities': recent_activities,
            'active_goals': active_goals,
            'weekly_stats': weekly_stats,
            'daily_tip': daily_tip,
        }
        
        return render(request, 'fitnesstrack/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return render(request, 'fitnesstrack/dashboard.html', {
            'error': 'Unable to load dashboard data. Please try again.'
        })


# ============================================================================
# ACTIVITY LOGGING VIEWS
# ============================================================================

@login_required
def log_activity(request):
    """
    View to log a new activity with automatic calorie calculation.
    
    Accepts: Activity Type, Duration, Distance (optional)
    Auto-calculates: Calories burned based on user's weight
    """
    if request.method == 'POST':
        form = ActivityLogForm(request.POST)
        
        if form.is_valid():
            try:
                # Create activity instance but don't save yet
                activity = form.save(commit=False)
                activity.user = request.user
                
                # Auto-calculate calories burned using utility function
                try:
                    profile = UserProfile.objects.get(user=request.user)
                    if profile.weight_kg:
                        calories = FitnessCalculator.estimate_calories_burned(
                            activity.activity_type,
                            activity.duration_minutes,
                            profile.weight_kg
                        )
                        activity.calories_burned = calories
                    else:
                        # Use default weight if profile weight not set
                        calories = FitnessCalculator.estimate_calories_burned(
                            activity.activity_type,
                            activity.duration_minutes,
                            70  # Default 70kg
                        )
                        activity.calories_burned = calories
                        messages.warning(
                            request, 
                            'Calories calculated using default weight. Please update your profile.'
                        )
                except UserProfile.DoesNotExist:
                    # Create profile and use default weight
                    UserProfile.objects.create(user=request.user)
                    calories = FitnessCalculator.estimate_calories_burned(
                        activity.activity_type,
                        activity.duration_minutes,
                        70  # Default 70kg
                    )
                    activity.calories_burned = calories
                    messages.warning(
                        request,
                        'Profile created. Calories calculated using default weight.'
                    )
                
                # Save the activity
                activity.save()
                
                messages.success(
                    request,
                    f'Activity logged! {activity.calories_burned} calories burned.'
                )
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'Error saving activity: {str(e)}')
                
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ActivityLogForm()
    
    context = {
        'form': form,
        'title': 'Log Activity',
    }
    return render(request, 'fitnesstrack/log_activity.html', context)


@login_required
@require_http_methods(["POST"])
def api_log_activity(request):
    """
    API endpoint to log activity via JSON.
    Accepts: application/json with activity_type, duration, intensity
    Returns: JSON response with activity data
    """
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        activity_type = data.get('activity_type')
        duration = data.get('duration')
        intensity = data.get('intensity', 'Medium')
        
        # Validate required fields
        if not activity_type or not duration:
            return JsonResponse({
                'success': False,
                'error': 'Activity type and duration are required'
            }, status=400)
        
        # Create activity instance
        activity = ActivityLog()
        activity.user = request.user
        activity.activity_type = activity_type
        activity.duration_minutes = int(duration)
        
        # Auto-calculate calories burned
        try:
            profile = UserProfile.objects.get(user=request.user)
            weight = profile.weight_kg if profile.weight_kg else 70  # Default 70kg
        except UserProfile.DoesNotExist:
            weight = 70  # Default weight
        
        calories = FitnessCalculator.estimate_calories_burned(
            activity_type,
            activity.duration_minutes,
            weight
        )
        activity.calories_burned = calories
        
        # Save to database
        activity.save()
        
        # Return success response with activity data
        return JsonResponse({
            'success': True,
            'message': 'Activity logged successfully!',
            'activity': {
                'id': activity.id,
                'activity_type': activity.activity_type,
                'duration_minutes': activity.duration_minutes,
                'calories_burned': float(activity.calories_burned),
                'intensity': intensity,
                'date_created': activity.date_created.strftime('%b %d, %Y')
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def edit_activity(request, pk):
    """Edit an existing activity log"""
    activity = get_object_or_404(ActivityLog, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ActivityLogForm(request.POST, instance=activity)
        
        if form.is_valid():
            try:
                # Recalculate calories if duration or activity type changed
                updated_activity = form.save(commit=False)
                
                try:
                    profile = UserProfile.objects.get(user=request.user)
                    if profile.weight_kg:
                        calories = FitnessCalculator.estimate_calories_burned(
                            updated_activity.activity_type,
                            updated_activity.duration_minutes,
                            profile.weight_kg
                        )
                        updated_activity.calories_burned = calories
                except UserProfile.DoesNotExist:
                    pass
                
                updated_activity.save()
                messages.success(request, 'Activity updated successfully!')
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'Error updating activity: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ActivityLogForm(instance=activity)
    
    context = {
        'form': form,
        'title': 'Edit Activity',
        'activity': activity,
    }
    return render(request, 'fitnesstrack/log_activity.html', context)


@login_required
def delete_activity(request, pk):
    """Delete an activity log"""
    activity = get_object_or_404(ActivityLog, pk=pk, user=request.user)
    
    if request.method == 'POST':
        try:
            activity.delete()
            messages.success(request, 'Activity deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting activity: {str(e)}')
        return redirect('dashboard')
    
    context = {
        'activity': activity,
    }
    return render(request, 'fitnesstrack/delete_activity.html', context)


# ============================================================================
# BIOMETRICS UPDATE VIEWS
# ============================================================================

@login_required
def update_biometrics(request):
    """
    View to update user's biometrics (weight, body composition).
    
    - Creates a new entry in BiometricsLog
    - Updates the main UserProfile with current weight
    - Calculates BMI automatically
    """
    if request.method == 'POST':
        form = BiometricsLogForm(request.POST)
        
        if form.is_valid():
            try:
                # Create biometrics log entry
                biometrics = form.save(commit=False)
                biometrics.user = request.user
                biometrics.save()
                
                # Update user profile with current weight
                try:
                    profile = UserProfile.objects.get(user=request.user)
                    profile.weight_kg = biometrics.weight_kg
                    profile.save()
                    
                    # Calculate and display BMI
                    if profile.height_cm:
                        bmi = FitnessCalculator.calculate_bmi(
                            biometrics.weight_kg,
                            profile.height_cm
                        )
                        if bmi:
                            category = FitnessCalculator.get_bmi_category(bmi)
                            messages.success(
                                request,
                                f'Biometrics updated! Weight: {biometrics.weight_kg}kg | '
                                f'BMI: {bmi} ({category})'
                            )
                        else:
                            messages.success(
                                request,
                                f'Biometrics updated! Weight: {biometrics.weight_kg}kg'
                            )
                    else:
                        messages.success(
                            request,
                            f'Biometrics updated! Add your height to see BMI.'
                        )
                        
                except UserProfile.DoesNotExist:
                    # Create profile if it doesn't exist
                    profile = UserProfile.objects.create(
                        user=request.user,
                        weight_kg=biometrics.weight_kg
                    )
                    messages.success(
                        request,
                        'Profile created and biometrics updated!'
                    )
                
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'Error saving biometrics: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill with current weight if available
        initial_data = {}
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.weight_kg:
                initial_data['weight_kg'] = profile.weight_kg
        except UserProfile.DoesNotExist:
            pass
        
        form = BiometricsLogForm(initial=initial_data)
    
    # Get recent biometrics history
    recent_logs = BiometricsLog.objects.filter(
        user=request.user
    ).order_by('-date_recorded')[:10]
    
    context = {
        'form': form,
        'title': 'Update Biometrics',
        'recent_logs': recent_logs,
    }
    return render(request, 'fitnesstrack/update_biometrics.html', context)


@login_required
def update_profile(request):
    """Update user profile information (height, gender, activity level, etc.)"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'title': 'Update Profile',
        'profile': profile,
    }
    return render(request, 'fitnesstrack/update_profile.html', context)


# ============================================================================
# WATER INTAKE VIEWS
# ============================================================================

@login_required
def log_water(request):
    """Log daily water intake"""
    if request.method == 'POST':
        form = WaterIntakeForm(request.POST)
        
        if form.is_valid():
            try:
                water = form.save(commit=False)
                water.user = request.user
                water.save()
                
                # Calculate today's total
                today = timezone.now().date()
                today_start = datetime.combine(today, datetime.min.time())
                today_start = timezone.make_aware(today_start)
                
                today_total = WaterIntake.objects.filter(
                    user=request.user,
                    date_recorded__gte=today_start
                ).aggregate(total=Sum('milliliters'))['total'] or 0
                
                messages.success(
                    request,
                    f'{water.milliliters}ml logged! Today\'s total: {today_total}ml'
                )
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'Error logging water: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WaterIntakeForm()
    
    context = {
        'form': form,
        'title': 'Log Water Intake',
    }
    return render(request, 'fitnesstrack/log_water.html', context)


@login_required
@require_http_methods(["POST"])
def log_water_quick(request):
    """Quick water logging endpoint for AJAX requests"""
    try:
        data = json.loads(request.body)
        milliliters = data.get('milliliters', 250)  # Default 1 glass = 250ml
        
        # Create water intake log
        water = WaterIntake.objects.create(
            user=request.user,
            milliliters=milliliters,
            date_recorded=timezone.now()
        )
        
        # Calculate today's total
        today = timezone.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_start = timezone.make_aware(today_start)
        
        today_total = WaterIntake.objects.filter(
            user=request.user,
            date_recorded__gte=today_start
        ).aggregate(total=Sum('milliliters'))['total'] or 0
        
        # Convert to glasses
        water_glasses = today_total // 250
        water_target_glasses = 8
        
        return JsonResponse({
            'success': True,
            'message': f'Logged {milliliters}ml of water!',
            'total_ml': today_total,
            'water_glasses': water_glasses,
            'water_target_glasses': water_target_glasses,
            'percentage': round((water_glasses / water_target_glasses * 100), 1)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def log_meal_quick(request):
    """Quick meal logging endpoint for AJAX requests"""
    try:
        data = json.loads(request.body)
        
        # Create meal log
        meal = MealLog.objects.create(
            user=request.user,
            meal_type=data.get('meal_type', 'SNACK'),
            food_name=data.get('food_name'),
            calories=data.get('calories', 0),
            protein_g=data.get('protein_g', 0),
            carbs_g=data.get('carbs_g', 0),
            fats_g=data.get('fats_g', 0),
            serving_size=data.get('serving_size', ''),
            date_logged=timezone.now()
        )
        
        # Calculate today's totals
        today = timezone.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_start = timezone.make_aware(today_start)
        
        today_meals = MealLog.objects.filter(
            user=request.user,
            date_logged__gte=today_start
        )
        
        totals = {
            'calories': sum(m.calories for m in today_meals),
            'protein': float(sum(m.protein_g for m in today_meals)),
            'carbs': float(sum(m.carbs_g for m in today_meals)),
            'fats': float(sum(m.fats_g for m in today_meals)),
        }
        
        return JsonResponse({
            'success': True,
            'message': f'Logged {meal.food_name}!',
            'totals': totals
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ============================================================================
# ACTIVITY LIST VIEWS (Class-Based)
# ============================================================================

class ActivityListView(LoginRequiredMixin, ListView):
    """Display list of all activities for the logged-in user"""
    model = ActivityLog
    template_name = 'fitnesstrack/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 20
    
    def get_queryset(self):
        """Filter activities for current user"""
        return ActivityLog.objects.filter(
            user=self.request.user
        ).order_by('-date_created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add summary statistics
        activities = self.get_queryset()
        context['total_activities'] = activities.count()
        context['total_calories'] = sum(
            a.calories_burned or 0 for a in activities
        )
        context['total_duration'] = sum(
            a.duration_minutes for a in activities
        )
        
        return context


class BiometricsListView(LoginRequiredMixin, ListView):
    """Display biometrics history"""
    model = BiometricsLog
    template_name = 'fitnesstrack/biometrics_list.html'
    context_object_name = 'biometrics'
    paginate_by = 20
    
    def get_queryset(self):
        return BiometricsLog.objects.filter(
            user=self.request.user
        ).order_by('-date_recorded')


# ============================================================================
# LEGACY VIEWS (for compatibility)
# ============================================================================

def fit_list(request):
    """Legacy view - redirects to activity list"""
    return redirect('activity_list')


def fit_detail(request, pk):
    """Display activity detail"""
    activity = get_object_or_404(ActivityLog, pk=pk)
    
    # Check if user owns this activity
    if request.user.is_authenticated and activity.user != request.user:
        messages.error(request, 'You do not have permission to view this activity.')
        return redirect('dashboard')
    
    context = {
        'activity': activity,
    }
    return render(request, 'fitnesstrack/activity_detail.html', context)


@login_required
def fit_form(request, pk=None):
    """Legacy form view - redirects to appropriate view"""
    if pk:
        return redirect('edit_activity', pk=pk)
    return redirect('log_activity')


def fit_confirm_delete(request, pk):
    """Legacy delete view"""
    return delete_activity(request, pk)


# ============================================================================
# PROGRESS & CHARTS VIEWS
# ============================================================================

@login_required
def progress_charts(request):
    """
    Progress visualization page with charts for weight trend and activity breakdown.
    Prepares data for Chart.js visualizations.
    """
    from collections import defaultdict
    import json
    
    try:
        # ========================================
        # WEIGHT TREND DATA (Last 30 Days)
        # ========================================
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Get biometrics logs for last 30 days
        biometrics = BiometricsLog.objects.filter(
            user=request.user,
            date_recorded__gte=thirty_days_ago
        ).order_by('date_recorded')
        
        # Prepare data for line chart
        weight_dates = []
        weight_values = []
        
        for entry in biometrics:
            weight_dates.append(entry.date_recorded.strftime('%Y-%m-%d'))
            weight_values.append(float(entry.weight_kg))
        
        # If no data, add current weight from profile
        if not weight_values:
            try:
                profile = UserProfile.objects.get(user=request.user)
                if profile.weight_kg:
                    today = timezone.now().strftime('%Y-%m-%d')
                    weight_dates.append(today)
                    weight_values.append(float(profile.weight_kg))
            except UserProfile.DoesNotExist:
                pass
        
        weight_chart_data = {
            'labels': weight_dates,
            'values': weight_values
        }
        
        # ========================================
        # ACTIVITY BREAKDOWN DATA (All Time)
        # ========================================
        
        # Count activities by type
        activity_counts = defaultdict(int)
        activities = ActivityLog.objects.filter(user=request.user)
        
        for activity in activities:
            activity_type = activity.get_activity_type_display()
            activity_counts[activity_type] += 1
        
        # Prepare data for pie chart
        activity_labels = list(activity_counts.keys())
        activity_values = list(activity_counts.values())
        
        activity_chart_data = {
            'labels': activity_labels,
            'values': activity_values
        }
        
        # ========================================
        # CALORIES BURNED TREND (Last 7 Days)
        # ========================================
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        # Group activities by day
        daily_calories = defaultdict(int)
        recent_activities = ActivityLog.objects.filter(
            user=request.user,
            date_created__gte=seven_days_ago
        )
        
        for activity in recent_activities:
            date_key = activity.date_created.strftime('%Y-%m-%d')
            daily_calories[date_key] += activity.calories_burned or 0
        
        # Create complete 7-day range
        calories_dates = []
        calories_values = []
        for i in range(7):
            date = (timezone.now() - timedelta(days=6-i)).date()
            date_str = date.strftime('%Y-%m-%d')
            calories_dates.append(date_str)
            calories_values.append(daily_calories.get(date_str, 0))
        
        calories_chart_data = {
            'labels': calories_dates,
            'values': calories_values
        }
        
        # ========================================
        # STATISTICS SUMMARY
        # ========================================
        
        # Total statistics
        total_activities = activities.count()
        total_calories = sum(a.calories_burned or 0 for a in activities)
        total_duration = sum(a.duration_minutes for a in activities)
        
        # This week stats
        week_ago = timezone.now() - timedelta(days=7)
        week_activities = activities.filter(date_created__gte=week_ago)
        week_calories = sum(a.calories_burned or 0 for a in week_activities)
        
        # Weight change (if we have data)
        weight_change = None
        if len(weight_values) >= 2:
            weight_change = round(weight_values[-1] - weight_values[0], 2)
        
        stats = {
            'total_activities': total_activities,
            'total_calories': total_calories,
            'total_duration': total_duration,
            'week_calories': week_calories,
            'weight_change': weight_change,
        }
        
        context = {
            'weight_chart_data': json.dumps(weight_chart_data),
            'activity_chart_data': json.dumps(activity_chart_data),
            'calories_chart_data': json.dumps(calories_chart_data),
            'stats': stats,
        }
        
        return render(request, 'fitnesstrack/progress_charts.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading charts: {str(e)}')
        return render(request, 'fitnesstrack/progress_charts.html', {
            'error': 'Unable to load chart data.'
        })


@login_required
def badges_view(request):
    """
    Display user's earned badges and progress towards new badges.
    Checks and awards any new badges.
    """
    from .badge_system import BadgeChecker
    from .models import Badge
    
    try:
        # Check and award any new badges
        badge_results = BadgeChecker.check_all_badges(request.user)
        
        # Show messages for newly awarded badges
        for badge_type in badge_results['badges_awarded']:
            badge = Badge.objects.get(user=request.user, badge_type=badge_type)
            messages.success(
                request,
                f'🏆 New Badge Earned: {badge.get_badge_type_display()}! {badge.description}'
            )
        
        # Get all user's badges
        earned_badges = BadgeChecker.get_user_badges(request.user)
        
        # Get progress towards unearned badges
        badge_progress = BadgeChecker.get_badge_progress(request.user)
        
        # Get current streak
        current_streak = badge_results['current_streak']
        
        context = {
            'earned_badges': earned_badges,
            'badge_progress': badge_progress,
            'current_streak': current_streak,
            'total_badges': badge_results['total_badges'],
            'newly_awarded': badge_results['badges_awarded'],
        }
        
        return render(request, 'fitnesstrack/badges.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading badges: {str(e)}')
        return render(request, 'fitnesstrack/badges.html', {
            'error': 'Unable to load badge data.'
        })


# ============================================================================
# USER REGISTRATION
# ============================================================================

def register(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to FitTrack!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'fitnesstrack/register.html', {'form': form})
