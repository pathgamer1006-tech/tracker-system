"""
Test suite for Progress Charts and Badge System features.

This module contains tests for:
- Progress chart data preparation
- Badge awarding logic
- Streak calculations
- Badge progress tracking
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from fitnesstrack.models import (
    UserProfile, ActivityLog, BiometricsLog, 
    WaterIntake, Goal, Badge
)
from fitnesstrack.badge_system import BadgeChecker


class BadgeSystemTestCase(TestCase):
    """Test cases for badge awarding system"""
    
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
    
    def test_first_workout_badge(self):
        """Test first workout badge is awarded"""
        # Initially no badges
        self.assertEqual(Badge.objects.filter(user=self.user).count(), 0)
        
        # Log first activity
        ActivityLog.objects.create(
            user=self.user,
            activity_type='RUNNING',
            duration_minutes=30,
            distance_km=5.0
        )
        
        # Check badge
        awarded = BadgeChecker.check_first_workout_badge(self.user)
        self.assertTrue(awarded)
        
        # Verify badge created
        self.assertTrue(
            Badge.objects.filter(
                user=self.user,
                badge_type='FIRST_WORKOUT'
            ).exists()
        )
    
    def test_streak_calculation(self):
        """Test consecutive day streak calculation"""
        today = timezone.now().date()
        
        # Create activities for last 5 days
        for i in range(5):
            date = today - timedelta(days=i)
            ActivityLog.objects.create(
                user=self.user,
                activity_type='RUNNING',
                duration_minutes=30,
                date_created=timezone.make_aware(
                    timezone.datetime.combine(date, timezone.datetime.min.time())
                )
            )
        
        # Calculate streak
        streak = BadgeChecker._calculate_current_streak(self.user)
        self.assertEqual(streak, 5)
    
    def test_7_day_consistency_badge(self):
        """Test 7-day consistency badge is awarded"""
        today = timezone.now().date()
        
        # Create activities for last 7 days
        for i in range(7):
            date = today - timedelta(days=i)
            ActivityLog.objects.create(
                user=self.user,
                activity_type='CYCLING',
                duration_minutes=20,
                date_created=timezone.make_aware(
                    timezone.datetime.combine(date, timezone.datetime.min.time())
                )
            )
        
        # Check badge
        awarded, streak = BadgeChecker.check_consistency_badge(self.user)
        self.assertTrue(awarded)
        self.assertEqual(streak, 7)
        
        # Verify badge created
        self.assertTrue(
            Badge.objects.filter(
                user=self.user,
                badge_type='CONSISTENCY_7'
            ).exists()
        )
    
    def test_broken_streak(self):
        """Test streak calculation with gap in activities"""
        today = timezone.now().date()
        
        # Day 0 (today): Activity
        ActivityLog.objects.create(
            user=self.user,
            activity_type='RUNNING',
            duration_minutes=30,
            date_created=timezone.now()
        )
        
        # Day 1: Activity
        ActivityLog.objects.create(
            user=self.user,
            activity_type='CYCLING',
            duration_minutes=30,
            date_created=timezone.now() - timedelta(days=1)
        )
        
        # Day 2: NO ACTIVITY (gap)
        
        # Day 3: Activity (shouldn't count)
        ActivityLog.objects.create(
            user=self.user,
            activity_type='SWIMMING',
            duration_minutes=30,
            date_created=timezone.now() - timedelta(days=3)
        )
        
        # Streak should be 2 (today and yesterday)
        streak = BadgeChecker._calculate_current_streak(self.user)
        self.assertEqual(streak, 2)
    
    def test_calorie_burner_1000_badge(self):
        """Test 1000 calorie badge is awarded"""
        # Create activities totaling over 1000 calories
        ActivityLog.objects.create(
            user=self.user,
            activity_type='RUNNING',
            duration_minutes=60,
            calories_burned=600
        )
        ActivityLog.objects.create(
            user=self.user,
            activity_type='CYCLING',
            duration_minutes=60,
            calories_burned=500
        )
        
        # Check badge
        badges = BadgeChecker.check_calorie_burner_badges(self.user)
        self.assertIn('CALORIE_BURNER_1000', badges)
        
        # Verify badge created
        self.assertTrue(
            Badge.objects.filter(
                user=self.user,
                badge_type='CALORIE_BURNER_1000'
            ).exists()
        )
    
    def test_early_bird_badge(self):
        """Test early bird badge for workout before 7 AM"""
        # Create activity at 6:30 AM
        early_morning = timezone.now().replace(hour=6, minute=30)
        ActivityLog.objects.create(
            user=self.user,
            activity_type='YOGA',
            duration_minutes=30,
            date_created=early_morning
        )
        
        # Check badge
        awarded = BadgeChecker.check_early_bird_badge(self.user)
        self.assertTrue(awarded)
        
        # Verify badge created
        self.assertTrue(
            Badge.objects.filter(
                user=self.user,
                badge_type='EARLY_BIRD'
            ).exists()
        )
    
    def test_badge_progress_tracking(self):
        """Test progress tracking for unearned badges"""
        # Create 3-day streak
        today = timezone.now().date()
        for i in range(3):
            date = today - timedelta(days=i)
            ActivityLog.objects.create(
                user=self.user,
                activity_type='RUNNING',
                duration_minutes=30,
                date_created=timezone.make_aware(
                    timezone.datetime.combine(date, timezone.datetime.min.time())
                )
            )
        
        # Get progress
        progress = BadgeChecker.get_badge_progress(self.user)
        
        # Check 7-day consistency progress
        self.assertIn('consistency_7', progress)
        self.assertEqual(progress['consistency_7']['current'], 3)
        self.assertEqual(progress['consistency_7']['required'], 7)
        self.assertAlmostEqual(progress['consistency_7']['percentage'], 42.86, places=1)
    
    def test_check_all_badges(self):
        """Test master badge checking function"""
        # Create sufficient data
        today = timezone.now().date()
        for i in range(5):
            date = today - timedelta(days=i)
            ActivityLog.objects.create(
                user=self.user,
                activity_type='RUNNING',
                duration_minutes=30,
                calories_burned=300,
                date_created=timezone.make_aware(
                    timezone.datetime.combine(date, timezone.datetime.min.time())
                )
            )
        
        # Check all badges
        results = BadgeChecker.check_all_badges(self.user)
        
        # Verify structure
        self.assertIn('badges_awarded', results)
        self.assertIn('current_streak', results)
        self.assertIn('total_badges', results)
        
        # Verify first workout badge awarded
        self.assertIn('FIRST_WORKOUT', results['badges_awarded'])
        
        # Verify streak calculated
        self.assertEqual(results['current_streak'], 5)
    
    def test_badge_unique_constraint(self):
        """Test that same badge can't be awarded twice"""
        # Award first workout badge
        Badge.objects.create(
            user=self.user,
            badge_type='FIRST_WORKOUT',
            description='First workout completed'
        )
        
        # Try to check again (should return False)
        awarded = BadgeChecker.check_first_workout_badge(self.user)
        self.assertFalse(awarded)
        
        # Verify only one badge exists
        self.assertEqual(
            Badge.objects.filter(
                user=self.user,
                badge_type='FIRST_WORKOUT'
            ).count(),
            1
        )
    
    def test_badge_icon_property(self):
        """Test badge icon property returns correct emoji"""
        badge = Badge.objects.create(
            user=self.user,
            badge_type='CONSISTENCY_7',
            description='7-day streak!'
        )
        
        # Check icon
        self.assertEqual(badge.icon, '🔥')


class ProgressChartsTestCase(TestCase):
    """Test cases for progress charts data preparation"""
    
    def setUp(self):
        """Create test user and client"""
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
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_progress_charts_view_loads(self):
        """Test progress charts page loads successfully"""
        response = self.client.get('/progress/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fitnesstrack/progress_charts.html')
    
    def test_weight_chart_data(self):
        """Test weight chart data preparation"""
        # Create weight logs
        today = timezone.now()
        for i in range(10):
            date = today - timedelta(days=i)
            BiometricsLog.objects.create(
                user=self.user,
                weight_kg=70 + (i * 0.5),  # Gradually increasing
                date_recorded=date
            )
        
        # Get page
        response = self.client.get('/progress/')
        
        # Check weight data in context
        self.assertIn('weight_chart_data', response.context)
        weight_data = response.context['weight_chart_data']
        
        # Verify structure
        self.assertIn('labels', weight_data)
        self.assertIn('values', weight_data)
        self.assertGreater(len(weight_data['labels']), 0)
        self.assertGreater(len(weight_data['values']), 0)
    
    def test_activity_chart_data(self):
        """Test activity distribution chart data"""
        # Create varied activities
        ActivityLog.objects.create(
            user=self.user,
            activity_type='RUNNING',
            duration_minutes=30
        )
        ActivityLog.objects.create(
            user=self.user,
            activity_type='RUNNING',
            duration_minutes=20
        )
        ActivityLog.objects.create(
            user=self.user,
            activity_type='CYCLING',
            duration_minutes=40
        )
        
        # Get page
        response = self.client.get('/progress/')
        
        # Check activity data in context
        self.assertIn('activity_chart_data', response.context)
        activity_data = response.context['activity_chart_data']
        
        # Verify structure
        self.assertIn('labels', activity_data)
        self.assertIn('values', activity_data)
        
        # Verify data (2 Running, 1 Cycling)
        if 'Running' in activity_data['labels']:
            running_index = activity_data['labels'].index('Running')
            self.assertEqual(activity_data['values'][running_index], 2)
    
    def test_badges_view_loads(self):
        """Test badges page loads successfully"""
        response = self.client.get('/badges/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fitnesstrack/badges.html')
    
    def test_badges_view_context(self):
        """Test badges view provides correct context"""
        # Create some activities and badges
        ActivityLog.objects.create(
            user=self.user,
            activity_type='RUNNING',
            duration_minutes=30
        )
        
        Badge.objects.create(
            user=self.user,
            badge_type='FIRST_WORKOUT',
            description='First workout!'
        )
        
        # Get page
        response = self.client.get('/badges/')
        
        # Check context
        self.assertIn('earned_badges', response.context)
        self.assertIn('badge_progress', response.context)
        self.assertIn('current_streak', response.context)
        self.assertIn('total_badges', response.context)
        
        # Verify earned badge
        earned = response.context['earned_badges']
        self.assertEqual(earned.count(), 1)


class BadgeModelTestCase(TestCase):
    """Test cases for Badge model"""
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_badge_creation(self):
        """Test badge can be created"""
        badge = Badge.objects.create(
            user=self.user,
            badge_type='CONSISTENCY_7',
            description='Logged activities for 7 days!'
        )
        
        self.assertEqual(badge.user, self.user)
        self.assertEqual(badge.badge_type, 'CONSISTENCY_7')
        self.assertIsNotNone(badge.earned_date)
    
    def test_badge_str_method(self):
        """Test badge string representation"""
        badge = Badge.objects.create(
            user=self.user,
            badge_type='FIRST_WORKOUT',
            description='First!'
        )
        
        expected = f"{self.user.username} - First Workout"
        self.assertEqual(str(badge), expected)
    
    def test_badge_ordering(self):
        """Test badges are ordered by earned_date descending"""
        # Create badges with different times
        badge1 = Badge.objects.create(
            user=self.user,
            badge_type='FIRST_WORKOUT',
            description='First'
        )
        
        badge2 = Badge.objects.create(
            user=self.user,
            badge_type='CONSISTENCY_7',
            description='Second'
        )
        
        # Get all badges
        badges = Badge.objects.filter(user=self.user)
        
        # First badge should be the most recent
        self.assertEqual(badges[0], badge2)


# Run tests with:
# python manage.py test fitnesstrack.test_badges_and_charts
