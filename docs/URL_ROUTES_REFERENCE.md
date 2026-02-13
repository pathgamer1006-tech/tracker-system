# Fitness Tracker - URL Routes Quick Reference

## All Available URLs

### 🏠 Main Dashboard
| URL | Name | View | Description |
|-----|------|------|-------------|
| `/` | `dashboard` | `dashboard` | Main overview with metrics, today's summary, and quick actions |

### 👤 User Profile
| URL | Name | View | Description |
|-----|------|------|-------------|
| `/profile/update/` | `update_profile` | `update_profile` | Edit user profile (height, weight, gender, DOB, activity level) |

### 🏃 Activity Tracking
| URL | Name | View | Description |
|-----|------|------|-------------|
| `/activities/` | `activity_list` | `activity_list` | View all logged activities |
| `/activities/log/` | `log_activity` | `log_activity` | Log new workout (auto-calculates calories) |
| `/activities/<int:pk>/` | `activity_detail` | `activity_detail` | View single activity details |
| `/activities/<int:pk>/edit/` | `edit_activity` | `edit_activity` | Update existing activity |
| `/activities/<int:pk>/delete/` | `delete_activity` | `ActivityDeleteView` | Delete activity (with confirmation) |

### ⚖️ Biometrics Tracking
| URL | Name | View | Description |
|-----|------|------|-------------|
| `/biometrics/update/` | `update_biometrics` | `update_biometrics` | Log weight, body fat, muscle mass (auto-calculates BMI) |
| `/biometrics/history/` | `biometrics_history` | `biometrics_history` | View historical biometrics logs |

### 💧 Water Intake
| URL | Name | View | Description |
|-----|------|------|-------------|
| `/water/log/` | `log_water` | `log_water` | Add water intake entry |
| `/water/history/` | `water_history` | `water_history` | View daily water intake history |

### 🎯 Goal Management
| URL | Name | View | Description |
|-----|------|------|-------------|
| `/goals/` | `goal_list` | `goal_list` | View all fitness goals |
| `/goals/create/` | `create_goal` | `create_goal` | Create new fitness goal |
| `/goals/<int:pk>/update/` | `update_goal` | `update_goal` | Update goal progress and status |

### 📊 Progress Visualization (NEW)
| URL | Name | View | Description |
|-----|------|------|-------------|
| `/progress/` | `progress_charts` | `progress_charts` | View 3 charts: Weight Trend (30d line), Activity Distribution (pie), Calories Burned (7d bar) |

### 🏆 Badge System (NEW)
| URL | Name | View | Description |
|-----|------|------|-------------|
| `/badges/` | `badges` | `badges_view` | View earned badges, track progress, see current streak |

### 🔧 Admin Interface
| URL | Description |
|-----|-------------|
| `/admin/` | Django admin panel (requires superuser) |
| `/admin/fitnesstrack/userprofile/` | Manage user profiles |
| `/admin/fitnesstrack/activitylog/` | Manage activities |
| `/admin/fitnesstrack/biometricslog/` | Manage biometrics logs |
| `/admin/fitnesstrack/goal/` | Manage goals |
| `/admin/fitnesstrack/waterintake/` | Manage water intake logs |
| `/admin/fitnesstrack/badge/` | Manage badges (NEW) |

## URL Patterns by Feature

### Complete CRUD for Activities
```
CREATE: /activities/log/                (POST form)
READ:   /activities/                    (List all)
        /activities/<id>/                (Single detail)
UPDATE: /activities/<id>/edit/          (POST form)
DELETE: /activities/<id>/delete/        (POST confirmation)
```

### Update-Only for Profile & Biometrics
```
Profile:    /profile/update/            (No list/detail/delete)
Biometrics: /biometrics/update/         (Create new log)
            /biometrics/history/        (View all logs)
```

### Create & List for Water & Goals
```
Water:  /water/log/                     (Add entry)
        /water/history/                 (View all)

Goals:  /goals/create/                  (Create goal)
        /goals/                         (List all)
        /goals/<id>/update/             (Update progress)
```

## HTTP Methods by Endpoint

### GET Requests (View Pages)
- `/` - Dashboard
- `/activities/` - Activity list
- `/activities/<id>/` - Activity detail
- `/activities/log/` - Activity form (empty)
- `/activities/<id>/edit/` - Activity form (prefilled)
- `/profile/update/` - Profile form (prefilled)
- `/biometrics/update/` - Biometrics form (empty)
- `/biometrics/history/` - Biometrics list
- `/water/log/` - Water form (empty)
- `/water/history/` - Water list
- `/goals/create/` - Goal form (empty)
- `/goals/` - Goal list
- `/goals/<id>/update/` - Goal form (prefilled)
- `/progress/` - Charts page (NEW)
- `/badges/` - Badges page (NEW)

### POST Requests (Form Submissions)
- `/activities/log/` - Submit new activity
- `/activities/<id>/edit/` - Update activity
- `/activities/<id>/delete/` - Confirm deletion
- `/profile/update/` - Update profile
- `/biometrics/update/` - Log biometrics
- `/water/log/` - Log water intake
- `/goals/create/` - Create goal
- `/goals/<id>/update/` - Update goal

## URL Parameters

### Primary Key (pk)
Used in activity, goal CRUD:
```python
path('<int:pk>/', views.activity_detail, name='activity_detail')
path('<int:pk>/edit/', views.edit_activity, name='edit_activity')
path('<int:pk>/delete/', ActivityDeleteView.as_view(), name='delete_activity')
path('<int:pk>/update/', views.update_goal, name='update_goal')
```

## Authentication Requirements

### All URLs Require Login
Every view uses `@login_required` decorator or `LoginRequiredMixin`:
```python
@login_required
def dashboard(request):
    ...

class ActivityDeleteView(LoginRequiredMixin, DeleteView):
    ...
```

**If not logged in**: Redirects to `/admin/login/?next=/original-url/`

## URL Naming Convention

### Pattern
```
<action>_<model>

Examples:
- log_activity      (create)
- activity_list     (read all)
- activity_detail   (read one)
- edit_activity     (update)
- delete_activity   (delete)
- update_profile
- create_goal
- progress_charts   (NEW)
- badges            (NEW)
```

## Using URLs in Templates

### Template URL Tags
```django
{% url 'dashboard' %}
{% url 'log_activity' %}
{% url 'activity_detail' activity.pk %}
{% url 'edit_activity' activity.pk %}
{% url 'delete_activity' activity.pk %}
{% url 'update_profile' %}
{% url 'update_biometrics' %}
{% url 'log_water' %}
{% url 'water_history' %}
{% url 'create_goal' %}
{% url 'goal_list' %}
{% url 'update_goal' goal.pk %}
{% url 'progress_charts' %}
{% url 'badges' %}
```

### Example in HTML
```html
<a href="{% url 'dashboard' %}">Back to Dashboard</a>
<a href="{% url 'log_activity' %}">Log Activity</a>
<a href="{% url 'activity_detail' activity.pk %}">View Details</a>
<a href="{% url 'progress_charts' %}">View Progress 📊</a>
<a href="{% url 'badges' %}">View Badges 🏆</a>
```

## Using URLs in Views

### Redirect After Form Submission
```python
from django.shortcuts import redirect

def log_activity(request):
    if request.method == 'POST':
        # Process form...
        return redirect('activity_list')
```

### Reverse URL Lookup
```python
from django.urls import reverse

success_url = reverse('dashboard')
detail_url = reverse('activity_detail', kwargs={'pk': activity.pk})
```

## URL Configuration Files

### Project URLs (`fitness/urls.py`)
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('fitnesstrack.urls')),
]
```

### App URLs (`fitnesstrack/urls.py`)
```python
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Profile
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Activities
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/log/', views.log_activity, name='log_activity'),
    path('activities/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('activities/<int:pk>/edit/', views.edit_activity, name='edit_activity'),
    path('activities/<int:pk>/delete/', views.ActivityDeleteView.as_view(), name='delete_activity'),
    
    # Biometrics
    path('biometrics/update/', views.update_biometrics, name='update_biometrics'),
    path('biometrics/history/', views.biometrics_history, name='biometrics_history'),
    
    # Water
    path('water/log/', views.log_water, name='log_water'),
    path('water/history/', views.water_history, name='water_history'),
    
    # Goals
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.create_goal, name='create_goal'),
    path('goals/<int:pk>/update/', views.update_goal, name='update_goal'),
    
    # Progress & Badges (NEW)
    path('progress/', views.progress_charts, name='progress_charts'),
    path('badges/', views.badges_view, name='badges'),
]
```

## API-Style URL Planning (Future)

For REST API implementation:
```
GET    /api/activities/              - List all activities
POST   /api/activities/              - Create activity
GET    /api/activities/<id>/         - Get activity detail
PUT    /api/activities/<id>/         - Update activity
DELETE /api/activities/<id>/         - Delete activity

GET    /api/badges/                  - List earned badges
GET    /api/badges/progress/         - Get badge progress
POST   /api/badges/check/            - Check and award badges

GET    /api/charts/weight/           - Weight trend data
GET    /api/charts/activities/       - Activity distribution data
GET    /api/charts/calories/         - Calorie burn data
```

## Quick Navigation Map

```
Homepage (/)
    │
    ├─→ Log Activity (/activities/log/)
    │       └─→ Activity List (/activities/)
    │               └─→ Activity Detail (/activities/<id>/)
    │                       ├─→ Edit (/activities/<id>/edit/)
    │                       └─→ Delete (/activities/<id>/delete/)
    │
    ├─→ Update Profile (/profile/update/)
    │
    ├─→ Update Biometrics (/biometrics/update/)
    │       └─→ Biometrics History (/biometrics/history/)
    │
    ├─→ Log Water (/water/log/)
    │       └─→ Water History (/water/history/)
    │
    ├─→ Create Goal (/goals/create/)
    │       └─→ Goal List (/goals/)
    │               └─→ Update Goal (/goals/<id>/update/)
    │
    ├─→ View Progress (/progress/) 📊 NEW
    │       └─→ Weight Trend Chart
    │       └─→ Activity Distribution Chart
    │       └─→ Calorie Burn Chart
    │
    └─→ View Badges (/badges/) 🏆 NEW
            └─→ Earned Badges
            └─→ Badges In Progress
            └─→ Streak Counter
```

## Common URL Patterns

### Back to Dashboard Links
```html
<a href="{% url 'dashboard' %}" class="btn">← Back to Dashboard</a>
```

### View All Links
```html
<a href="{% url 'activity_list' %}">View All Activities →</a>
<a href="{% url 'biometrics_history' %}">View History →</a>
<a href="{% url 'water_history' %}">View Water Logs →</a>
<a href="{% url 'goal_list' %}">View All Goals →</a>
```

### Quick Action Buttons
```html
<div class="quick-actions">
    <a href="{% url 'log_activity' %}" class="btn btn-primary">📝 Log Activity</a>
    <a href="{% url 'update_biometrics' %}" class="btn btn-secondary">⚖️ Update Weight</a>
    <a href="{% url 'log_water' %}" class="btn btn-info">💧 Log Water</a>
    <a href="{% url 'update_profile' %}" class="btn btn-outline">👤 Update Profile</a>
    <a href="{% url 'progress_charts' %}" class="btn btn-success">📊 View Progress</a>
    <a href="{% url 'badges' %}" class="btn btn-warning">🏆 View Badges</a>
</div>
```

## Testing URLs

### Browser Testing
```
http://localhost:8000/
http://localhost:8000/activities/
http://localhost:8000/activities/log/
http://localhost:8000/activities/1/
http://localhost:8000/activities/1/edit/
http://localhost:8000/profile/update/
http://localhost:8000/biometrics/update/
http://localhost:8000/water/log/
http://localhost:8000/goals/create/
http://localhost:8000/progress/           # NEW
http://localhost:8000/badges/             # NEW
http://localhost:8000/admin/
```

### Django Shell Testing
```python
python manage.py shell

from django.urls import reverse

# Get URL paths
reverse('dashboard')                # '/'
reverse('log_activity')             # '/activities/log/'
reverse('activity_detail', args=[1]) # '/activities/1/'
reverse('progress_charts')          # '/progress/'
reverse('badges')                   # '/badges/'
```

## URL Security Notes

1. **All views require authentication** - `@login_required`
2. **User isolation** - Queries filtered by `request.user`
3. **CSRF protection** - All forms include `{% csrf_token %}`
4. **Safe redirects** - Only internal URLs
5. **Primary key validation** - Django validates integer PKs
6. **404 on invalid IDs** - `get_object_or_404()`

---

**Last Updated**: December 2024  
**Total URLs**: 20+ (including admin)  
**New URLs**: 2 (Progress Charts, Badges)
