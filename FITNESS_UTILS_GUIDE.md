# Fitness Calculator Utilities - Quick Reference Guide

## Overview
This module provides comprehensive fitness calculation utilities for the Fitness Tracker application. All calculations follow industry-standard formulas and best practices.

## Installation
The utilities are located in: `fitnesstrack/utils.py`

## Usage Examples

### 1. BMI Calculation
```python
from fitnesstrack.utils import FitnessCalculator

# Calculate BMI
bmi = FitnessCalculator.calculate_bmi(weight_kg=70, height_cm=175)
print(f"BMI: {bmi}")  # Output: BMI: 22.86

# Get BMI category
category = FitnessCalculator.get_bmi_category(bmi)
print(f"Category: {category}")  # Output: Category: Normal weight

# Get ideal weight range
ideal = FitnessCalculator.calculate_ideal_weight_range(height_cm=175)
print(f"Ideal weight: {ideal['min']}-{ideal['max']} kg")
```

### 2. BMR Calculation (Basal Metabolic Rate)
```python
# Using Mifflin-St Jeor equation
bmr = FitnessCalculator.calculate_bmr(
    weight_kg=70,
    height_cm=175,
    age=30,
    gender='M'  # 'M', 'F', or 'O'
)
print(f"BMR: {bmr} calories/day")  # Output: BMR: 1648.75 calories/day
```

### 3. TDEE Calculation (Total Daily Energy Expenditure)
```python
# Calculate total daily calorie needs
tdee = FitnessCalculator.calculate_tdee(
    bmr=1648.75,
    activity_level='ACTIVE'  # 'SEDENTARY', 'ACTIVE', or 'ATHLETE'
)
print(f"TDEE: {tdee} calories/day")  # Output: TDEE: 2555.56 calories/day
```

### 4. Calorie Burn Estimation
```python
# Estimate calories burned during activity
calories = FitnessCalculator.estimate_calories_burned(
    activity_type='RUNNING',  # See list below
    duration_minutes=30,
    weight_kg=70
)
print(f"Calories burned: {calories}")  # Output: Calories burned: 343
```

**Supported Activity Types:**
- `RUNNING` (MET: 9.8)
- `CYCLING` (MET: 7.5)
- `WEIGHTLIFTING` (MET: 6.0)
- `SWIMMING` (MET: 8.0)
- `WALKING` (MET: 3.8)
- `YOGA` (MET: 2.5)
- `HIIT` (MET: 8.0)
- `OTHER` (MET: 5.0)

### 5. Macronutrient Calculation
```python
# Calculate macro breakdown
macros = FitnessCalculator.calculate_macros(
    tdee=2500,
    goal='MAINTAIN'  # 'MAINTAIN', 'WEIGHT_LOSS', or 'MUSCLE_GAIN'
)
print(f"Protein: {macros['protein_g']}g")
print(f"Carbs: {macros['carbs_g']}g")
print(f"Fat: {macros['fat_g']}g")
```

**Macro Ratios by Goal:**
- **MAINTAIN**: 30% protein, 40% carbs, 30% fat
- **WEIGHT_LOSS**: 40% protein, 30% carbs, 30% fat
- **MUSCLE_GAIN**: 30% protein, 50% carbs, 20% fat

### 6. Water Intake Calculation
```python
# Calculate daily water target
water_ml = FitnessCalculator.calculate_water_intake_target(
    weight_kg=70,
    activity_level='ACTIVE'
)
print(f"Daily water target: {water_ml}ml ({water_ml/1000:.1f}L)")
```

### 7. Age Calculation
```python
from datetime import date

age = FitnessCalculator.calculate_age(date(1990, 5, 15))
print(f"Age: {age} years")
```

## Integration with Django Models

### Example: Auto-calculate calories in ActivityLog
```python
# In your view or model save method
from fitnesstrack.utils import FitnessCalculator

activity = ActivityLog.objects.create(
    user=request.user,
    activity_type='RUNNING',
    duration_minutes=30
)

# Auto-calculate calories
user_weight = request.user.profile.weight_kg
if user_weight:
    activity.calories_burned = FitnessCalculator.estimate_calories_burned(
        activity.activity_type,
        activity.duration_minutes,
        user_weight
    )
    activity.save()
```

### Example: Display user fitness metrics
```python
# In your view
from fitnesstrack.utils import FitnessCalculator

def profile_view(request):
    profile = request.user.profile
    
    # Calculate all metrics
    bmi = FitnessCalculator.calculate_bmi(profile.weight_kg, profile.height_cm)
    bmr = FitnessCalculator.calculate_bmr(
        profile.weight_kg,
        profile.height_cm,
        profile.age,
        profile.gender
    )
    tdee = FitnessCalculator.calculate_tdee(bmr, profile.activity_level)
    water_target = FitnessCalculator.calculate_water_intake_target(
        profile.weight_kg,
        profile.activity_level
    )
    
    context = {
        'bmi': bmi,
        'bmr': bmr,
        'tdee': tdee,
        'water_target': water_target,
    }
    return render(request, 'profile.html', context)
```

## Formulas Reference

### BMI (Body Mass Index)
```
BMI = weight (kg) / (height (m))²
```

### BMR (Mifflin-St Jeor Equation)
```
Men:   BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
Women: BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161
```

### TDEE (Total Daily Energy Expenditure)
```
TDEE = BMR × Activity Multiplier

Activity Multipliers:
- Sedentary: 1.2
- Active: 1.55
- Athlete: 1.9
```

### Calorie Burn
```
Calories = MET × weight (kg) × time (hours)
```

### Water Intake
```
Base: 35 ml per kg of body weight
- Sedentary: 1.0x
- Active: 1.15x
- Athlete: 1.3x
```

## Testing
Run the comprehensive test suite:
```bash
python manage.py test fitnesstrack.test_utils
```

## Demo
See all functions in action:
```bash
python demo_fitness_calculator.py
```

## Error Handling
All functions return `None` for invalid input rather than raising exceptions. Always check for `None` before using results:

```python
bmi = FitnessCalculator.calculate_bmi(weight, height)
if bmi is not None:
    print(f"Your BMI is {bmi}")
else:
    print("Invalid input provided")
```

## Notes
- All functions are static methods - no need to instantiate the class
- Decimal and float types are accepted for measurements
- Activity level strings are case-insensitive
- Convenience functions available at module level for quick access
