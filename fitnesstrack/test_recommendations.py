"""
Test suite for recommendation engine (generate_daily_tip function).

Tests all three recommendation conditions:
- Water intake < 2000ml
- Sleep < 7 hours (placeholder for future feature)
- Calories burned > 500
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from fitnesstrack.models import UserProfile, ActivityLog, WaterIntake
from fitnesstrack.utils import generate_daily_tip


class RecommendationEngineTestCase(TestCase):
    """Test cases for the recommendation engine"""
    
    def setUp(self):
        """Create test user and profile"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            height_cm=175,
            weight_kg=70,
            gender='M',
            date_of_birth='1990-01-01',
            activity_level='ACTIVE'
        )
        self.yesterday = timezone.now().date() - timedelta(days=1)
    
    def test_hydration_alert_low_water(self):
        """Test hydration alert when water intake is below 2000ml"""
        # Log low water intake for yesterday
        yesterday_time = timezone.make_aware(
            timezone.datetime.combine(self.yesterday, timezone.datetime.min.time())
        )
        
        WaterIntake.objects.create(
            user=self.user,
            milliliters=1500,  # Below 2000ml threshold
            date_recorded=yesterday_time
        )
        
        # Get tip
        tip = generate_daily_tip(self.user)
        
        # Should return hydration alert
        self.assertEqual(tip, 'Hydration Alert: Try to drink more water today.')
    
    def test_no_hydration_alert_good_water(self):
        """Test no hydration alert when water intake is sufficient"""
        # Log good water intake for yesterday
        yesterday_time = timezone.make_aware(
            timezone.datetime.combine(self.yesterday, timezone.datetime.min.time())
        )
        
        WaterIntake.objects.create(
            user=self.user,
            milliliters=2500,  # Above 2000ml threshold
            date_recorded=yesterday_time
        )
        
        # Get tip
        tip = generate_daily_tip(self.user)
        
        # Should NOT return hydration alert
        self.assertNotEqual(tip, 'Hydration Alert: Try to drink more water today.')
    
    def test_high_calorie_burn_encouragement(self):
        """Test encouragement message when calories burned > 500"""
        # Log high calorie activity for yesterday
        yesterday_time = timezone.make_aware(
            timezone.datetime.combine(self.yesterday, timezone.datetime.min.time())
        )
        
        # Log good water first (to skip hydration alert)
        WaterIntake.objects.create(
            user=self.user,
            milliliters=2500,
            date_recorded=yesterday_time
        )
        
        # Log high-calorie activity
        ActivityLog.objects.create(
            user=self.user,
            activity_type='RUNNING',
            duration_minutes=60,
            calories_burned=600,  # Above 500 threshold
            date_created=yesterday_time
        )
        
        # Get tip
        tip = generate_daily_tip(self.user)
        
        # Should return encouragement
        self.assertEqual(tip, 'Great work! You hit a high burn yesterday.')
    
    def test_default_motivational_message(self):
        """Test default message when no specific conditions are met"""
        # Log good water intake
        yesterday_time = timezone.make_aware(
            timezone.datetime.combine(self.yesterday, timezone.datetime.min.time())
        )
        
        WaterIntake.objects.create(
            user=self.user,
            milliliters=2500,
            date_recorded=yesterday_time
        )
        
        # Log low-calorie activity
        ActivityLog.objects.create(
            user=self.user,
            activity_type='YOGA',
            duration_minutes=30,
            calories_burned=150,  # Below 500 threshold
            date_created=yesterday_time
        )
        
        # Get tip
        tip = generate_daily_tip(self.user)
        
        # Should return default motivational message
        self.assertEqual(tip, 'Keep up the great work! Stay consistent with your fitness journey.')
    
    def test_no_data_returns_hydration_alert(self):
        """Test hydration alert when user has no yesterday data (0ml water)"""
        # Don't log any data for yesterday
        
        # Get tip
        tip = generate_daily_tip(self.user)
        
        # Should return hydration alert since 0ml < 2000ml
        self.assertEqual(tip, 'Hydration Alert: Try to drink more water today.')
    
    def test_priority_hydration_over_calories(self):
        """Test that hydration alert takes priority over calorie encouragement"""
        # Log low water AND high calories for yesterday
        yesterday_time = timezone.make_aware(
            timezone.datetime.combine(self.yesterday, timezone.datetime.min.time())
        )
        
        # Low water
        WaterIntake.objects.create(
            user=self.user,
            milliliters=1000,
            date_recorded=yesterday_time
        )
        
        # High calories
        ActivityLog.objects.create(
            user=self.user,
            activity_type='RUNNING',
            duration_minutes=60,
            calories_burned=700,
            date_created=yesterday_time
        )
        
        # Get tip
        tip = generate_daily_tip(self.user)
        
        # Should prioritize hydration alert
        self.assertEqual(tip, 'Hydration Alert: Try to drink more water today.')
    
    def test_multiple_activities_calorie_sum(self):
        """Test that multiple activities are summed for calorie check"""
        # Log good water first
        yesterday_time = timezone.make_aware(
            timezone.datetime.combine(self.yesterday, timezone.datetime.min.time())
        )
        
        WaterIntake.objects.create(
            user=self.user,
            milliliters=2500,
            date_recorded=yesterday_time
        )
        
        # Log multiple low-calorie activities that sum to > 500
        ActivityLog.objects.create(
            user=self.user,
            activity_type='WALKING',
            duration_minutes=30,
            calories_burned=200,
            date_created=yesterday_time
        )
        
        ActivityLog.objects.create(
            user=self.user,
            activity_type='YOGA',
            duration_minutes=30,
            calories_burned=150,
            date_created=yesterday_time
        )
        
        ActivityLog.objects.create(
            user=self.user,
            activity_type='CYCLING',
            duration_minutes=20,
            calories_burned=200,
            date_created=yesterday_time
        )
        
        # Total: 550 calories (> 500)
        
        # Get tip
        tip = generate_daily_tip(self.user)
        
        # Should return encouragement for high total burn
        self.assertEqual(tip, 'Great work! You hit a high burn yesterday.')
    
    def test_function_handles_no_profile(self):
        """Test function doesn't crash when user has no profile"""
        # Create user without profile
        user_no_profile = User.objects.create_user(
            username='noprofile',
            password='testpass123'
        )
        
        # Get tip (should not crash)
        tip = generate_daily_tip(user_no_profile)
        
        # Should return some message (likely default)
        self.assertIsNotNone(tip)
        self.assertIsInstance(tip, str)


# Run tests with:
# python manage.py test fitnesstrack.test_recommendations --verbosity=2
