"""
Fitness calculation utilities for the Fitness Tracker application.

This module provides reusable functions for calculating various fitness metrics
including BMI, BMR, TDEE, and calorie burn estimates.
"""

from decimal import Decimal
from typing import Optional, Union
from datetime import date


class FitnessCalculator:
    """
    A class containing static methods for fitness-related calculations.
    All methods are designed to be reusable and handle edge cases.
    """
    
    # MET (Metabolic Equivalent of Task) values for different activities
    MET_VALUES = {
        'RUNNING': 9.8,
        'CYCLING': 7.5,
        'WEIGHTLIFTING': 6.0,
        'SWIMMING': 8.0,
        'WALKING': 3.8,
        'YOGA': 2.5,
        'HIIT': 8.0,
        'OTHER': 5.0,
    }
    
    # Activity level multipliers for TDEE calculation
    ACTIVITY_MULTIPLIERS = {
        'SEDENTARY': 1.2,      # Little or no exercise
        'ACTIVE': 1.55,        # Moderate exercise 3-5 days/week
        'ATHLETE': 1.9,        # Intense exercise 6-7 days/week
    }
    
    @staticmethod
    def calculate_bmi(weight_kg: Union[float, Decimal], 
                      height_cm: Union[float, Decimal]) -> Optional[float]:
        """
        Calculate Body Mass Index (BMI).
        
        Formula: BMI = weight (kg) / (height (m))^2
        
        Args:
            weight_kg: Weight in kilograms
            height_cm: Height in centimeters
            
        Returns:
            BMI value rounded to 2 decimal places, or None if invalid input
            
        Example:
            >>> FitnessCalculator.calculate_bmi(70, 175)
            22.86
        """
        try:
            weight = float(weight_kg)
            height = float(height_cm)
            
            if weight <= 0 or height <= 0:
                return None
                
            height_m = height / 100  # Convert cm to meters
            bmi = weight / (height_m ** 2)
            return round(bmi, 2)
        except (TypeError, ValueError, ZeroDivisionError):
            return None
    
    @staticmethod
    def get_bmi_category(bmi: float) -> str:
        """
        Determine BMI category based on WHO classification.
        
        Args:
            bmi: Body Mass Index value
            
        Returns:
            String describing the BMI category
        """
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    @staticmethod
    def calculate_bmr(weight_kg: Union[float, Decimal],
                      height_cm: Union[float, Decimal],
                      age: int,
                      gender: str) -> Optional[float]:
        """
        Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation.
        
        This is the most accurate formula for calculating BMR in modern use.
        
        Formulas:
            Men: BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
            Women: BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161
        
        Args:
            weight_kg: Weight in kilograms
            height_cm: Height in centimeters
            age: Age in years
            gender: Gender ('M' for male, 'F' for female, 'O' for other - uses female formula)
            
        Returns:
            BMR in calories per day, or None if invalid input
            
        Example:
            >>> FitnessCalculator.calculate_bmr(70, 175, 30, 'M')
            1673.75
        """
        try:
            weight = float(weight_kg)
            height = float(height_cm)
            
            if weight <= 0 or height <= 0 or age <= 0:
                return None
            
            # Base calculation (same for both genders)
            bmr = (10 * weight) + (6.25 * height) - (5 * age)
            
            # Gender-specific adjustment
            if gender == 'M':
                bmr += 5
            else:  # 'F' or 'O' or any other value uses female formula
                bmr -= 161
                
            return round(bmr, 2)
        except (TypeError, ValueError):
            return None
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> Optional[float]:
        """
        Calculate Total Daily Energy Expenditure (TDEE).
        
        TDEE represents the total number of calories you burn per day,
        including your BMR and activity level.
        
        Formula: TDEE = BMR × Activity Multiplier
        
        Activity Levels:
            - SEDENTARY: Little or no exercise (multiplier: 1.2)
            - ACTIVE: Moderate exercise 3-5 days/week (multiplier: 1.55)
            - ATHLETE: Intense exercise 6-7 days/week (multiplier: 1.9)
        
        Args:
            bmr: Basal Metabolic Rate in calories per day
            activity_level: Activity level ('SEDENTARY', 'ACTIVE', 'ATHLETE')
            
        Returns:
            TDEE in calories per day, or None if invalid input
            
        Example:
            >>> FitnessCalculator.calculate_tdee(1673.75, 'ACTIVE')
            2594.31
        """
        try:
            if bmr <= 0:
                return None
                
            multiplier = FitnessCalculator.ACTIVITY_MULTIPLIERS.get(
                activity_level.upper(), 
                1.2  # Default to sedentary if unknown
            )
            
            tdee = bmr * multiplier
            return round(tdee, 2)
        except (TypeError, ValueError, AttributeError):
            return None
    
    @staticmethod
    def estimate_calories_burned(activity_type: str,
                                duration_minutes: int,
                                weight_kg: Union[float, Decimal]) -> Optional[int]:
        """
        Estimate calories burned during an activity using MET values.
        
        Formula: Calories = MET × weight (kg) × duration (hours)
        
        MET (Metabolic Equivalent of Task) values:
            - Running: 9.8
            - Cycling: 7.5
            - Weightlifting: 6.0
            - Swimming: 8.0
            - Walking: 3.8
            - Yoga: 2.5
            - HIIT: 8.0
            - Other: 5.0
        
        Args:
            activity_type: Type of activity (e.g., 'RUNNING', 'CYCLING')
            duration_minutes: Duration of activity in minutes
            weight_kg: User's weight in kilograms
            
        Returns:
            Estimated calories burned (integer), or None if invalid input
            
        Example:
            >>> FitnessCalculator.estimate_calories_burned('RUNNING', 30, 70)
            343
        """
        try:
            weight = float(weight_kg)
            
            if weight <= 0 or duration_minutes <= 0:
                return None
            
            # Get MET value for the activity type
            met = FitnessCalculator.MET_VALUES.get(
                activity_type.upper(),
                5.0  # Default moderate MET value
            )
            
            # Convert minutes to hours
            duration_hours = duration_minutes / 60
            
            # Calculate calories burned
            calories = met * weight * duration_hours
            return int(round(calories))
        except (TypeError, ValueError, AttributeError):
            return None
    
    @staticmethod
    def calculate_age(date_of_birth: date) -> Optional[int]:
        """
        Calculate age from date of birth.
        
        Args:
            date_of_birth: Date of birth as a date object
            
        Returns:
            Age in years, or None if invalid input
            
        Example:
            >>> from datetime import date
            >>> FitnessCalculator.calculate_age(date(1990, 5, 15))
            35  # (assuming current year is 2026)
        """
        try:
            today = date.today()
            age = today.year - date_of_birth.year
            
            # Adjust if birthday hasn't occurred this year
            if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
                age -= 1
                
            return age if age >= 0 else None
        except (TypeError, AttributeError):
            return None
    
    @staticmethod
    def calculate_ideal_weight_range(height_cm: Union[float, Decimal],
                                    gender: str = 'M') -> Optional[dict]:
        """
        Calculate ideal weight range based on healthy BMI (18.5-24.9).
        
        Args:
            height_cm: Height in centimeters
            gender: Gender ('M' or 'F') - currently for reference only
            
        Returns:
            Dictionary with 'min' and 'max' ideal weights in kg, or None if invalid
            
        Example:
            >>> FitnessCalculator.calculate_ideal_weight_range(175)
            {'min': 56.61, 'max': 76.26}
        """
        try:
            height = float(height_cm)
            
            if height <= 0:
                return None
            
            height_m = height / 100
            
            # Calculate weight range for healthy BMI (18.5 - 24.9)
            min_weight = 18.5 * (height_m ** 2)
            max_weight = 24.9 * (height_m ** 2)
            
            return {
                'min': round(min_weight, 2),
                'max': round(max_weight, 2)
            }
        except (TypeError, ValueError):
            return None
    
    @staticmethod
    def calculate_macros(tdee: float,
                        goal: str = 'MAINTAIN') -> Optional[dict]:
        """
        Calculate recommended macronutrient breakdown based on TDEE and goal.
        
        Macro ratios:
            - WEIGHT_LOSS: 40% protein, 30% carbs, 30% fat
            - MUSCLE_GAIN: 30% protein, 50% carbs, 20% fat
            - MAINTAIN: 30% protein, 40% carbs, 30% fat
        
        Args:
            tdee: Total Daily Energy Expenditure in calories
            goal: Fitness goal ('WEIGHT_LOSS', 'MUSCLE_GAIN', 'MAINTAIN')
            
        Returns:
            Dictionary with macro breakdown in grams, or None if invalid
            
        Example:
            >>> FitnessCalculator.calculate_macros(2500, 'MAINTAIN')
            {'protein_g': 187.5, 'carbs_g': 250.0, 'fat_g': 83.33, 'calories': 2500}
        """
        try:
            if tdee <= 0:
                return None
            
            # Calories per gram
            PROTEIN_CAL_PER_G = 4
            CARB_CAL_PER_G = 4
            FAT_CAL_PER_G = 9
            
            # Macro ratios based on goal
            if goal == 'WEIGHT_LOSS':
                protein_ratio, carb_ratio, fat_ratio = 0.40, 0.30, 0.30
            elif goal == 'MUSCLE_GAIN':
                protein_ratio, carb_ratio, fat_ratio = 0.30, 0.50, 0.20
            else:  # MAINTAIN or default
                protein_ratio, carb_ratio, fat_ratio = 0.30, 0.40, 0.30
            
            # Calculate calories for each macro
            protein_calories = tdee * protein_ratio
            carb_calories = tdee * carb_ratio
            fat_calories = tdee * fat_ratio
            
            # Convert to grams
            protein_g = protein_calories / PROTEIN_CAL_PER_G
            carbs_g = carb_calories / CARB_CAL_PER_G
            fat_g = fat_calories / FAT_CAL_PER_G
            
            return {
                'protein_g': round(protein_g, 2),
                'carbs_g': round(carbs_g, 2),
                'fat_g': round(fat_g, 2),
                'calories': round(tdee, 2)
            }
        except (TypeError, ValueError):
            return None
    
    @staticmethod
    def calculate_water_intake_target(weight_kg: Union[float, Decimal],
                                     activity_level: str = 'SEDENTARY') -> Optional[int]:
        """
        Calculate recommended daily water intake in milliliters.
        
        Base formula: 30-35 ml per kg of body weight
        Adjusted for activity level.
        
        Args:
            weight_kg: Weight in kilograms
            activity_level: Activity level ('SEDENTARY', 'ACTIVE', 'ATHLETE')
            
        Returns:
            Recommended water intake in milliliters, or None if invalid
            
        Example:
            >>> FitnessCalculator.calculate_water_intake_target(70, 'ACTIVE')
            2625
        """
        try:
            weight = float(weight_kg)
            
            if weight <= 0:
                return None
            
            # Base calculation: 35 ml per kg
            base_intake = weight * 35
            
            # Adjust for activity level
            if activity_level == 'ATHLETE':
                base_intake *= 1.3  # 30% more for athletes
            elif activity_level == 'ACTIVE':
                base_intake *= 1.15  # 15% more for active people
            
            return int(round(base_intake))
        except (TypeError, ValueError, AttributeError):
            return None


# Convenience functions for direct module-level access
def calculate_bmi(weight_kg: Union[float, Decimal], 
                 height_cm: Union[float, Decimal]) -> Optional[float]:
    """Convenience function for BMI calculation."""
    return FitnessCalculator.calculate_bmi(weight_kg, height_cm)


def calculate_bmr(weight_kg: Union[float, Decimal],
                 height_cm: Union[float, Decimal],
                 age: int,
                 gender: str) -> Optional[float]:
    """Convenience function for BMR calculation."""
    return FitnessCalculator.calculate_bmr(weight_kg, height_cm, age, gender)


def calculate_tdee(bmr: float, activity_level: str) -> Optional[float]:
    """Convenience function for TDEE calculation."""
    return FitnessCalculator.calculate_tdee(bmr, activity_level)


def estimate_calories_burned(activity_type: str,
                           duration_minutes: int,
                           weight_kg: Union[float, Decimal]) -> Optional[int]:
    """Convenience function for calorie burn estimation."""
    return FitnessCalculator.estimate_calories_burned(
        activity_type, duration_minutes, weight_kg
    )


def generate_daily_tip(user) -> Optional[str]:
    """
    Generate personalized daily tip based on user's yesterday data.
    
    Analyzes the user's activity from yesterday and provides actionable
    recommendations for today based on:
    - Water intake (< 2000ml triggers hydration alert)
    - Sleep hours (< 7 hours triggers recovery focus) - Not yet implemented
    - Calories burned (> 500 shows encouragement)
    
    Args:
        user: Django User object
        
    Returns:
        str: Personalized tip message, or None if no tip applicable
        
    Priority order (returns first matching condition):
        1. Hydration alert (most important for health)
        2. Sleep recovery (if sleep tracking is implemented)
        3. High calorie burn encouragement
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import WaterIntake, ActivityLog
    
    # Get yesterday's date
    yesterday = timezone.now().date() - timedelta(days=1)
    
    # Check water intake for yesterday
    try:
        daily_water = WaterIntake.get_daily_total(user, yesterday)
        if daily_water < 2000:
            return 'Hydration Alert: Try to drink more water today.'
    except Exception:
        pass
    
    # Check sleep hours (placeholder for future sleep tracking feature)
    # TODO: Implement sleep tracking model and uncomment this section
    # try:
    #     from .models import SleepLog
    #     yesterday_sleep = SleepLog.objects.filter(
    #         user=user,
    #         date_recorded__date=yesterday
    #     ).first()
    #     
    #     if yesterday_sleep and yesterday_sleep.hours < 7:
    #         return 'Recovery Focus: Prioritize getting to bed early tonight.'
    # except Exception:
    #     pass
    
    # Check calories burned for yesterday
    try:
        from django.db.models import Sum
        
        total_calories = ActivityLog.objects.filter(
            user=user,
            date_created__date=yesterday
        ).aggregate(total=Sum('calories_burned'))['total'] or 0
        
        if total_calories > 500:
            return 'Great work! You hit a high burn yesterday.'
    except Exception:
        pass
    
    # No specific tip applicable, return motivational message
    return 'Keep up the great work! Stay consistent with your fitness journey.'
