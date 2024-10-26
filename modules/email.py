from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv
import os

load_dotenv()
verified_emails = {}
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
oauth = OAuth(app)

# Register Microsoft OAuth
oauth.register(
    name='microsoft',
    client_id= os.environ.get("CLIENT_ID"),
    client_secret= os.environ.get("CLIENT_SECRET"),
    authorize_url='https://login.microsoftonline.com/{}/oauth2/v2.0/authorize'.format(os.environ['TENANT_ID']),
    token_url='https://login.microsoftonline.com/{}/oauth2/v2.0/token'.format(os.environ['TENANT_ID']),
    client_kwargs={
        'scope': 'openid User.Read offline_access'
    }
)

# Step 1: Redirect to Microsoft login
@app.route('/login')
def login():
    redirect_uri = url_for('auth_callback', _external=True)
    return oauth.microsoft.authorize_redirect(redirect_uri)

# Step 2: Handle the callback after Microsoft authentication
@app.route('/auth/microsoft/callback')
def auth_callback():
    token = oauth.microsoft.authorize_access_token()
    user_info = oauth.microsoft.parse_id_token(token)
    
    # Check if the email belongs to RPI
    if user_info['email'].endswith('@rpi.edu'):
        # Proceed with your club management logic
        session['user'] = user_info
        return redirect(url_for('dashboard'))
    else:
        return 'Invalid email domain', 403

# Protected dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"Welcome, {session['user']['name']}!"
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

def store_verified_email(discord_user_id, email):
    """
    Stores the verified email against the Discord user ID.
    """
    verified_emails[discord_user_id] = email

def get_verified_email(discord_user_id):
    """
    Retrieves the verified email for the given Discord user ID, if available.
    """
    return verified_emails.pop(discord_user_id, None)  # Remove after retrieval for one-time use