"""
Demo script showing how to use the fitness calculator utilities.

This script demonstrates all the functions available in utils.py
"""

from datetime import date
from fitnesstrack.utils import FitnessCalculator


def print_section(title):
    """Helper to print section headers"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_bmi_calculation():
    """Demonstrate BMI calculation"""
    print_section("BMI CALCULATION")
    
    weight = 70  # kg
    height = 175  # cm
    
    bmi = FitnessCalculator.calculate_bmi(weight, height)
    category = FitnessCalculator.get_bmi_category(bmi)
    
    print(f"Weight: {weight} kg")
    print(f"Height: {height} cm")
    print(f"BMI: {bmi}")
    print(f"Category: {category}")
    
    # Ideal weight range
    ideal_range = FitnessCalculator.calculate_ideal_weight_range(height)
    print(f"\nIdeal weight range for your height:")
    print(f"  Minimum: {ideal_range['min']} kg")
    print(f"  Maximum: {ideal_range['max']} kg")


def demo_bmr_calculation():
    """Demonstrate BMR calculation"""
    print_section("BMR CALCULATION (Basal Metabolic Rate)")
    
    weight = 70  # kg
    height = 175  # cm
    age = 30
    gender = 'M'
    
    bmr = FitnessCalculator.calculate_bmr(weight, height, age, gender)
    
    print(f"Weight: {weight} kg")
    print(f"Height: {height} cm")
    print(f"Age: {age} years")
    print(f"Gender: {'Male' if gender == 'M' else 'Female'}")
    print(f"\nBMR: {bmr} calories/day")
    print(f"\nThis is the number of calories your body burns at rest.")


def demo_tdee_calculation():
    """Demonstrate TDEE calculation"""
    print_section("TDEE CALCULATION (Total Daily Energy Expenditure)")
    
    bmr = 1673.75  # from previous calculation
    
    print(f"Base BMR: {bmr} calories/day\n")
    
    for activity_level in ['SEDENTARY', 'ACTIVE', 'ATHLETE']:
        tdee = FitnessCalculator.calculate_tdee(bmr, activity_level)
        print(f"{activity_level:12s}: {tdee:7.2f} calories/day")
    
    print("\nTDEE = BMR × Activity Level Multiplier")
    print("This is your total daily calorie burn including activities.")


def demo_calorie_burn():
    """Demonstrate calorie burn estimation"""
    print_section("CALORIE BURN ESTIMATION")
    
    weight = 70  # kg
    print(f"User weight: {weight} kg\n")
    
    activities = [
        ('RUNNING', 30, "30-minute run"),
        ('CYCLING', 45, "45-minute bike ride"),
        ('WALKING', 60, "1-hour walk"),
        ('WEIGHTLIFTING', 45, "45-minute weight training"),
        ('SWIMMING', 30, "30-minute swim"),
        ('YOGA', 60, "1-hour yoga session"),
    ]
    
    print(f"{'Activity':<25s} {'Duration':<15s} {'Calories Burned':>20s}")
    print("-" * 60)
    
    for activity_type, duration, description in activities:
        calories = FitnessCalculator.estimate_calories_burned(
            activity_type, duration, weight
        )
        print(f"{description:<25s} {duration:>3d} minutes    {calories:>15d} cal")


def demo_macronutrients():
    """Demonstrate macronutrient calculation"""
    print_section("MACRONUTRIENT BREAKDOWN")
    
    tdee = 2500  # calories
    
    print(f"TDEE: {tdee} calories/day\n")
    
    goals = ['MAINTAIN', 'WEIGHT_LOSS', 'MUSCLE_GAIN']
    
    for goal in goals:
        macros = FitnessCalculator.calculate_macros(tdee, goal)
        print(f"\n{goal}:")
        print(f"  Protein: {macros['protein_g']:.1f}g")
        print(f"  Carbs:   {macros['carbs_g']:.1f}g")
        print(f"  Fat:     {macros['fat_g']:.1f}g")


def demo_water_intake():
    """Demonstrate water intake calculation"""
    print_section("DAILY WATER INTAKE TARGET")
    
    weight = 70  # kg
    print(f"User weight: {weight} kg\n")
    
    for activity_level in ['SEDENTARY', 'ACTIVE', 'ATHLETE']:
        intake = FitnessCalculator.calculate_water_intake_target(
            weight, activity_level
        )
        liters = intake / 1000
        print(f"{activity_level:12s}: {intake:>5d} ml ({liters:.2f} liters)")


def demo_complete_profile():
    """Demonstrate a complete user profile analysis"""
    print_section("COMPLETE FITNESS PROFILE ANALYSIS")
    
    # User data
    name = "John Doe"
    weight = 75
    height = 180
    age = 28
    gender = 'M'
    activity_level = 'ACTIVE'
    dob = date(1998, 3, 15)
    
    print(f"User: {name}")
    print(f"Age: {FitnessCalculator.calculate_age(dob)} years")
    print(f"Weight: {weight} kg")
    print(f"Height: {height} cm")
    print(f"Activity Level: {activity_level}")
    
    # Calculate all metrics
    bmi = FitnessCalculator.calculate_bmi(weight, height)
    bmr = FitnessCalculator.calculate_bmr(weight, height, age, gender)
    tdee = FitnessCalculator.calculate_tdee(bmr, activity_level)
    ideal_weight = FitnessCalculator.calculate_ideal_weight_range(height)
    water_target = FitnessCalculator.calculate_water_intake_target(
        weight, activity_level
    )
    macros = FitnessCalculator.calculate_macros(tdee, 'MAINTAIN')
    
    print(f"\n{'BODY METRICS':-^60}")
    print(f"BMI: {bmi} ({FitnessCalculator.get_bmi_category(bmi)})")
    print(f"Ideal Weight Range: {ideal_weight['min']}-{ideal_weight['max']} kg")
    
    print(f"\n{'CALORIC NEEDS':-^60}")
    print(f"BMR (Basal Metabolic Rate): {bmr:.0f} cal/day")
    print(f"TDEE (Total Daily Energy):  {tdee:.0f} cal/day")
    
    print(f"\n{'NUTRITION TARGETS':-^60}")
    print(f"Protein: {macros['protein_g']:.0f}g/day")
    print(f"Carbs:   {macros['carbs_g']:.0f}g/day")
    print(f"Fat:     {macros['fat_g']:.0f}g/day")
    print(f"Water:   {water_target}ml/day ({water_target/1000:.1f} liters)")
    
    print(f"\n{'SAMPLE WORKOUT CALORIE BURN':-^60}")
    print(f"30-min run:  {FitnessCalculator.estimate_calories_burned('RUNNING', 30, weight)} calories")
    print(f"45-min bike: {FitnessCalculator.estimate_calories_burned('CYCLING', 45, weight)} calories")
    print(f"60-min walk: {FitnessCalculator.estimate_calories_burned('WALKING', 60, weight)} calories")


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  FITNESS CALCULATOR UTILITIES - DEMONSTRATION".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    
    demo_bmi_calculation()
    demo_bmr_calculation()
    demo_tdee_calculation()
    demo_calorie_burn()
    demo_macronutrients()
    demo_water_intake()
    demo_complete_profile()
    
    print("\n" + "=" * 60)
    print("  Demo completed!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
