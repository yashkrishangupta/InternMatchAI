import json
import os
import requests
from flask import session, request, redirect, url_for
from google_auth_oauthlib.flow import Flow
from app import app, db
from models import Student, Department

# Google OAuth configuration
GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""

def load_google_secrets():
    """Load Google OAuth secrets from environment"""
    global GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

    # Try JSON secrets format
    secrets_json = os.environ.get("GOOGLE_OAUTH_SECRETS")
    if secrets_json:
        try:
            secrets = json.loads(secrets_json)
            web_config = secrets.get("web", {})
            GOOGLE_CLIENT_ID = web_config.get("client_id", "")
            GOOGLE_CLIENT_SECRET = web_config.get("client_secret", "")
        except json.JSONDecodeError:
            print("Error: Invalid JSON in GOOGLE_OAUTH_SECRETS")

    # Fallback to individual env variables
    if not GOOGLE_CLIENT_ID:
        GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    if not GOOGLE_CLIENT_SECRET:
        GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

def create_google_flow():
    """Create Google OAuth flow"""
    load_google_secrets()

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return None

    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [get_redirect_uri()],
        }
    }

    flow = Flow.from_client_config(
        client_config,     
        scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    )
    flow.redirect_uri = get_redirect_uri()
    return flow

def get_redirect_uri():
    """Get OAuth redirect URI (works for local + deployment)"""
    return url_for("oauth_callback", _external=True)

def get_google_user_info(access_token):
    """Fetch user info from Google API"""
    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching Google user info: {e}")
        return None

def handle_google_login(user_info, user_type):
    """Process login and save user"""
    if not user_info:
        return False, "Failed to get user information from Google"

    email = user_info.get("email")
    name = user_info.get("name")
    google_id = user_info.get("id")
    picture = user_info.get("picture")

    if not email or not name or not google_id:
        return False, "Incomplete user information from Google"

    if user_type == "student":
        user = Student.query.filter_by(google_id=google_id).first()
        if not user:
            user = Student.query.filter_by(email=email).first()
            if user:
                user.google_id = google_id
                user.profile_picture = picture
            else:
                user = Student(
                    email=email,
                    name=name,
                    google_id=google_id,
                    profile_picture=picture,
                )
                db.session.add(user)
    else:  # department
        user = Department.query.filter_by(email=email).first()
        if user:
            # Departments cannot use Google OAuth - only admin-created accounts
            return False, "Departments must use admin-provided credentials"

    try:
        db.session.commit()
        session["user_type"] = user_type
        session["user_id"] = user.id
        session["google_auth"] = True
        return True, user
    except Exception as e:
        db.session.rollback()
        return False, f"Database error: {str(e)}"
