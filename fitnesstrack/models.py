from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class UserProfile(models.Model):
    """Extended user profile with health and fitness information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        ('SEDENTARY', 'Sedentary'),
        ('ACTIVE', 'Active'),
        ('ATHLETE', 'Athlete'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text="User's date of birth"
    )
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )
    height_cm = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True,
        blank=True,
        help_text="Height in centimeters"
    )
    weight_kg = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True,
        blank=True,
        help_text="Current weight in kilograms"
    )
    activity_level = models.CharField(
        max_length=20,
        choices=ACTIVITY_LEVEL_CHOICES,
        default='SEDENTARY',
        help_text="General activity level"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def age(self):
        """Calculate user's age from date of birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def bmi(self):
        """Calculate Body Mass Index"""
        if self.height_cm and self.weight_kg:
            height_m = float(self.height_cm) / 100
            return round(float(self.weight_kg) / (height_m ** 2), 2)
        return None


class ActivityLog(models.Model):
    """Track daily exercises and physical activities"""
    ACTIVITY_TYPE_CHOICES = [
        ('RUNNING', 'Running'),
        ('CYCLING', 'Cycling'),
        ('WEIGHTLIFTING', 'Weightlifting'),
        ('SWIMMING', 'Swimming'),
        ('WALKING', 'Walking'),
        ('YOGA', 'Yoga'),
        ('HIIT', 'HIIT'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES,
        help_text="Type of physical activity"
    )
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Duration of activity in minutes"
    )
    distance_km = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True,
        help_text="Distance covered in kilometers (if applicable)"
    )
    calories_burned = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated calories burned during activity"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the activity"
    )
    date_created = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['-date_created', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} on {self.date_created.date()}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate calories burned if not provided"""
        if not self.calories_burned:
            self.calories_burned = self.calculate_calories()
        super().save(*args, **kwargs)
    
    def calculate_calories(self):
        """
        Estimate calories burned based on activity type and duration
        Using METs (Metabolic Equivalent of Task) approximation
        Assumes average weight of 70kg for calculation
        """
        # MET values for different activities
        met_values = {
            'RUNNING': 9.8,
            'CYCLING': 7.5,
            'WEIGHTLIFTING': 6.0,
            'SWIMMING': 8.0,
            'WALKING': 3.8,
            'YOGA': 2.5,
            'HIIT': 8.0,
            'OTHER': 5.0,
        }
        
        met = met_values.get(self.activity_type, 5.0)
        
        # Get user's actual weight if available
        try:
            weight_kg = float(self.user.profile.weight_kg) if self.user.profile.weight_kg else 70.0
        except:
            weight_kg = 70.0
        
        # Calories = MET * weight(kg) * time(hours)
        calories = met * weight_kg * (self.duration_minutes / 60)
        return int(round(calories))


class BiometricsLog(models.Model):
    """Track weight and body composition changes over time"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='biometrics_logs'
    )
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Weight in kilograms"
    )
    body_fat_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        null=True,
        blank=True,
        help_text="Body fat percentage"
    )
    muscle_mass_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True,
        help_text="Muscle mass in kilograms"
    )
    waist_circumference_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True,
        help_text="Waist circumference in centimeters"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional observations"
    )
    date_recorded = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Biometrics Log"
        verbose_name_plural = "Biometrics Logs"
        ordering = ['-date_recorded']
        indexes = [
            models.Index(fields=['-date_recorded', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.weight_kg}kg on {self.date_recorded.date()}"
    
    @property
    def bmi(self):
        """Calculate BMI using logged weight and user's height"""
        try:
            if self.user.profile.height_cm:
                height_m = float(self.user.profile.height_cm) / 100
                return round(float(self.weight_kg) / (height_m ** 2), 2)
        except:
            pass
        return None


class Goal(models.Model):
    """Set and track fitness goals and targets"""
    GOAL_TYPE_CHOICES = [
        ('WEIGHT', 'Target Weight'),
        ('WEEKLY_STEPS', 'Weekly Steps'),
        ('MONTHLY_DISTANCE', 'Monthly Distance'),
        ('BODY_FAT', 'Body Fat Percentage'),
        ('MUSCLE_GAIN', 'Muscle Gain'),
        ('EXERCISE_FREQUENCY', 'Exercise Frequency'),
        ('WATER_INTAKE', 'Daily Water Intake'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('ABANDONED', 'Abandoned'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    goal_type = models.CharField(
        max_length=20,
        choices=GOAL_TYPE_CHOICES,
        help_text="Type of fitness goal"
    )
    title = models.CharField(
        max_length=200,
        help_text="Goal title or description"
    )
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Target numerical value"
    )
    current_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text="Current progress value"
    )
    unit = models.CharField(
        max_length=20,
        default='units',
        help_text="Unit of measurement (kg, km, steps, %, etc.)"
    )
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target completion date"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional goal details"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Goal"
        verbose_name_plural = "Goals"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    @property
    def progress_percentage(self):
        """Calculate goal progress as a percentage"""
        if self.target_value > 0:
            progress = (float(self.current_value) / float(self.target_value)) * 100
            return min(round(progress, 2), 100.0)
        return 0.0
    
    @property
    def is_achieved(self):
        """Check if goal has been achieved"""
        return self.current_value >= self.target_value


class WaterIntake(models.Model):
    """Log daily water intake"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='water_intakes'
    )
    milliliters = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Amount of water in milliliters"
    )
    date_recorded = models.DateTimeField(default=timezone.now)
    notes = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional notes (e.g., type of beverage)"
    )
    
    class Meta:
        verbose_name = "Water Intake"
        verbose_name_plural = "Water Intakes"
        ordering = ['-date_recorded']
        indexes = [
            models.Index(fields=['-date_recorded', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.milliliters}ml on {self.date_recorded.date()}"
    
    @classmethod
    def get_daily_total(cls, user, date=None):
        """Get total water intake for a specific day"""
        if date is None:
            date = timezone.now().date()
        
        daily_logs = cls.objects.filter(
            user=user,
            date_recorded__date=date
        )
        
        total = sum(log.milliliters for log in daily_logs)
        return total


class Badge(models.Model):
    """Achievement badges for fitness milestones"""
    BADGE_TYPES = [
        ('CONSISTENCY_7', '7-Day Consistency'),
        ('CONSISTENCY_30', '30-Day Consistency'),
        ('FIRST_WORKOUT', 'First Workout'),
        ('CALORIE_BURNER_1000', '1000 Calories Burned'),
        ('CALORIE_BURNER_5000', '5000 Calories Burned'),
        ('EARLY_BIRD', 'Early Bird (Workout before 7 AM)'),
        ('HYDRATION_MASTER', 'Hydration Master'),
        ('WEIGHT_GOAL', 'Weight Goal Achieved'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='badges'
    )
    badge_type = models.CharField(
        max_length=30,
        choices=BADGE_TYPES,
        help_text="Type of achievement badge"
    )
    earned_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Achievement description"
    )
    
    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ['-earned_date']
        unique_together = ['user', 'badge_type']  # One badge per type per user
        indexes = [
            models.Index(fields=['user', 'badge_type']),
        ]
    
    @property
    def icon(self):
        """Return emoji icon for badge type"""
        icon_map = {
            'CONSISTENCY_7': '🔥',
            'CONSISTENCY_30': '💪',
            'FIRST_WORKOUT': '🌟',
            'CALORIE_BURNER_1000': '🔥',
            'CALORIE_BURNER_5000': '💥',
            'EARLY_BIRD': '🌅',
            'HYDRATION_MASTER': '💧',
            'WEIGHT_GOAL': '🎯',
        }
        return icon_map.get(self.badge_type, '🏅')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_badge_type_display()}"


class MealLog(models.Model):
    """Track meals and nutrition intake"""
    MEAL_TYPE_CHOICES = [
        ('BREAKFAST', 'Breakfast'),
        ('LUNCH', 'Lunch'),
        ('DINNER', 'Dinner'),
        ('SNACK', 'Snack'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meals'
    )
    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPE_CHOICES,
        default='BREAKFAST'
    )
    food_name = models.CharField(
        max_length=255,
        help_text="Name of the food/meal"
    )
    calories = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Calories in kcal"
    )
    protein_g = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0'))],
        default=0,
        help_text="Protein in grams"
    )
    carbs_g = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0'))],
        default=0,
        help_text="Carbohydrates in grams"
    )
    fats_g = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0'))],
        default=0,
        help_text="Fats in grams"
    )
    serving_size = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="e.g., '1 cup', '100g', '1 serving'"
    )
    notes = models.TextField(
        null=True,
        blank=True
    )
    date_logged = models.DateTimeField(
        default=timezone.now
    )
    
    class Meta:
        ordering = ['-date_logged']
        indexes = [
            models.Index(fields=['user', '-date_logged']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.food_name} ({self.get_meal_type_display()})"

