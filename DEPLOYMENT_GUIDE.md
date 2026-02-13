# Fitness Tracker - Deployment Guide

## GitHub Repository
Your code is now pushed to: https://github.com/pathgamer1006-tech/tracker-system

## Deployment Steps on Render

### 1. Create a Render Account
- Go to https://render.com
- Sign up with GitHub (recommended for easy connection)

### 2. Create a New Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repository (pathgamer1006-tech/tracker-system)
- Select the repository and main branch

### 3. Configure the Service
- **Name**: fitness-tracker (or your preference)
- **Environment**: Python 3
- **Build Command**: `bash build.sh`
- **Start Command**: `gunicorn fitness.wsgi:application --bind 0.0.0.0:$PORT`
- **Plan**: Free (or upgrade if needed)

### 4. Set Environment Variables
Add these in the Render dashboard under "Environment":

```
SECRET_KEY=<generate a new strong secret key>
DEBUG=False
ALLOWED_HOSTS=<your-render-domain>.onrender.com
CSRF_TRUSTED_ORIGINS=https://<your-render-domain>.onrender.com
DATABASE_URL=sqlite:///db.sqlite3
```

For a production-ready setup, you can optionally add:
```
USE_POSTGRES=True
DATABASE_URL=<postgresql-connection-string>
```

### 5. Deploy
- Click "Create Web Service"
- Render will automatically deploy on every push to main branch

### 6. First Time Setup
After deployment:
1. Visit your app URL
2. You may need to run migrations if they didn't run automatically
3. Create a superuser via the Render shell (if needed)

## Local Development

### Prerequisites
```bash
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file:
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Run Locally
```bash
python manage.py migrate
python manage.py runserver
```

## Troubleshooting

### If build fails:
- Check Render logs in the dashboard
- Ensure `requirements.txt` has all dependencies
- Verify `build.sh` has correct permissions

### If migrations fail:
- Check PostgreSQL connection if using database
- Verify migrations files are in git
- Run manually via Render shell

### For production issues:
- Check Render logs
- Verify environment variables are set
- Test locally with `DEBUG=False`

## Database Options

### Free Tier (SQLite)
- Limited to single dyno
- Good for testing/small projects
- Persistent storage

### Production (PostgreSQL)
- Render offers PostgreSQL
- Set `USE_POSTGRES=True`
- Update `DATABASE_URL` with connection string

## Custom Domain (Optional)
1. In Render dashboard → Settings
2. Add custom domain
3. Update DNS records as instructed
4. Update `ALLOWED_HOSTS` with your domain
