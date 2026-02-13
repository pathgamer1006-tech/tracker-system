"""
Unit tests for fitness calculation utilities.

Run with: python manage.py test fitnesstrack.test_utils
"""

from django.test import TestCase
from decimal import Decimal
from datetime import date
from .utils import FitnessCalculator


class BMICalculatorTests(TestCase):
    """Test cases for BMI calculation"""
    
    def test_calculate_bmi_normal(self):
        """Test BMI calculation with normal values"""
        bmi = FitnessCalculator.calculate_bmi(70, 175)
        self.assertAlmostEqual(bmi, 22.86, places=2)
    
    def test_calculate_bmi_decimal(self):
        """Test BMI calculation with Decimal values"""
        bmi = FitnessCalculator.calculate_bmi(Decimal('70.5'), Decimal('175.5'))
        self.assertIsNotNone(bmi)
        self.assertAlmostEqual(bmi, 22.89, places=2)
    
    def test_calculate_bmi_invalid(self):
        """Test BMI calculation with invalid values"""
        self.assertIsNone(FitnessCalculator.calculate_bmi(0, 175))
        self.assertIsNone(FitnessCalculator.calculate_bmi(70, 0))
        self.assertIsNone(FitnessCalculator.calculate_bmi(-70, 175))
    
    def test_get_bmi_category(self):
        """Test BMI category classification"""
        self.assertEqual(FitnessCalculator.get_bmi_category(17), "Underweight")
        self.assertEqual(FitnessCalculator.get_bmi_category(22), "Normal weight")
        self.assertEqual(FitnessCalculator.get_bmi_category(27), "Overweight")
        self.assertEqual(FitnessCalculator.get_bmi_category(32), "Obese")


class BMRCalculatorTests(TestCase):
    """Test cases for BMR calculation"""
    
    def test_calculate_bmr_male(self):
        """Test BMR calculation for male"""
        bmr = FitnessCalculator.calculate_bmr(70, 175, 30, 'M')
        self.assertAlmostEqual(bmr, 1648.75, places=2)
    
    def test_calculate_bmr_female(self):
        """Test BMR calculation for female"""
        bmr = FitnessCalculator.calculate_bmr(60, 165, 25, 'F')
        self.assertAlmostEqual(bmr, 1345.25, places=2)
    
    def test_calculate_bmr_other_gender(self):
        """Test BMR calculation for other gender (uses female formula)"""
        bmr = FitnessCalculator.calculate_bmr(65, 170, 28, 'O')
        self.assertIsNotNone(bmr)
        # Should use female formula
        expected = (10 * 65) + (6.25 * 170) - (5 * 28) - 161
        self.assertAlmostEqual(bmr, expected, places=2)
    
    def test_calculate_bmr_invalid(self):
        """Test BMR calculation with invalid values"""
        self.assertIsNone(FitnessCalculator.calculate_bmr(0, 175, 30, 'M'))
        self.assertIsNone(FitnessCalculator.calculate_bmr(70, 0, 30, 'M'))
        self.assertIsNone(FitnessCalculator.calculate_bmr(70, 175, 0, 'M'))


class TDEECalculatorTests(TestCase):
    """Test cases for TDEE calculation"""
    
    def test_calculate_tdee_sedentary(self):
        """Test TDEE calculation for sedentary activity level"""
        tdee = FitnessCalculator.calculate_tdee(1648.75, 'SEDENTARY')
        self.assertAlmostEqual(tdee, 1978.50, places=2)
    
    def test_calculate_tdee_active(self):
        """Test TDEE calculation for active activity level"""
        tdee = FitnessCalculator.calculate_tdee(1648.75, 'ACTIVE')
        self.assertAlmostEqual(tdee, 2555.56, places=2)
    
    def test_calculate_tdee_athlete(self):
        """Test TDEE calculation for athlete activity level"""
        tdee = FitnessCalculator.calculate_tdee(1648.75, 'ATHLETE')
        self.assertAlmostEqual(tdee, 3132.62, places=1)
    
    def test_calculate_tdee_invalid(self):
        """Test TDEE calculation with invalid BMR"""
        self.assertIsNone(FitnessCalculator.calculate_tdee(0, 'ACTIVE'))
        self.assertIsNone(FitnessCalculator.calculate_tdee(-1000, 'ACTIVE'))


class CalorieBurnTests(TestCase):
    """Test cases for calorie burn estimation"""
    
    def test_estimate_calories_running(self):
        """Test calorie estimation for running"""
        calories = FitnessCalculator.estimate_calories_burned('RUNNING', 30, 70)
        # MET 9.8 * 70 kg * 0.5 hours = 343
        self.assertEqual(calories, 343)
    
    def test_estimate_calories_walking(self):
        """Test calorie estimation for walking"""
        calories = FitnessCalculator.estimate_calories_burned('WALKING', 60, 70)
        # MET 3.8 * 70 kg * 1 hour = 266
        self.assertEqual(calories, 266)
    
    def test_estimate_calories_cycling(self):
        """Test calorie estimation for cycling"""
        calories = FitnessCalculator.estimate_calories_burned('CYCLING', 45, 80)
        # MET 7.5 * 80 kg * 0.75 hours = 450
        self.assertEqual(calories, 450)
    
    def test_estimate_calories_unknown_activity(self):
        """Test calorie estimation for unknown activity (uses default MET)"""
        calories = FitnessCalculator.estimate_calories_burned('UNKNOWN', 30, 70)
        self.assertIsNotNone(calories)
        # Should use default MET of 5.0
        expected = int(round(5.0 * 70 * 0.5))
        self.assertEqual(calories, expected)
    
    def test_estimate_calories_invalid(self):
        """Test calorie estimation with invalid values"""
        self.assertIsNone(
            FitnessCalculator.estimate_calories_burned('RUNNING', 0, 70)
        )
        self.assertIsNone(
            FitnessCalculator.estimate_calories_burned('RUNNING', 30, 0)
        )


class AgeCalculatorTests(TestCase):
    """Test cases for age calculation"""
    
    def test_calculate_age(self):
        """Test age calculation"""
        # Assuming current date is Feb 13, 2026
        dob = date(1990, 5, 15)
        age = FitnessCalculator.calculate_age(dob)
        self.assertEqual(age, 35)
    
    def test_calculate_age_birthday_not_yet(self):
        """Test age when birthday hasn't occurred this year"""
        # Birthday in March, but current date is February
        dob = date(1990, 3, 15)
        age = FitnessCalculator.calculate_age(dob)
        # Should still be 35 (not 36 yet)
        self.assertEqual(age, 35)
    
    def test_calculate_age_birthday_passed(self):
        """Test age when birthday has already passed this year"""
        dob = date(1990, 1, 15)
        age = FitnessCalculator.calculate_age(dob)
        # Birthday already passed, should be 36
        self.assertEqual(age, 36)


class IdealWeightTests(TestCase):
    """Test cases for ideal weight range calculation"""
    
    def test_calculate_ideal_weight_range(self):
        """Test ideal weight range calculation"""
        result = FitnessCalculator.calculate_ideal_weight_range(175)
        self.assertIsNotNone(result)
        self.assertIn('min', result)
        self.assertIn('max', result)
        # For 175cm, BMI 18.5-24.9 should give approximately 56.6-76.3 kg
        self.assertAlmostEqual(result['min'], 56.61, places=1)
        self.assertAlmostEqual(result['max'], 76.26, places=1)
    
    def test_calculate_ideal_weight_invalid(self):
        """Test ideal weight calculation with invalid height"""
        self.assertIsNone(FitnessCalculator.calculate_ideal_weight_range(0))
        self.assertIsNone(FitnessCalculator.calculate_ideal_weight_range(-175))


class MacrosCalculatorTests(TestCase):
    """Test cases for macronutrient calculation"""
    
    def test_calculate_macros_maintain(self):
        """Test macro calculation for maintenance"""
        result = FitnessCalculator.calculate_macros(2500, 'MAINTAIN')
        self.assertIsNotNone(result)
        # 30% protein, 40% carbs, 30% fat
        self.assertAlmostEqual(result['protein_g'], 187.5, places=1)
        self.assertAlmostEqual(result['carbs_g'], 250.0, places=1)
        self.assertAlmostEqual(result['fat_g'], 83.33, places=1)
    
    def test_calculate_macros_weight_loss(self):
        """Test macro calculation for weight loss"""
        result = FitnessCalculator.calculate_macros(2000, 'WEIGHT_LOSS')
        self.assertIsNotNone(result)
        # 40% protein, 30% carbs, 30% fat
        self.assertAlmostEqual(result['protein_g'], 200.0, places=1)
        self.assertAlmostEqual(result['carbs_g'], 150.0, places=1)
    
    def test_calculate_macros_muscle_gain(self):
        """Test macro calculation for muscle gain"""
        result = FitnessCalculator.calculate_macros(3000, 'MUSCLE_GAIN')
        self.assertIsNotNone(result)
        # 30% protein, 50% carbs, 20% fat
        self.assertAlmostEqual(result['protein_g'], 225.0, places=1)
        self.assertAlmostEqual(result['carbs_g'], 375.0, places=1)


class WaterIntakeTests(TestCase):
    """Test cases for water intake calculation"""
    
    def test_calculate_water_intake_sedentary(self):
        """Test water intake for sedentary person"""
        intake = FitnessCalculator.calculate_water_intake_target(70, 'SEDENTARY')
        # 70 kg * 35 ml = 2450 ml
        self.assertEqual(intake, 2450)
    
    def test_calculate_water_intake_active(self):
        """Test water intake for active person"""
        intake = FitnessCalculator.calculate_water_intake_target(70, 'ACTIVE')
        # 70 kg * 35 ml * 1.15 = 2817.5 → 2818 ml
        self.assertAlmostEqual(intake, 2818, delta=2)
    
    def test_calculate_water_intake_athlete(self):
        """Test water intake for athlete"""
        intake = FitnessCalculator.calculate_water_intake_target(70, 'ATHLETE')
        # 70 kg * 35 ml * 1.3 = 3185 ml
        self.assertAlmostEqual(intake, 3185, delta=2)
    
    def test_calculate_water_intake_invalid(self):
        """Test water intake with invalid weight"""
        self.assertIsNone(
            FitnessCalculator.calculate_water_intake_target(0, 'ACTIVE')
        )
