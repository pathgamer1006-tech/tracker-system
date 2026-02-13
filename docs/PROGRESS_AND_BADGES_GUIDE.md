# Progress Visualization & Badge System Guide

## Overview
The Fitness Tracker now includes comprehensive progress visualization with Chart.js charts and a gamified badge system to track achievements.

## Features

### 📊 Progress Charts

#### Accessing Charts
Navigate to the Progress Charts page via:
- Dashboard → View Progress button
- Direct URL: `/progress/`

#### Available Charts

**1. Weight Trend Line Chart**
- **Purpose**: Track weight changes over time
- **Time Range**: Last 30 days
- **Data Source**: BiometricsLog entries
- **Visual**: Blue line chart with filled area
- **Features**:
  - Hover tooltips showing exact weight values
  - Date labels on X-axis
  - Weight (kg) on Y-axis
  - Smooth curve interpolation

**2. Activity Type Distribution Pie Chart**
- **Purpose**: Visualize workout variety
- **Data Source**: All ActivityLog entries
- **Visual**: Multi-color pie chart
- **Features**:
  - Percentage calculations for each activity type
  - Legend showing all activity types
  - Hover tooltips with count and percentage
  - Color-coded segments

**3. Daily Calories Burned Bar Chart**
- **Time Range**: Last 7 days
- **Data Source**: ActivityLog calories_burned
- **Visual**: Green bar chart
- **Features**:
  - Daily calorie totals
  - Hover tooltips showing exact calories
  - Date labels on X-axis

#### Statistics Summary
The Progress Charts page also displays:
- Total workouts logged
- Total calories burned (all-time)
- Total duration in minutes
- This week's calorie burn
- Weight change over last 30 days (if available)

### 🏆 Badge System

#### Badge Types

1. **🌟 First Steps** (FIRST_WORKOUT)
   - **Requirement**: Complete your first workout
   - **Auto-awarded**: When you log your first activity

2. **🔥 7-Day Warrior** (CONSISTENCY_7)
   - **Requirement**: Log activities for 7 consecutive days
   - **Progress Tracked**: Shows current streak
   - **Algorithm**: Checks backwards from today for daily activities

3. **💪 30-Day Champion** (CONSISTENCY_30)
   - **Requirement**: Log activities for 30 consecutive days
   - **Progress Tracked**: Shows current streak
   - **Note**: Builds on 7-day consistency

4. **🔥 Calorie Crusher** (CALORIE_BURNER_1000)
   - **Requirement**: Burn 1,000 total calories
   - **Progress Tracked**: Current total / 1000 target
   - **Cumulative**: Across all activities

5. **💥 Inferno Master** (CALORIE_BURNER_5000)
   - **Requirement**: Burn 5,000 total calories
   - **Progress Tracked**: Current total / 5000 target
   - **Cumulative**: Across all activities

6. **🌅 Early Bird** (EARLY_BIRD)
   - **Requirement**: Complete a workout before 7:00 AM
   - **One-time**: Awarded on first occurrence
   - **Timezone**: Uses server timezone

7. **💧 Hydration Master** (HYDRATION_MASTER)
   - **Requirement**: Meet water intake goal for 7 consecutive days
   - **Progress Tracked**: Shows consecutive days meeting goal
   - **Target**: Based on FitnessCalculator.calculate_water_intake_target()

8. **🎯 Goal Achiever** (WEIGHT_GOAL)
   - **Requirement**: Reach your weight goal
   - **Manual Check**: Must have active weight goal
   - **Triggered**: When current_value == target_value in Goal model

#### Badge Features

**Earned Badges Section**
- Shows all badges you've earned
- Displays:
  - Badge icon
  - Badge name
  - Description with achievement details
  - Date earned
  - Green checkmark status

**Badges In Progress Section**
- Shows badges you haven't earned yet
- Displays:
  - Progress bars showing completion percentage
  - Current vs. required values
  - Grayscale locked icon (becomes colored when earned)
  - Tips on how to earn

**Streak Banner**
- Displays your current activity streak
- Animated fire emoji (🔥)
- Encouragement messages based on streak length:
  - 0 days: "Start your streak today! 🚀"
  - 1-2 days: "You're on a roll! ⚡"
  - 3-6 days: "Great momentum! 💪"
  - 7+ days: "Amazing! Keep it up! 🎉"

## Technical Implementation

### Backend Structure

**Models** (`fitnesstrack/models.py`)
```python
class Badge(models.Model):
    user = ForeignKey(User)
    badge_type = CharField(choices=BADGE_TYPES)
    earned_date = DateTimeField(auto_now_add=True)
    description = CharField(max_length=200)
    
    class Meta:
        unique_together = ['user', 'badge_type']  # One per type per user
```

**Badge System** (`fitnesstrack/badge_system.py`)
```python
class BadgeChecker:
    @staticmethod
    def check_consistency_badge(user):
        """Awards 7-day consistency badge"""
        streak = _calculate_current_streak(user)
        if streak >= 7:
            Badge.objects.create(...)
        return (awarded, streak)
    
    @staticmethod
    def _calculate_current_streak(user):
        """Counts consecutive days with activities"""
        # Iterates backward from today
        # Breaks on first day without activity
        
    @staticmethod
    def check_all_badges(user):
        """Master function to check all badges"""
        # Returns dict with badges_awarded, current_streak, total_badges
    
    @staticmethod
    def get_badge_progress(user):
        """Returns progress data for unearned badges"""
        # Returns dict with current/required/percentage
```

**Views** (`fitnesstrack/views.py`)

**progress_charts(request):**
```python
# Prepares 3 datasets:
weight_chart_data = {
    'labels': ['2025-01-01', '2025-01-02', ...],
    'values': [70.5, 70.3, ...]
}

activity_chart_data = {
    'labels': ['Running', 'Cycling', ...],
    'values': [15, 10, ...]  # counts
}

calories_chart_data = {
    'labels': ['Mon', 'Tue', ...],
    'values': [450, 300, ...]  # daily totals
}
```

**badges_view(request):**
```python
# Check and award new badges
badge_results = BadgeChecker.check_all_badges(user)

# Show success messages for new badges
for badge_type in badge_results['badges_awarded']:
    messages.success(request, '🏆 New Badge Earned!')

# Get earned badges and progress
earned_badges = BadgeChecker.get_user_badges(user)
badge_progress = BadgeChecker.get_badge_progress(user)
```

### Frontend Structure

**Chart.js Integration** (`progress_charts.html`)
- CDN: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0`
- Charts initialized in `<script>` block
- Data parsed from Django template: `{{ weight_chart_data|safe }}`

**Weight Chart Configuration:**
```javascript
new Chart(ctx, {
    type: 'line',
    data: {
        labels: weightData.labels,
        datasets: [{
            label: 'Weight (kg)',
            borderColor: '#007bff',
            tension: 0.3,  // Smooth curves
            fill: true     // Filled area
        }]
    }
});
```

**Activity Chart Configuration:**
```javascript
new Chart(ctx, {
    type: 'pie',
    data: {
        labels: activityData.labels,
        datasets: [{
            backgroundColor: pieColors,  // Multi-color
            borderWidth: 2
        }]
    }
});
```

**Responsive Design:**
- Mobile-friendly grid layouts
- Chart height adjusts for mobile (400px → 300px)
- Progress bars with percentage widths
- Flexbox for action buttons

## Usage Examples

### Earning Your First Badge

1. **Log your first activity:**
   ```
   Dashboard → Log Activity
   - Select activity type: Running
   - Duration: 30 minutes
   - Save
   ```
   → **🌟 First Steps badge earned!**

2. **Start a streak:**
   ```
   Day 1: Log running activity
   Day 2: Log cycling activity
   Day 3: Log swimming activity
   ...
   Day 7: Log any activity
   ```
   → **🔥 7-Day Warrior badge earned!**

3. **Burn calories:**
   ```
   Activity 1: Running 30 min → 300 calories
   Activity 2: Cycling 45 min → 350 calories
   Activity 3: Swimming 20 min → 200 calories
   Activity 4: Weightlifting 30 min → 180 calories
   Total: 1,030 calories
   ```
   → **🔥 Calorie Crusher badge earned!**

### Viewing Progress

1. **Check your weight trend:**
   ```
   Dashboard → View Progress → Weight Trend Chart
   - Hover over points to see exact weights
   - Observe trend line (gaining/losing)
   ```

2. **Analyze activity variety:**
   ```
   Dashboard → View Progress → Activity Breakdown
   - Pie chart shows distribution
   - Ensure balanced workout types
   ```

3. **Track weekly performance:**
   ```
   Dashboard → View Progress → Daily Calories Bar Chart
   - Compare daily calorie burns
   - Identify most active days
   ```

## URL Routes

```python
urlpatterns = [
    path('progress/', views.progress_charts, name='progress_charts'),
    path('badges/', views.badges_view, name='badges'),
]
```

**Accessible URLs:**
- Progress Charts: `http://localhost:8000/progress/`
- Badges: `http://localhost:8000/badges/`

## Database Schema

**Badge Table:**
```sql
CREATE TABLE fitnesstrack_badge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    badge_type VARCHAR(30) NOT NULL,
    earned_date DATETIME NOT NULL,
    description VARCHAR(200),
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    UNIQUE (user_id, badge_type)
);

CREATE INDEX idx_badge_user_type ON fitnesstrack_badge(user_id, badge_type);
```

## Admin Interface

**Badge Admin:**
```python
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge_type', 'earned_date']
    list_filter = ['badge_type', 'earned_date']
    search_fields = ['user__username']
    date_hierarchy = 'earned_date'
    readonly_fields = ['earned_date']
```

Accessible at: `http://localhost:8000/admin/fitnesstrack/badge/`

## Testing Badge Logic

**Manual Testing:**

1. **Test 7-day streak:**
   ```python
   # In Django shell:
   from django.contrib.auth.models import User
   from fitnesstrack.badge_system import BadgeChecker
   
   user = User.objects.get(username='testuser')
   awarded, streak = BadgeChecker.check_consistency_badge(user)
   print(f"Awarded: {awarded}, Streak: {streak}")
   ```

2. **Test calorie badges:**
   ```python
   from fitnesstrack.models import ActivityLog
   from django.db.models import Sum
   
   total = ActivityLog.objects.filter(user=user).aggregate(
       total=Sum('calories_burned')
   )['total']
   print(f"Total calories: {total}")
   
   badges = BadgeChecker.check_calorie_burner_badges(user)
   print(f"Badges awarded: {badges}")
   ```

3. **Test badge progress:**
   ```python
   progress = BadgeChecker.get_badge_progress(user)
   print(progress)
   # Output:
   # {
   #     'consistency_7': {
   #         'current': 3,
   #         'required': 7,
   #         'percentage': 42
   #     },
   #     ...
   # }
   ```

## Performance Considerations

**Chart Data Optimization:**
- Weight chart limited to 30 days (not full history)
- Calorie chart limited to 7 days
- Activity breakdown uses all data but aggregated

**Badge Checking:**
- Badges checked on badges_view page load
- Uses `.exists()` for efficiency (doesn't load full objects)
- Streak calculation breaks early when streak ends
- Safety limit: 365 days max to prevent infinite loops

**Database Queries:**
- Uses `.values_list()` for earned badges check
- `.aggregate(Sum())` for calorie totals
- `.filter().exists()` for daily activity checks
- Indexed fields: `user`, `badge_type`, `date_created`

## Customization

### Adding New Badge Types

1. **Update Badge model:**
   ```python
   BADGE_TYPES = [
       ...
       ('NEW_BADGE', 'New Achievement'),
   ]
   ```

2. **Create check function in BadgeChecker:**
   ```python
   @staticmethod
   def check_new_badge(user):
       if Badge.objects.filter(user=user, badge_type='NEW_BADGE').exists():
           return False
       
       # Your condition here
       if condition_met:
           Badge.objects.create(
               user=user,
               badge_type='NEW_BADGE',
               description='Achievement description'
           )
           return True
       return False
   ```

3. **Add to check_all_badges():**
   ```python
   if BadgeChecker.check_new_badge(user):
       results['badges_awarded'].append('NEW_BADGE')
   ```

4. **Update badge icon property:**
   ```python
   icon_map = {
       ...
       'NEW_BADGE': '🎉',
   }
   ```

5. **Update badges.html template:**
   Add section in "Badges In Progress"

6. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Customizing Chart Appearance

**Change colors:**
```javascript
// In progress_charts.html <script> section
const pieColors = [
    '#FF6384',  // Pink
    '#36A2EB',  // Blue
    '#FFCE56',  // Yellow
    // Add more colors...
];
```

**Adjust chart height:**
```css
.chart-wrapper {
    height: 500px;  /* Default: 400px */
}
```

**Change time ranges:**
```python
# In views.py progress_charts()
thirty_days_ago = timezone.now() - timedelta(days=60)  # Show 60 days
```

## Troubleshooting

### Charts Not Displaying

**Issue**: Blank chart areas  
**Solution**:
1. Check browser console for JavaScript errors
2. Verify Chart.js CDN is loading: `view-source:` and find `<script src="https://cdn.jsdelivr.net/npm/chart.js"`
3. Check that data is not empty: `{{ weight_chart_data }}` in template

### No Badges Showing

**Issue**: Badge page empty  
**Solution**:
1. Check if BadgeChecker is importing correctly
2. Verify Badge model migrated: `python manage.py showmigrations`
3. Check for errors in badge_system.py logic
4. Test in Django shell:
   ```python
   from fitnesstrack.badge_system import BadgeChecker
   from django.contrib.auth.models import User
   user = User.objects.first()
   BadgeChecker.check_all_badges(user)
   ```

### Streak Not Calculating

**Issue**: Streak always shows 0  
**Solution**:
1. Verify activities have `date_created` field populated
2. Check timezone settings in settings.py
3. Test streak calculation:
   ```python
   from fitnesstrack.badge_system import BadgeChecker
   streak = BadgeChecker._calculate_current_streak(user)
   print(f"Current streak: {streak}")
   ```

### Migration Errors

**Issue**: Badge model migration fails  
**Solution**:
```bash
# Reset migrations (WARNING: loses data)
python manage.py migrate fitnesstrack zero
python manage.py makemigrations fitnesstrack
python manage.py migrate

# Or fake the migration
python manage.py migrate fitnesstrack 0004_badge --fake
```

## Best Practices

1. **Log activities daily** to build streaks
2. **Check badges page regularly** for new achievements
3. **Review progress charts weekly** to track trends
4. **Update biometrics consistently** for accurate weight chart
5. **Set realistic goals** for weight achievements
6. **Vary activity types** for balanced pie chart
7. **Log early morning workouts** for Early Bird badge
8. **Track water intake** for Hydration Master badge

## Future Enhancements

Potential additions:
- **Social features**: Share badges with friends
- **Leaderboards**: Compare streaks with other users
- **Custom badges**: Admin-created achievements
- **Badge levels**: Bronze/Silver/Gold tiers
- **Monthly challenges**: Time-limited badges
- **Notifications**: Push alerts for new badges
- **Export charts**: Download as PNG/PDF
- **More chart types**: Scatter plots, heat maps
- **Goal-based badges**: Linked to Goal model
- **Multi-month trends**: 3-month, 6-month, 1-year charts

---

**Created**: December 2024  
**Version**: 1.0  
**Author**: Fitness Tracker Development Team
