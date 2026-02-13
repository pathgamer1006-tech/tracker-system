from django.test import TestCase
from .models import FitnessItem

class FitnessItemTestCase(TestCase):
    def test_create_fitness_item(self):
        item = FitnessItem.objects.create(name="Push-up", description="Upper body exercise", category="Strength")
        self.assertEqual(item.name, "Push-up")
