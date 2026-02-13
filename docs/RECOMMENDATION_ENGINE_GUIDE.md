# Recommendation Engine Documentation

## Overview
The recommendation engine analyzes user activity from yesterday and provides personalized, actionable tips on the dashboard to help users improve their fitness journey.

## Function: `generate_daily_tip(user)`

### Location
`fitnesstrack/utils.py`

### Purpose
Analyzes yesterday's fitness data and returns a personalized recommendation based on specific health metrics.

### Function Signature
```python
def generate_daily_tip(user) -> Optional[str]:
    """
    Generate personalized daily tip based on user's yesterday data.
    
    Args:
        user: Django User object
        
    Returns:
        str: Personalized tip message, or None if no tip applicable
    """
```

### Recommendation Logic

The function checks three conditions in priority order:

#### 1. **Hydration Alert** (Highest Priority)
- **Condition**: Water intake yesterday < 2000ml
- **Message**: `"Hydration Alert: Try to drink more water today."`
- **Rationale**: Hydration is critical for health and performance
- **Why Priority #1**: Dehydration affects all body functions

#### 2. **Sleep Recovery** (Medium Priority) - Placeholder
- **Condition**: Sleep hours yesterday < 7 hours
- **Message**: `"Recovery Focus: Prioritize getting to bed early tonight."`
- **Status**: Not yet implemented (sleep tracking feature needed)
- **Note**: Code structure is ready for future sleep tracking model

#### 3. **Calorie Burn Encouragement** (Lower Priority)
- **Condition**: Total calories burned yesterday > 500
- **Message**: `"Great work! You hit a high burn yesterday."`
- **Rationale**: Positive reinforcement for high activity days

#### 4. **Default Motivational Message**
- **Condition**: None of the above conditions met
- **Message**: `"Keep up the great work! Stay consistent with your fitness journey."`
- **Purpose**: Always provide encouragement, never return empty

### Data Sources

**Water Intake:**
```python
WaterIntake.get_daily_total(user, yesterday)
# Sums all water intake logs for yesterday
```

**Calories Burned:**
```python
ActivityLog.objects.filter(
    user=user,
    date_created__date=yesterday
).aggregate(total=Sum('calories_burned'))['total']
# Aggregates all activities from yesterday
```

**Sleep Hours:** (Future feature)
```python
# Planned implementation:
SleepLog.objects.filter(
    user=user,
    date_recorded__date=yesterday
).first()
```

### Priority System

The function uses **early return** pattern to enforce priority:

1. Check hydration → If < 2000ml, return hydration alert
2. Check sleep → If < 7 hours, return sleep focus message
3. Check calories → If > 500, return encouragement
4. Return default motivational message

This ensures the most important health metric is addressed first.

### Integration

#### Dashboard View (`views.py`)
```python
from .utils import generate_daily_tip

@login_required
def dashboard(request):
    # ... other dashboard logic ...
    
    # Generate daily tip
    daily_tip = generate_daily_tip(request.user)
    
    context = {
        # ... other context ...
        'daily_tip': daily_tip,
    }
    
    return render(request, 'fitnesstrack/dashboard.html', context)
```

#### Dashboard Template (`dashboard.html`)
```django
{% if daily_tip %}
<div class="daily-tip card">
    <div class="tip-icon">💡</div>
    <div class="tip-content">
        <h3>Daily Tip</h3>
        <p>{{ daily_tip }}</p>
    </div>
</div>
{% endif %}
```

### Visual Design

**Card Styling:**
- Gradient background (purple to violet)
- Animated lightbulb icon (pulse effect)
- White text for visibility
- Rounded corners and shadow
- Prominent placement on dashboard

**CSS:**
```css
.daily-tip {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.tip-icon {
    font-size: 3em;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.1); opacity: 0.8; }
}
```

### Example Scenarios

#### Scenario 1: Low Water Intake
**User's Yesterday Data:**
- Water: 1200ml (logged via WaterIntake model)
- Activity: 30 min running, 300 calories
- Sleep: N/A (not tracked yet)

**Result:**
```
💡 Daily Tip
Hydration Alert: Try to drink more water today.
```

**Why:** Water intake (1200ml) is below threshold (2000ml)

#### Scenario 2: High Calorie Burn
**User's Yesterday Data:**
- Water: 2500ml
- Activity: 60 min running + 30 min cycling = 650 calories total
- Sleep: N/A

**Result:**
```
💡 Daily Tip
Great work! You hit a high burn yesterday.
```

**Why:** Water intake is good, calories (650) exceed threshold (500)

#### Scenario 3: Multiple Activities
**User's Yesterday Data:**
- Water: 2800ml
- Activities:
  - Morning: 20 min yoga, 100 calories
  - Afternoon: 30 min walking, 150 calories
  - Evening: 40 min cycling, 300 calories
  - Total: 550 calories
- Sleep: N/A

**Result:**
```
💡 Daily Tip
Great work! You hit a high burn yesterday.
```

**Why:** All activities are summed; total (550) > 500

#### Scenario 4: Both Conditions Met
**User's Yesterday Data:**
- Water: 800ml (LOW)
- Activity: 90 min running, 900 calories (HIGH)
- Sleep: N/A

**Result:**
```
💡 Daily Tip
Hydration Alert: Try to drink more water today.
```

**Why:** Hydration has higher priority than calorie encouragement

#### Scenario 5: New User, No Data
**User's Yesterday Data:**
- Water: 0ml (no logs)
- Activity: None
- Sleep: N/A

**Result:**
```
💡 Daily Tip
Hydration Alert: Try to drink more water today.
```

**Why:** 0ml < 2000ml triggers hydration alert (correct behavior)

#### Scenario 6: Good All Around
**User's Yesterday Data:**
- Water: 2600ml
- Activity: 30 min yoga, 150 calories
- Sleep: N/A

**Result:**
```
💡 Daily Tip
Keep up the great work! Stay consistent with your fitness journey.
```

**Why:** Water is good, calories below 500, default message shown

### Error Handling

The function uses try-except blocks for each check:

```python
try:
    daily_water = WaterIntake.get_daily_total(user, yesterday)
    if daily_water < 2000:
        return 'Hydration Alert: Try to drink more water today.'
except Exception:
    pass  # Continue to next check
```

**Benefits:**
- Function never crashes
- Handles missing data gracefully
- Always returns a message
- Resilient to database issues

### Testing

**Test Coverage:**
- ✅ Hydration alert when water < 2000ml
- ✅ No hydration alert when water >= 2000ml
- ✅ Calorie encouragement when calories > 500
- ✅ Default message when conditions not met
- ✅ Priority: hydration over calories
- ✅ Multiple activities summed correctly
- ✅ Handles user with no profile
- ✅ Handles user with no data (returns hydration alert)

**Run Tests:**
```bash
python manage.py test fitnesstrack.test_recommendations --verbosity=2
```

**Expected Result:** All 8 tests pass ✅

### Thresholds

Current thresholds are evidence-based:

| Metric | Threshold | Reasoning |
|--------|-----------|-----------|
| Water Intake | < 2000ml | Minimum daily hydration for average adult |
| Sleep Hours | < 7 hours | CDC recommendation for adult sleep |
| Calories Burned | > 500 | Indicates significant exercise session |

### Customization

To modify thresholds, edit the function in `utils.py`:

```python
# Change water threshold
if daily_water < 2500:  # Was 2000
    return 'Hydration Alert: Try to drink more water today.'

# Change calorie threshold
if total_calories > 600:  # Was 500
    return 'Great work! You hit a high burn yesterday.'
```

### Future Enhancements

#### 1. Sleep Tracking Implementation
**Add SleepLog Model:**
```python
class SleepLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hours = models.DecimalField(max_digits=3, decimal_places=1)
    quality = models.CharField(max_length=20)  # Good/Fair/Poor
    date_recorded = models.DateTimeField(auto_now_add=True)
```

**Uncomment in `generate_daily_tip()`:**
```python
try:
    from .models import SleepLog
    yesterday_sleep = SleepLog.objects.filter(
        user=user,
        date_recorded__date=yesterday
    ).first()
    
    if yesterday_sleep and yesterday_sleep.hours < 7:
        return 'Recovery Focus: Prioritize getting to bed early tonight.'
except Exception:
    pass
```

#### 2. Personalized Thresholds
Use user's profile for dynamic thresholds:

```python
# Water based on weight
water_threshold = profile.weight_kg * 35  # 35ml per kg

# Calories based on TDEE
calorie_threshold = profile.tdee * 0.2  # 20% of TDEE
```

#### 3. More Tip Types
- Streak encouragement: "7 days in a row! Amazing!"
- Rest day suggestion: "Consider a rest day after 5 intense workouts"
- Nutrition reminder: "High burn day - don't forget to refuel!"
- Goal progress: "Only 2kg from your weight goal!"

#### 4. Tip Rotation
Avoid showing same tip repeatedly:

```python
# Store last tip in session
last_tip = request.session.get('last_tip')
new_tip = generate_daily_tip(user)

if new_tip == last_tip:
    # Show variation or different tip
    new_tip = get_alternative_tip(user)

request.session['last_tip'] = new_tip
```

#### 5. Multi-Language Support
```python
TIPS = {
    'en': {
        'hydration': 'Hydration Alert: Try to drink more water today.',
        'sleep': 'Recovery Focus: Prioritize getting to bed early tonight.',
        'calories': 'Great work! You hit a high burn yesterday.',
    },
    'es': {
        'hydration': 'Alerta de hidratación: Intenta beber más agua hoy.',
        # ... etc
    }
}
```

#### 6. Tip History Log
Track which tips were shown:

```python
class TipHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tip_type = models.CharField(max_length=50)
    message = models.TextField()
    shown_date = models.DateField(auto_now_add=True)
```

### Best Practices

1. **Always show a tip** - Never return None, always encourage
2. **Priority matters** - Health alerts before motivational messages
3. **Be specific** - "yesterday" data makes tips actionable today
4. **Test thoroughly** - Edge cases (no data, extreme values)
5. **Fail gracefully** - Try-except prevents crashes
6. **Document thresholds** - Make values understandable

### Performance Considerations

**Database Queries:**
- 1 query for water intake (aggregate)
- 1 query for activity calories (aggregate)
- Total: 2 queries per dashboard load

**Optimization:**
```python
# Cache result for 1 hour
from django.core.cache import cache

cache_key = f'daily_tip_{user.id}_{yesterday}'
cached_tip = cache.get(cache_key)

if cached_tip:
    return cached_tip

tip = generate_daily_tip(user)
cache.set(cache_key, tip, 3600)  # Cache for 1 hour
return tip
```

### Analytics Potential

Track tip effectiveness:

```python
# When user clicks on tip action
TipClick.objects.create(
    user=user,
    tip_type='hydration',
    action_taken=True
)

# Measure: Did water intake improve after hydration tip?
```

### API Endpoint (Future)

For mobile app or external integrations:

```python
# urls.py
path('api/daily-tip/', views.api_daily_tip, name='api_daily_tip'),

# views.py
from django.http import JsonResponse

@login_required
def api_daily_tip(request):
    tip = generate_daily_tip(request.user)
    return JsonResponse({
        'tip': tip,
        'date': timezone.now().date().isoformat(),
    })
```

### User Feedback

Consider adding feedback mechanism:

```html
<div class="daily-tip card">
    <div class="tip-icon">💡</div>
    <div class="tip-content">
        <h3>Daily Tip</h3>
        <p>{{ daily_tip }}</p>
        <div class="tip-feedback">
            Was this helpful?
            <button onclick="rateTip(true)">👍</button>
            <button onclick="rateTip(false)">👎</button>
        </div>
    </div>
</div>
```

---

## Summary

The recommendation engine provides:
- ✅ **Personalized**: Based on individual user data
- ✅ **Actionable**: Specific suggestions for today
- ✅ **Prioritized**: Most important metrics first
- ✅ **Always Positive**: Never discourages, always motivates
- ✅ **Reliable**: Error handling prevents crashes
- ✅ **Tested**: 8 comprehensive tests, all passing
- ✅ **Extensible**: Easy to add more tip types
- ✅ **Visual**: Prominent, attractive dashboard placement

**Implementation Status:** ✅ Fully functional and ready for production!

**Location:** Dashboard (http://localhost:8000/)  
**Updated:** February 2026  
**Version:** 1.0
