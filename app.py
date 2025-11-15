from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Flask configuration from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///reports.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Discord OAuth2 settings from environment variables
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/callback')
DISCORD_API_BASE_URL = 'https://discord.com/api/v10'
DISCORD_AUTHORIZATION_BASE_URL = f'{DISCORD_API_BASE_URL}/oauth2/authorize'
DISCORD_TOKEN_URL = f'{DISCORD_API_BASE_URL}/oauth2/token'

# Admin user IDs from environment variable (comma-separated)
ADMINS = os.getenv('ADMINS', '').split(',') if os.getenv('ADMINS') else []

# Database Models
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    report_reason = db.Column(db.Text, nullable=False)
    submitted_by = db.Column(db.String(100), nullable=False)
    submitted_by_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'report_reason': self.report_reason,
            'submitted_by': self.submitted_by,
            'submitted_by_id': self.submitted_by_id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

# Create tables
with app.app_context():
    db.create_all()

def is_admin(user_id):
    """Check if user is an admin"""
    return str(user_id) in ADMINS

def get_discord_oauth_session(token=None, state=None):
    """Create Discord OAuth2 session"""
    return OAuth2Session(
        client_id=DISCORD_CLIENT_ID,
        token=token,
        state=state,
        redirect_uri=DISCORD_REDIRECT_URI,
        scope=['identify']
    )

@app.route('/')
def index():
    """Home page - shows login or report form"""
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    user = session['user']
    return render_template('index.html', user=user, is_admin=is_admin(user['id']))

@app.route('/login_page')
def login_page():
    """Login page"""
    if 'user' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/login')
def login():
    """Redirect to Discord OAuth"""
    discord = get_discord_oauth_session()
    authorization_url, state = discord.authorization_url(DISCORD_AUTHORIZATION_BASE_URL)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    """Discord OAuth callback"""
    if 'error' in request.args:
        return redirect(url_for('login_page'))
    
    discord = get_discord_oauth_session(state=session.get('oauth_state'))
    
    try:
        token = discord.fetch_token(
            DISCORD_TOKEN_URL,
            client_secret=DISCORD_CLIENT_SECRET,
            authorization_response=request.url
        )
        
        session['oauth_token'] = token
        
        # Get user info
        discord = get_discord_oauth_session(token=token)
        user_data = discord.get(f'{DISCORD_API_BASE_URL}/users/@me').json()
        
        session['user'] = {
            'id': user_data['id'],
            'username': user_data['username'],
            'discriminator': user_data.get('discriminator', '0'),
            'avatar': user_data.get('avatar')
        }
        
        return redirect(url_for('index'))
    except Exception as e:
        print(f"OAuth error: {e}")
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/submit_report', methods=['POST'])
def submit_report():
    """Submit a new report"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    username = data.get('username', '').strip()
    report_reason = data.get('report_reason', '').strip()
    
    if not username or not report_reason:
        return jsonify({'error': 'Username and report reason are required'}), 400
    
    user = session['user']
    
    report = Report(
        username=username,
        report_reason=report_reason,
        submitted_by=f"{user['username']}#{user['discriminator']}",
        submitted_by_id=user['id']
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Report submitted successfully'})

@app.route('/admin/reports')
def admin_reports():
    """Admin page to view all reports"""
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    user = session['user']
    if not is_admin(user['id']):
        return "Access Denied - Admin Only", 403
    
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    return render_template('admin.html', user=user, reports=reports)

@app.route('/api/reports')
def api_reports():
    """API endpoint to get all reports (admin only)"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = session['user']
    if not is_admin(user['id']):
        return jsonify({'error': 'Access denied'}), 403
    
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    return jsonify([report.to_dict() for report in reports])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
