from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv
import os
import secrets

load_dotenv()
verified_emails = {}

def create_app():
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.secret_key = secrets.token_urlsafe(32)
    
    oauth = OAuth(app)
    oauth.register(
        name='microsoft',
        client_id=os.environ.get('CLIENT_ID'),
        client_secret=os.environ.get('CLIENT_SECRET'),
        authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
        api_base_url='https://graph.microsoft.com/v1.0/',
        access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
        server_metadata_url="https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration",
        client_kwargs={'scope': 'openid profile email User.Read offline_access'},
        claims_options={
            "iss": {
                "essential": True,  # Making the "iss" claim essential
                "values": [
                    "https://login.microsoftonline.com/common/v2.0",  # Accept this common format
                    "https://login.microsoftonline.com/{tenant_id}/v2.0"  # Accept tenant-specific format
                ]
            }
        }
    )

    print("OAuth configuration:", oauth._clients['microsoft'].__dict__)
    @app.route('/login')
    def login():
        redirect_uri = url_for('auth_callback', _external=True)
        print(f"Redirect URI: {redirect_uri}")
        return oauth.microsoft.authorize_redirect(redirect_uri)

    @app.route('/auth/microsoft/callback')
    def auth_callback():
        print("HEOFJOIEF")
        try: 
            token = oauth.microsoft.authorize_access_token()
            print(f"TOKEN:  {token}")
            if not token:
                print("Failed to get access token :((((((((")
                return 'Error: ' + str(token)
        except Exception as e:
            print(f"STUPID ASS ERROR FROM TOKEN: {e}")
            return 'Error: ' + str(e)

        user_info = oauth.microsoft.get('me').json()
        print(f"User22 Info: {user_info}")
        user_info = oauth.microsoft.get('me').json()
        print(f"User Info: {user_info}")
        
        if user_info['email'].endswith('@rpi.edu'):
            discord_user_id = user_info['id']
            store_verified_email(discord_user_id, user_info['email'])
            session['user'] = user_info
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid email domain', 403

    @app.route('/dashboard')
    def dashboard():
        if 'user' in session:
            return f"Welcome, {session['user']['name']}!"
        return redirect(url_for('login'))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5000, debug=True)

def store_verified_email(discord_user_id, email):
    verified_emails[discord_user_id] = email

def get_verified_email(discord_user_id):
    return verified_emails.pop(discord_user_id, None)

