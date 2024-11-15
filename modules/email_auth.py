from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, request, url_for, session
from dotenv import load_dotenv
import os
import secrets

import requests
#from requests_oauthlib import OAuth2Session

load_dotenv()
verified_emails = {}

# def fetch_token_manually(auth_code):
#     token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
#     client_id = os.environ.get('CLIENT_ID')
#     client_secret = os.environ.get('CLIENT_SECRET')
    
#     oauth_session = OAuth2Session(client_id, redirect_uri=url_for('auth_callback', _external=True))
    
#     token = oauth_session.fetch_token(
#         token_url,
#         client_secret=client_secret,
#         code=auth_code
#     )
#     return token

def refresh_access_token(refresh_token):
    """
    Refresh the access token using the provided refresh token.
    """
    Atoken_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    token_data = {
        'client_id': os.environ.get('CLIENT_ID'),
        'client_secret': os.environ.get('CLIENT_SECRET'),
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'scope': 'openid profile email User.Read offline_access'
    }

    response = requests.post(Atoken_url, data=token_data)
    refreshed_token = response.json()

    if 'error' in refreshed_token:
        print("Failed to refresh token:", refreshed_token['error_description'])
        return None, None

    new_access_token = refreshed_token.get("access_token")
    new_refresh_token = refreshed_token.get("refresh_token", refresh_token)
    print("New Access Token:", new_access_token)
    print("New Refresh Token:", new_refresh_token)

    return new_access_token, new_refresh_token
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
            'token_endpoint_auth_method': 'client_secret_post',
            "iss": {"values": [
                "https://sts.windows.net/aaf653e1-0bcd-4c2c-8658-12eb03e15774/",
                "https://login.microsoftonline.com/aaf653e1-0bcd-4c2c-8658-12eb03e15774/v2.0"
            ]}
        }
    )

    print("OAuth configuration:", oauth._clients['microsoft'].__dict__)
    @app.route('/login')
    def login():
        redirect_uri = url_for('auth_callback', _external=True)
        print(f"Redirect URI: {redirect_uri}") 
        print(f"Client ID: {os.environ.get('CLIENT_ID')}") 
        print(f"Client Secret: {os.environ.get('CLIENT_SECRET')}")
        return oauth.microsoft.authorize_redirect(redirect_uri)

    @app.route('/auth/microsoft/callback')
    def auth_callback():
        print("HEOFJOIEF")

        auth_code = request.args.get("code")
    
        Atoken_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        Aclient_id = os.environ.get('CLIENT_ID')
        Aclient_secret = os.environ.get('CLIENT_SECRET')
        Aredirect_uri = url_for('auth_callback', _external=True)
        
        # Prepare token request data
        token_data = {
            'client_id': Aclient_id,
            'client_secret': Aclient_secret,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': Aredirect_uri,
            'scope': 'openid profile email User.Read offline_access'
        }
        
        # Send a POST request to fetch the token
        response = requests.post(Atoken_url, data=token_data)
        token = response.json()
        print("Raw Token Response:", token)  # Log the raw token response for inspection


        if 'error' in token:
            return f"Error fetching token: {token['error_description']}"
        # try: 
        #     token = oauth.microsoft.authorize_access_token(withhold_token=True) #causing the error rn: ISS 
        #     print(f"TOKEN:  {token}")
        #     if not token:
        #         print("Failed to get access token :((((((((")
        #         return 'Error: ' + str(token)
        # except Exception as e:
        #     print(f"STUPID ASS ERROR FROM TOKEN: {e}")
        #     import traceback
        #     traceback.print_exc()
        #     return 'Error: ' + str(e)

        # user_info = oauth.microsoft.get('me').json()
        # print(f"User22 Info: {user_info}")
        # user_info = oauth.microsoft.get('me').json()
        # print(f"User Info: {user_info}")

        # Extract tokens
        access_token = token.get("access_token")
        refresh_token = token.get("refresh_token")

        if not access_token or not refresh_token:
            return "Failed to retrieve tokens."

        # Store tokens in the session (for demo purposes)
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

        # Fetch user info using the access token
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        user_info = user_info_response.json()
        print("User Info:", user_info)
        
        if user_info['mail'].endswith('@rpi.edu'):
            with open("resources/temp_emails.txt", "r+") as f:
                discord_user_id = f.read()
                f.seek(0) 
                f.truncate()
            store_verified_email(discord_user_id, user_info['mail'])
            session['user'] = user_info
            return f"Email verified successfully. You can close this window. {discord_user_id}"
            # return redirect(url_for('dashboard'))
        else:
            return 'Invalid email domain; Check if you have signed in correct email!', 403

    @app.route('/dashboard')
    def dashboard():
        if 'user' in session:
            return f"Welcome, {session['user']['givenName']}!"
        return redirect(url_for('login'))
    
    @app.route('/refresh_token')
    def refresh_token_route():
        # Refresh the token using the stored refresh token
        refresh_token = session.get('refresh_token')
        if not refresh_token:
            return "No refresh token found in session."

        new_access_token, new_refresh_token = refresh_access_token(refresh_token)
        if not new_access_token:
            return "Failed to refresh access token."

        # Update session tokens
        session['access_token'] = new_access_token
        session['refresh_token'] = new_refresh_token
        return "Token refreshed successfully."

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5000, debug=True)

def store_verified_email(discord_user_id, email):
    verified_emails[discord_user_id] = email

def get_verified_email(discord_user_id):
    return verified_emails.get(discord_user_id)



