import json
import os
import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from flask import session, request, redirect, url_for, flash
from app import app, db
from models import Student, Company

# Google OAuth configuration
GOOGLE_CLIENT_ID = ""  # Will be loaded from secrets
GOOGLE_CLIENT_SECRET = ""  # Will be loaded from secrets

def load_google_secrets():
    """Load Google OAuth secrets from environment"""
    global GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    
    # Try to load from GOOGLE_OAUTH_SECRETS environment variable (JSON format)
    secrets_json = os.environ.get('GOOGLE_OAUTH_SECRETS')
    if secrets_json:
        try:
            secrets = json.loads(secrets_json)
            web_config = secrets.get('web', {})
            GOOGLE_CLIENT_ID = web_config.get('client_id', '')
            GOOGLE_CLIENT_SECRET = web_config.get('client_secret', '')
        except json.JSONDecodeError:
            print("Error: Invalid JSON in GOOGLE_OAUTH_SECRETS")
    
    # Fallback to individual environment variables
    if not GOOGLE_CLIENT_ID:
        GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    if not GOOGLE_CLIENT_SECRET:
        GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

def create_google_flow():
    """Create Google OAuth flow"""
    load_google_secrets()
    
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return None
    
    # Create flow from client config
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [get_redirect_uri()]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=['openid', 'email', 'profile']
    )
    flow.redirect_uri = get_redirect_uri()
    return flow

def get_redirect_uri():
    """Get the OAuth redirect URI"""
    # Use Replit dev domain if available, otherwise localhost
    replit_domain = os.environ.get('REPLIT_DEV_DOMAIN')
    if replit_domain:
        return f"https://{replit_domain}/oauth2callback"
    else:
        return url_for('oauth_callback', _external=True)

def get_google_user_info(access_token):
    """Get user info from Google using access token"""
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error getting Google user info: {e}")
        return None

def handle_google_login(user_info, user_type):
    """Handle Google login for both students and companies"""
    if not user_info:
        return False, "Failed to get user information from Google"
    
    email = user_info.get('email')
    name = user_info.get('name')
    google_id = user_info.get('id')
    picture = user_info.get('picture')
    
    if not email or not name or not google_id:
        return False, "Incomplete user information from Google"
    
    # Check if user exists with this Google ID
    if user_type == 'student':
        user = Student.query.filter_by(google_id=google_id).first()
        if not user:
            # Check if user exists with this email
            user = Student.query.filter_by(email=email).first()
            if user:
                # Link existing account with Google
                user.google_id = google_id
                user.profile_picture = picture
            else:
                # Create new user
                user = Student(
                    email=email,
                    name=name,
                    google_id=google_id,
                    profile_picture=picture
                )
                db.session.add(user)
    else:  # company
        user = Company.query.filter_by(google_id=google_id).first()
        if not user:
            # Check if user exists with this email
            user = Company.query.filter_by(email=email).first()
            if user:
                # Link existing account with Google
                user.google_id = google_id
                user.profile_picture = picture
            else:
                # Create new user
                user = Company(
                    email=email,
                    name=name,
                    google_id=google_id,
                    profile_picture=picture
                )
                db.session.add(user)
    
    try:
        db.session.commit()
        
        # Set session
        session['user_type'] = user_type
        session['user_id'] = user.id
        session['google_auth'] = True
        
        return True, user
    except Exception as e:
        db.session.rollback()
        return False, f"Database error: {str(e)}"
