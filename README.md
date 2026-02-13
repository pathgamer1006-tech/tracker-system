# 🏃‍♂️ Fitness Tracker - Django Web Application

A comprehensive fitness tracking application built with Django 4.2.7, featuring progress visualization, achievement badges, and intelligent fitness calculations.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Django](https://img.shields.io/badge/Django-4.2.7-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Tests](https://img.shields.io/badge/Tests-29%20Passing-brightgreen)

## ✨ Key Features

### 📊 Activity Tracking
- Log workouts with automatic calorie calculation
- Support for 7 activity types (Running, Cycling, Swimming, Weightlifting, Walking, Yoga, HIIT)
- Duration, distance, and notes tracking
- Historical activity logs with full CRUD operations

### ⚖️ Biometrics Monitoring
- Weight tracking with historical logs
- Body fat percentage and muscle mass tracking
- Automatic BMI calculation
- 30-day weight trend visualization

### 💧 Hydration Tracking
- Daily water intake logging
- Personalized water intake targets
- Progress bars showing daily goal achievement
- Weekly hydration consistency tracking

### 🎯 Goal Management
- Set and track fitness goals
- Multiple goal types: Weight, Calories, Distance, Duration, Body Fat, Muscle Mass
- Progress percentage tracking
- Active/Completed/Abandoned status

### 📈 Progress Visualization (NEW!)
- **Weight Trend Chart**: Interactive line chart showing 30-day weight history
- **Activity Distribution**: Pie chart displaying workout variety
- **Calorie Burn Trend**: Bar chart of daily calories burned (7 days)
- Overall statistics dashboard
- Powered by Chart.js 4.4.0

### 🏆 Achievement Badges (NEW!)
- **8 Badge Types**:
  - 🌟 First Steps - Complete first workout
  - 🔥 7-Day Warrior - 7-day activity streak
  - 💪 30-Day Champion - 30-day activity streak
  - 🔥 Calorie Crusher - Burn 1,000 calories
  - 💥 Inferno Master - Burn 5,000 calories
  - 🌅 Early Bird - Workout before 7 AM
  - 💧 Hydration Master - Meet water goal for 7 days
  - 🎯 Goal Achiever - Reach weight goal
- Real-time progress tracking
- Animated streak counter
- Automatic badge detection and awarding

### 🧮 Intelligent Calculations
- **BMI** (Body Mass Index) - Automatic calculation and categorization
- **BMR** (Basal Metabolic Rate) - Mifflin-St Jeor equation
- **TDEE** (Total Daily Energy Expenditure) - Activity-adjusted calorie target
- **Calorie Burn** - MET-based estimation for each activity type
- **Water Intake Target** - Personalized based on weight and activity level

## 🚀 Quick Start

### Prerequisites
- Python 3.14+
- pip (Python package manager)
- Django 4.2.7

### Installation

1. **Clone the repository**
```bash
cd "c:\Users\SCATTER ONLY\fitness"
```

2. **Install dependencies**
```bash
pip install django
```

3. **Run migrations**
```bash
python manage.py migrate
```

4. **Create superuser**
```bash
python manage.py createsuperuser
```

5. **Start development server**
```bash
python manage.py runserver
```

6. **Access the application**
- Web App: http://localhost:8000/
- Admin Panel: http://localhost:8000/admin/

## 📁 Project Structure

```
fitness/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database
├── fitness/                 # Project settings
│   ├── __init__.py
│   ├── settings.py         # Configuration
│   ├── urls.py             # Main URL routing
│   ├── wsgi.py             # WSGI config
│   └── asgi.py             # ASGI config
├── fitnesstrack/           # Main application
│   ├── models.py           # 6 database models
│   ├── views.py            # 15+ view functions
│   ├── forms.py            # 5 ModelForms
│   ├── urls.py             # App URL routing
│   ├── admin.py            # Admin interface config
│   ├── tests.py            # 29 unit tests
│   ├── utils.py            # Fitness calculations
│   ├── badge_system.py     # Badge logic (NEW)
│   ├── migrations/         # Database migrations
│   └── templates/          # HTML templates
│       └── fitnesstrack/
│           ├── base.html               # Base template
│           ├── dashboard.html          # Main dashboard
│           ├── progress_charts.html    # Charts page (NEW)
│           ├── badges.html             # Badges page (NEW)
│           ├── fit_form.html           # Generic form
│           ├── fit_list.html           # Generic list
│           ├── fit_detail.html         # Activity detail
│           ├── fit_confirm_delete.html # Delete confirmation
│           ├── atoms/                  # Atomic components
│           │   ├── button.html
│           │   └── field.html
│           ├── molecules/
│           │   └── fit_row.html
│           └── organisms/
│               └── fit_table.html
├── security_management/    # Security app (placeholder)
└── docs/                   # Documentation
    ├── SETUP_GUIDE.md
    ├── MODELS_DOCUMENTATION.md
    ├── VIEWS_GUIDE.md
    ├── TESTING_GUIDE.md
    ├── PROGRESS_AND_BADGES_GUIDE.md    # Charts & badges guide (NEW)
    └── COMPLETE_FEATURE_SUMMARY.md     # Feature summary (NEW)
```

## 📖 Documentation

Comprehensive documentation available in the `docs/` directory:

1. **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Installation and configuration
2. **[MODELS_DOCUMENTATION.md](docs/MODELS_DOCUMENTATION.md)** - Database models reference
3. **[VIEWS_GUIDE.md](docs/VIEWS_GUIDE.md)** - Views and URL endpoints
4. **[TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - Unit testing examples
5. **[PROGRESS_AND_BADGES_GUIDE.md](docs/PROGRESS_AND_BADGES_GUIDE.md)** - Charts and badges system (NEW)
6. **[COMPLETE_FEATURE_SUMMARY.md](docs/COMPLETE_FEATURE_SUMMARY.md)** - Full feature list (NEW)

## 🎯 Usage Examples

### Log an Activity
```python
# Navigate to http://localhost:8000/activities/log/
1. Select activity type: Running
2. Enter duration: 30 minutes
3. Enter distance: 5 km (optional)
4. Add notes (optional)
5. Click "Save Activity"
# Calories automatically calculated based on your weight!
```

### Track Your Weight
```python
# Navigate to http://localhost:8000/biometrics/update/
1. Enter current weight: 70.5 kg
2. Enter body fat %: 15.2% (optional)
3. Enter muscle mass: 55.0 kg (optional)
4. Click "Save Biometrics"
# BMI automatically calculated!
# Weight chart updates automatically!
```

### View Progress Charts
```python
# Navigate to http://localhost:8000/progress/
# See three interactive charts:
1. Weight Trend - Line chart (30 days)
2. Activity Distribution - Pie chart (all-time)
3. Calories Burned - Bar chart (7 days)
# Plus overall statistics summary!
```

### Earn Badges
```python
# Navigate to http://localhost:8000/badges/
# Log activities daily to build streaks
# Check your progress toward unearned badges
# See animated streak counter with fire emoji!
```

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test fitnesstrack

# Run specific test class
python manage.py test fitnesstrack.tests.UserProfileTestCase

# Run with verbose output
python manage.py test fitnesstrack --verbosity=2
```

**Test Results**: ✅ 29 tests passing

## 🗄️ Database Models

### 1. UserProfile
Extended user profile with health metrics

### 2. ActivityLog
Daily workout and exercise tracking

### 3. BiometricsLog
Historical body measurements (weight, body fat, muscle mass)

### 4. Goal
Fitness goals with progress tracking

### 5. WaterIntake
Daily hydration logs

### 6. Badge (NEW)
Achievement badges for milestones

See [MODELS_DOCUMENTATION.md](docs/MODELS_DOCUMENTATION.md) for detailed schema.

## 🎨 Tech Stack

**Backend:**
- Django 4.2.7
- Python 3.14
- SQLite database

**Frontend:**
- HTML5
- CSS3 (custom styling)
- JavaScript (ES6)
- Chart.js 4.4.0 (NEW)

**Libraries:**
- Django ORM for database
- Django Forms for validation
- Django Admin for management
- Django Messages for notifications

## 🔐 Security Features

- ✅ Login required for all views (`@login_required`)
- ✅ CSRF protection on forms
- ✅ User data isolation (all queries filtered by `request.user`)
- ✅ Unique constraints prevent duplicate badges
- ✅ Input validation with Django validators
- ✅ XSS protection with template auto-escaping

## 📊 Key Algorithms

### Calorie Burn Calculation
```python
calories = MET × weight_kg × (duration_minutes / 60)

MET values:
- Running: 9.8
- Cycling: 7.5
- Swimming: 8.0
- Weightlifting: 6.0
- Walking: 3.8
- Yoga: 2.5
- HIIT: 8.0
```

### BMR (Mifflin-St Jeor Equation)
```python
Men: 10 × weight + 6.25 × height - 5 × age + 5
Women: 10 × weight + 6.25 × height - 5 × age - 161
```

### Streak Calculation (NEW)
```python
# Iterates backward from today
# Counts consecutive days with activities
# Breaks on first day without activity
# Safety limit: 365 days
```

## 🎯 Feature Highlights

### Auto-Calculation Engine
- Calories burned automatically calculated for each activity
- No manual calorie entry needed
- Uses scientifically-backed MET (Metabolic Equivalent of Task) values

### Dual-Update System
- BiometricsLog maintains historical records
- UserProfile.weight_kg stores current value
- Best of both worlds approach

### Chart.js Integration (NEW)
- Interactive data visualization
- Hover tooltips with exact values
- Responsive design for mobile
- Multiple chart types (line, pie, bar)

### Gamification System (NEW)
- 8 achievement badge types
- Progress bars showing completion percentage
- Real-time streak counter
- Automatic badge detection

### Atomic Design Templates
- Reusable components (atoms, molecules, organisms)
- Easy maintenance and consistency
- DRY (Don't Repeat Yourself) principle

## 🌟 Pages Overview

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Main overview with metrics and quick actions |
| Log Activity | `/activities/log/` | Create new workout entry |
| Activity List | `/activities/` | View all logged activities |
| Activity Detail | `/activities/<id>/` | View single activity |
| Edit Activity | `/activities/<id>/edit/` | Update activity |
| Delete Activity | `/activities/<id>/delete/` | Remove activity |
| Update Profile | `/profile/update/` | Edit user profile |
| Update Biometrics | `/biometrics/update/` | Log weight/measurements |
| Biometrics History | `/biometrics/history/` | View historical logs |
| Log Water | `/water/log/` | Add water intake |
| Water History | `/water/history/` | View water logs |
| Create Goal | `/goals/create/` | Set new fitness goal |
| Goal List | `/goals/` | View all goals |
| Update Goal | `/goals/<id>/update/` | Edit goal progress |
| **Progress Charts** (NEW) | `/progress/` | View weight trends, activity distribution, calorie charts |
| **Badges** (NEW) | `/badges/` | View earned badges and track progress |

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Django models with custom properties and methods
- ✅ Form validation and ModelForms
- ✅ Function-based views with authentication
- ✅ Template inheritance and components
- ✅ Static methods for business logic
- ✅ Database aggregations (Sum, Count, etc.)
- ✅ Admin interface customization
- ✅ URL routing with parameters
- ✅ Unit testing with Django TestCase
- ✅ Chart.js integration for data visualization (NEW)
- ✅ Gamification with achievement systems (NEW)
- ✅ Progress tracking algorithms (NEW)

## 🚧 Potential Enhancements

- [ ] REST API with Django REST Framework
- [ ] Mobile app (React Native/Flutter)
- [ ] Social features (friends, leaderboards)
- [ ] Wearable device integration (Fitbit, Apple Watch)
- [ ] Nutrition tracking integration
- [ ] Custom workout plans
- [ ] Video exercise library
- [ ] Meal planning
- [ ] Sleep tracking
- [ ] Export data (CSV, PDF)
- [ ] Email notifications
- [ ] Push notifications for mobile
- [ ] Advanced analytics with ML predictions
- [ ] Community forums

## 📞 Support

For issues or questions:
1. Check the documentation in `docs/` folder
2. Review test cases in `fitnesstrack/tests.py`
3. Use Django admin panel for data management
4. Run Django shell for debugging:
   ```bash
   python manage.py shell
   ```

## 🤝 Contributing

This is a learning project. Feel free to:
- Fork the repository
- Add new features
- Improve existing code
- Write more tests
- Enhance documentation

## 📄 License

This project is for educational purposes.

## 🏆 Acknowledgments

- **Django Documentation** - Comprehensive guides
- **Chart.js** - Beautiful, simple charts
- **Mifflin-St Jeor** - BMR calculation formula
- **MET Values** - Calorie burn accuracy
- **Atomic Design** - Component architecture

---

**Built with ❤️ using Django**

**Status**: ✅ Production Ready  
**Version**: 1.0  
**Last Updated**: December 2024  
**Author**: Fitness Tracker Development Team

🎉 **Start tracking your fitness journey today!**

