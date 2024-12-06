from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, request, url_for, session
from dotenv import load_dotenv
import os
import secrets

import requests
#from requests_oauthlib import OAuth2Session

load_dotenv()
verified_emails = {}

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
    """
    Creates and configures a Flask application for Microsoft OAuth 2.0 authentication.

    This function sets up a Flask application with routes for handling login,
    authorization callback, dashboard display, and token refresh. It registers
    the Microsoft OAuth client and configures the necessary endpoints and 
    credentials for the authentication process.

    Returns:
        app (Flask): The configured Flask application instance.
    """
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
        # Retrieve and clear the error message
        """
        Initiates the Microsoft OAuth flow for authentication.

        This endpoint is responsible for retrieving and clearing any error messages
        that have been stored in the session, and then redirecting the user to the
        Microsoft OAuth authorization endpoint.

        If an error message is present in the session, the user is shown an HTML page
        with the error message and a link to retry the login process.

        Otherwise, the user is redirected to the authorization endpoint, which will
        prompt the user to authenticate and then redirect them back to the
        `auth_callback` endpoint.

        Returns:
            A redirect response to the authorization endpoint, or an HTML page with an
            error message if an error is present in the session.
        """
        error_message = session.pop('error_message', None)

        # Initiate the Microsoft OAuth flow
        redirect_uri = url_for('auth_callback', _external=True)
        
        # Add error handling display
        if error_message:
            print(f"Error: {error_message}")  # Debugging purposes only
            return f"""
                <html>
                    <body>
                        <p style="color:red;">{error_message}</p>
                        <p>Click <a href="{url_for('login')}">here</a> to continue with the correct email.</p>
                    </body>
                </html>
            """

        return oauth.microsoft.authorize_redirect(redirect_uri)


    @app.route('/auth/microsoft/callback')
    def auth_callback():
        """
        Handles the Microsoft OAuth flow callback.

        This route is called when the user authorizes the app. The app then exchanges the authorization code for an access token and refresh token.
        The access token is used to fetch the user's email address and check if it is an RPI email address.
        If it is, the user is added to the list of verified emails and the user is redirected to the dashboard.
        If not, an error message is displayed and the user is redirected to the login page.

        :return: A redirect to the login page with an error message if the email address is not an RPI email address, or a redirect to the dashboard if it is.
        """
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
        
        if user_info['mail'][-8:] == ('@rpi.edu'):
            with open("resources/temp_emails.txt", "r+") as f:
                discord_user_id = f.read()
                f.seek(0) 
                f.truncate()
            store_verified_email(discord_user_id, user_info['mail'])
            session['user'] = user_info
            return f"Email verified successfully. You can close this window."
            # return redirect(url_for('dashboard'))
        else:
            session['error_message'] = 'Invalid email domain; please check if you have signed in with the correct email!'
            return redirect(url_for('login'))   

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

def remove_verified_email(discord_user_id):
    if discord_user_id in verified_emails:
        del verified_emails[discord_user_id]

