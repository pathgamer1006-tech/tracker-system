# Database Setup for Render

Your Fitness Tracker can use either **SQLite** (development) or **PostgreSQL** (production).

## Current Setup

- **Development (Local):** SQLite (`db.sqlite3`)
- **Production (Render):** Currently SQLite, but can be upgraded to PostgreSQL

## Why Add PostgreSQL?

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Data Persistence | ✅ Files on disk | ✅ Managed database |
| Performance | Good for small apps | Better for scale |
| Concurrent Users | Limited | Excellent |
| Backups | Manual | Automatic on Render |
| Cost | Free | Free tier on Render |

## How to Add PostgreSQL to Render (Free Tier)

### Step 1: Create PostgreSQL Database on Render
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Choose:
   - **Name:** `fitness-db`
   - **Plan:** Free
   - **Region:** Same as your service
4. Click **"Create Database"**
5. Wait for it to be created (~5 minutes)

### Step 2: Get Database URL
1. Click on the new PostgreSQL database
2. Copy the **"Internal Database URL"** (starts with `postgresql://`)
3. This is your `DATABASE_URL`

### Step 3: Add to Your Web Service Environment
1. Go back to your **tracker-system** service
2. Click **"Environment"**
3. Click **"Edit"**
4. Add a new environment variable:
   - **KEY:** `DATABASE_URL`
   - **VALUE:** Paste the URL from Step 2
5. Click **"Save"**

### Step 4: Deploy
1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. The build will run migrations and create tables in PostgreSQL
3. Your data will now persist!

## Automatic Database Selection

Your app now automatically:
- Uses **PostgreSQL** if `DATABASE_URL` is set
- Falls back to **SQLite** if `DATABASE_URL` is not set
- Handles both development and production seamlessly

## Testing Locally

No changes needed! Your app works with SQLite locally:
```bash
python manage.py runserver
```

## Monitoring Database

You can check your PostgreSQL database from Render:
1. Go to your PostgreSQL resource on Render
2. Click **"Connect"**
3. Use the psql connection string to query directly (optional)

## Free Tier Limits (PostgreSQL on Render)

- Storage: 256 MB (plenty for fitness tracking)
- Connections: 10 concurrent
- Backups: Automatic, 7-day retention
- No downtime: Data synced to storage

## If You Need More Storage

Simply click **"Upgrade"** on your PostgreSQL database in Render to increase capacity.

## Troubleshooting

**If your app still shows 400 errors after adding PostgreSQL:**
1. Ensure DATABASE_URL is in environment variables
2. Trigger a new manual deploy
3. Check the build logs for any migration errors

**To check database migrations:**
View deployment logs in Render to see if `python manage.py migrate` completed successfully.
