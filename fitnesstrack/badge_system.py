"""
Badge System for Fitness Tracker

This module contains logic for checking achievements and awarding badges
to users based on their fitness activities.
"""

from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta


class BadgeChecker:
    """
    Checks user activities and awards badges for achievements.
    """
    
    @staticmethod
    def check_consistency_badge(user):
        """
        Check if user has logged activities for 7 consecutive days.
        Awards 'CONSISTENCY_7' badge if achieved.
        
        Args:
            user: User object
            
        Returns:
            tuple: (badge_awarded: bool, days_streak: int)
        """
        from .models import ActivityLog, Badge
        
        # Check if user already has this badge
        if Badge.objects.filter(user=user, badge_type='CONSISTENCY_7').exists():
            # Already has badge, return current streak
            streak = BadgeChecker._calculate_current_streak(user)
            return False, streak
        
        # Calculate current streak
        streak = BadgeChecker._calculate_current_streak(user)
        
        # Award badge if 7+ day streak
        if streak >= 7:
            badge = Badge.objects.create(
                user=user,
                badge_type='CONSISTENCY_7',
                description=f'Logged activities for {streak} consecutive days!'
            )
            return True, streak
        else:
            return False, streak
    
    @staticmethod
    def _calculate_current_streak(user):
        """
        Calculate the current consecutive days streak for a user.
        
        Args:
            user: User object
            
        Returns:
            int: Number of consecutive days with activities
        """
        from .models import ActivityLog
        
        today = timezone.now().date()
        
        # Check backwards from today
        streak = 0
        check_date = today
        
        while True:
            # Check if user has activity on this date
            has_activity = ActivityLog.objects.filter(
                user=user,
                date_created__date=check_date
            ).exists()
            
            if has_activity:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                # Streak broken
                break
            
            # Safety limit to prevent infinite loop
            if streak > 365:
                break
        
        return streak
    
    @staticmethod
    def check_30_day_consistency(user):
        """
        Check if user has logged activities for 30 consecutive days.
        
        Args:
            user: User object
            
        Returns:
            tuple: (badge_awarded: bool, days_streak: int)
        """
        from .models import Badge
        
        if Badge.objects.filter(user=user, badge_type='CONSISTENCY_30').exists():
            streak = BadgeChecker._calculate_current_streak(user)
            return False, streak
        
        streak = BadgeChecker._calculate_current_streak(user)
        
        if streak >= 30:
            Badge.objects.create(
                user=user,
                badge_type='CONSISTENCY_30',
                description=f'Amazing! {streak} consecutive days of activities!'
            )
            return True, streak
        else:
            return False, streak
    
    @staticmethod
    def check_first_workout_badge(user):
        """
        Award badge for logging first workout.
        
        Returns:
            bool: True if badge awarded
        """
        from .models import ActivityLog, Badge
        
        # Check if already has badge
        if Badge.objects.filter(user=user, badge_type='FIRST_WORKOUT').exists():
            return False
        
        # Check if user has at least one activity
        if ActivityLog.objects.filter(user=user).exists():
            Badge.objects.create(
                user=user,
                badge_type='FIRST_WORKOUT',
                description='Started your fitness journey!'
            )
            return True
        
        return False
    
    @staticmethod
    def check_calorie_burner_badges(user):
        """
        Check total calories burned and award badges.
        
        Returns:
            list: Badges awarded
        """
        from .models import ActivityLog, Badge
        
        # Calculate total calories burned
        total_calories = ActivityLog.objects.filter(user=user).aggregate(
            total=Sum('calories_burned')
        )['total'] or 0
        
        badges_awarded = []
        
        # Check 1000 calorie badge
        if (total_calories >= 1000 and 
            not Badge.objects.filter(user=user, badge_type='CALORIE_BURNER_1000').exists()):
            Badge.objects.create(
                user=user,
                badge_type='CALORIE_BURNER_1000',
                description=f'Burned {total_calories} total calories!'
            )
            badges_awarded.append('CALORIE_BURNER_1000')
        
        # Check 5000 calorie badge
        if (total_calories >= 5000 and 
            not Badge.objects.filter(user=user, badge_type='CALORIE_BURNER_5000').exists()):
            Badge.objects.create(
                user=user,
                badge_type='CALORIE_BURNER_5000',
                description=f'Amazing! Burned {total_calories} total calories!'
            )
            badges_awarded.append('CALORIE_BURNER_5000')
        
        return badges_awarded
    
    @staticmethod
    def check_early_bird_badge(user):
        """
        Check if user has logged an activity before 7 AM.
        
        Returns:
            bool: True if badge awarded
        """
        from .models import ActivityLog, Badge
        
        # Check if already has badge
        if Badge.objects.filter(user=user, badge_type='EARLY_BIRD').exists():
            return False
        
        # Check for activities before 7 AM
        early_activities = ActivityLog.objects.filter(
            user=user,
            date_created__hour__lt=7
        )
        
        if early_activities.exists():
            Badge.objects.create(
                user=user,
                badge_type='EARLY_BIRD',
                description='Worked out before 7 AM!'
            )
            return True
        
        return False
    
    @staticmethod
    def check_hydration_badge(user):
        """
        Check if user has met water intake goal for 7 consecutive days.
        
        Returns:
            bool: True if badge awarded
        """
        from .models import WaterIntake, Badge, UserProfile
        from .utils import FitnessCalculator
        
        # Check if already has badge
        if Badge.objects.filter(user=user, badge_type='HYDRATION_MASTER').exists():
            return False
        
        # Get user's water intake target
        try:
            profile = UserProfile.objects.get(user=user)
            target = FitnessCalculator.calculate_water_intake_target(
                profile.weight_kg,
                profile.activity_level
            ) or 2500
        except:
            target = 2500
        
        # Check last 7 days
        check_date = timezone.now().date()
        consecutive_days = 0
        
        for i in range(7):
            day_total = WaterIntake.get_daily_total(user, check_date)
            if day_total >= target:
                consecutive_days += 1
            else:
                break
            check_date -= timedelta(days=1)
        
        if consecutive_days >= 7:
            Badge.objects.create(
                user=user,
                badge_type='HYDRATION_MASTER',
                description='Met water intake goal for 7 days straight!'
            )
            return True
        
        return False
    
    @staticmethod
    def check_all_badges(user):
        """
        Check all badge conditions and award any earned badges.
        
        Args:
            user: User object
            
        Returns:
            dict: Summary of badges checked and awarded
        """
        results = {
            'badges_awarded': [],
            'current_streak': 0,
            'total_badges': 0
        }
        
        # Check first workout
        if BadgeChecker.check_first_workout_badge(user):
            results['badges_awarded'].append('FIRST_WORKOUT')
        
        # Check consistency badges
        awarded_7, streak = BadgeChecker.check_consistency_badge(user)
        if awarded_7:
            results['badges_awarded'].append('CONSISTENCY_7')
        results['current_streak'] = streak
        
        awarded_30, _ = BadgeChecker.check_30_day_consistency(user)
        if awarded_30:
            results['badges_awarded'].append('CONSISTENCY_30')
        
        # Check calorie badges
        calorie_badges = BadgeChecker.check_calorie_burner_badges(user)
        results['badges_awarded'].extend(calorie_badges)
        
        # Check early bird
        if BadgeChecker.check_early_bird_badge(user):
            results['badges_awarded'].append('EARLY_BIRD')
        
        # Check hydration
        if BadgeChecker.check_hydration_badge(user):
            results['badges_awarded'].append('HYDRATION_MASTER')
        
        # Get total badges
        from .models import Badge
        results['total_badges'] = Badge.objects.filter(user=user).count()
        
        return results
    
    @staticmethod
    def get_user_badges(user):
        """
        Get all badges earned by a user.
        
        Args:
            user: User object
            
        Returns:
            QuerySet: Badge objects
        """
        from .models import Badge
        return Badge.objects.filter(user=user).order_by('-earned_date')
    
    @staticmethod
    def get_badge_progress(user):
        """
        Get progress towards unearned badges.
        
        Args:
            user: User object
            
        Returns:
            dict: Progress information for each badge type
        """
        from .models import Badge, ActivityLog
        
        # Get list of earned badge types
        earned_badges = set(
            Badge.objects.filter(user=user).values_list('badge_type', flat=True)
        )
        
        progress = {}
        
        # Consistency badges
        if 'CONSISTENCY_7' not in earned_badges:
            streak = BadgeChecker._calculate_current_streak(user)
            progress['consistency_7'] = {
                'current': streak,
                'required': 7,
                'percentage': min(100, int(streak / 7 * 100))
            }
        
        if 'CONSISTENCY_30' not in earned_badges:
            streak = BadgeChecker._calculate_current_streak(user)
            progress['consistency_30'] = {
                'current': streak,
                'required': 30,
                'percentage': min(100, int(streak / 30 * 100))
            }
        
        # Calorie badges
        total_calories = ActivityLog.objects.filter(user=user).aggregate(
            total=Sum('calories_burned')
        )['total'] or 0
        
        if 'CALORIE_BURNER_1000' not in earned_badges:
            progress['calorie_burner_1000'] = {
                'current': total_calories,
                'required': 1000,
                'percentage': min(100, int(total_calories / 1000 * 100))
            }
        
        if 'CALORIE_BURNER_5000' not in earned_badges:
            progress['calorie_burner_5000'] = {
                'current': total_calories,
                'required': 5000,
                'percentage': min(100, int(total_calories / 5000 * 100))
            }
        
        return progress
