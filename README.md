# Royal Guard Report System

A Flask-based web application for submitting and managing reports with Discord OAuth authentication.

## Features

- **Discord OAuth Login**: Secure authentication using Discord
- **Report Submission**: Users can submit reports with username and reason
- **Admin Panel**: Admins can view all submitted reports
- **SQLite Database**: Persistent storage using Railway's SQLite implementation
- **Responsive Design**: Modern UI matching the British Army theme

## Setup Instructions

### 1. Discord Application Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to OAuth2 settings
4. Add redirect URI: `http://localhost:5000/callback` (for local testing)
5. For Railway deployment, add: `https://your-app.railway.app/callback`
6. Copy your Client ID and Client Secret

### 2. Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Discord OAuth Configuration
DISCORD_CLIENT_ID=YOUR_DISCORD_CLIENT_ID
DISCORD_CLIENT_SECRET=YOUR_DISCORD_CLIENT_SECRET
DISCORD_REDIRECT_URI=http://localhost:5000/callback

# Admin User IDs (comma-separated)
ADMINS=YOUR_DISCORD_USER_ID

# Flask Secret Key (change this to a random secret)
SECRET_KEY=change-this-to-a-random-secret-key

# Database (optional, defaults to sqlite:///reports.db)
DATABASE_URI=sqlite:///reports.db
```

**Important**: 
- Replace `YOUR_DISCORD_CLIENT_ID` with your Discord application's client ID
- Replace `YOUR_DISCORD_CLIENT_SECRET` with your Discord application's client secret
- Replace `YOUR_DISCORD_USER_ID` with your Discord user ID
- For multiple admins, use comma-separated IDs: `ADMINS=123456789,987654321`
- Change `SECRET_KEY` to a random string for session security
- Never commit `.env` to version control (it's in `.gitignore`)

### 3. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Visit `http://localhost:5000` in your browser.

### 4. Railway Deployment

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository or upload the files
3. Railway will automatically detect the Flask app
4. Add environment variables in Railway dashboard:
   - `DISCORD_CLIENT_ID`
   - `DISCORD_CLIENT_SECRET`
   - `DISCORD_REDIRECT_URI` (use your Railway URL: `https://your-app.railway.app/callback`)
   - `ADMINS` (comma-separated Discord user IDs)
   - `SECRET_KEY` (random secret string)
5. Update Discord OAuth redirect URI to match Railway URL

## File Structure

```
RoyalGuardReportSystem/
├── app.py                 # Main Flask application
├── .env                   # Environment variables (create from .env.example)
├── .env.example           # Example environment configuration
├── requirements.txt       # Python dependencies
├── Procfile              # Railway/Heroku deployment config
├── runtime.txt           # Python version
├── .gitignore            # Git ignore file
├── templates/
│   ├── login.html        # Login page
│   ├── index.html        # Report submission form
│   └── admin.html        # Admin panel
└── reports.db            # SQLite database (auto-created)
```

## Admin Access

Users listed in the `ADMINS` environment variable can:
- Access the admin panel at `/admin/reports`
- View all submitted reports
- See submission details including timestamp and submitter

## Security Notes

- Never commit `.env` with real credentials to public repositories (it's in `.gitignore`)
- Use environment variables for all deployments
- Change the `SECRET_KEY` to a strong random value
- Keep your Discord client secret confidential
- For production, use a secure random string generator for `SECRET_KEY`

## License

© 2025 ArchiveAnt. All Rights Reserved.
