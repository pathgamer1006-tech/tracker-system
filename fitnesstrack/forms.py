# fitnesstrack/forms.py
from django import forms
from .models import (
    UserProfile,
    ActivityLog,
    BiometricsLog,
    Goal,
    WaterIntake,
    MealLog
)


class ActivityLogForm(forms.ModelForm):
    """Form for logging activities"""
    class Meta:
        model = ActivityLog
        fields = ['activity_type', 'duration_minutes', 'distance_km', 'notes']
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'distance_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BiometricsLogForm(forms.ModelForm):
    """Form for logging biometrics"""
    class Meta:
        model = BiometricsLog
        fields = ['weight_kg', 'body_fat_percentage', 'muscle_mass_kg', 'waist_circumference_cm', 'notes']
        widgets = {
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'body_fat_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'muscle_mass_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'waist_circumference_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class WaterIntakeForm(forms.ModelForm):
    """Form for logging water intake"""
    class Meta:
        model = WaterIntake
        fields = ['milliliters', 'notes']
        widgets = {
            'milliliters': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }


class GoalForm(forms.ModelForm):
    """Form for creating fitness goals"""
    class Meta:
        model = Goal
        fields = ['goal_type', 'title', 'target_value', 'unit', 'target_date', 'notes']
        widgets = {
            'goal_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = UserProfile
        fields = ['date_of_birth', 'gender', 'height_cm', 'weight_kg', 'activity_level']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'activity_level': forms.Select(attrs={'class': 'form-control'}),
        }


class MealLogForm(forms.ModelForm):
    """Form for logging meals and nutrition"""
    class Meta:
        model = MealLog
        fields = ['meal_type', 'food_name', 'calories', 'protein_g', 'carbs_g', 'fats_g', 'serving_size', 'notes']
        widgets = {
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
            'food_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Grilled Chicken Salad'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '250'}),
            'protein_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '25.0'}),
            'carbs_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '30.0'}),
            'fats_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '10.0'}),
            'serving_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1 bowl'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any additional notes...'}),
        }

