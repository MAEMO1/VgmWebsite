from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_user
from app import db
from models import User
from oauthlib.oauth2 import WebApplicationClient
import os
import requests
import json
from werkzeug.security import generate_password_hash
from flask_babel import _

auth = Blueprint('auth', __name__)

# OAuth 2.0 client configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
FACEBOOK_CLIENT_ID = os.environ.get("FACEBOOK_APP_ID")
FACEBOOK_CLIENT_SECRET = os.environ.get("FACEBOOK_APP_SECRET")
LINKEDIN_CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET")

# OAuth 2.0 endpoints
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
FACEBOOK_AUTH_URL = "https://www.facebook.com/v12.0/dialog/oauth"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v12.0/oauth/access_token"
FACEBOOK_USER_INFO_URL = "https://graph.facebook.com/me?fields=id,name,email"
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USER_INFO_URL = "https://api.linkedin.com/v2/me"
LINKEDIN_EMAIL_URL = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"

# Initialize OAuth clients
google_client = WebApplicationClient(GOOGLE_CLIENT_ID)
facebook_client = WebApplicationClient(FACEBOOK_CLIENT_ID)
linkedin_client = WebApplicationClient(LINKEDIN_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@auth.route("/login/google")
def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = google_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.replace("http://", "https://") + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth.route("/login/google/callback")
def google_callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Get tokens
    token_url, headers, body = google_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url.replace("http://", "https://"),
        redirect_url=request.base_url.replace("http://", "https://"),
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens
    google_client.parse_request_body_response(json.dumps(token_response.json()))

    # Get user info from Google
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = google_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        flash(_("Google account niet geverifieerd. Gebruik een geverifieerd account."), "error")
        return redirect(url_for("main.register"))

    # Create or update user
    user = User.query.filter_by(email=users_email).first()
    if not user:
        user = User(
            username=users_name,
            email=users_email,
            password_hash=generate_password_hash(unique_id),  # Use Google ID as password
            user_type='visitor'
        )
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)
    flash(_("Succesvol ingelogd via Google!"), "success")
    return redirect(url_for("main.index"))

@auth.route("/login/facebook")
def facebook_login():
    request_uri = facebook_client.prepare_request_uri(
        FACEBOOK_AUTH_URL,
        redirect_uri=request.base_url.replace("http://", "https://") + "/callback",
        scope=["email"],
    )
    return redirect(request_uri)

@auth.route("/login/facebook/callback")
def facebook_callback():
    # Get access token
    code = request.args.get("code")
    token_url, headers, body = facebook_client.prepare_token_request(
        FACEBOOK_TOKEN_URL,
        authorization_response=request.url.replace("http://", "https://"),
        redirect_url=request.base_url.replace("http://", "https://"),
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET),
    )
    facebook_client.parse_request_body_response(json.dumps(token_response.json()))

    # Get user info from Facebook
    userinfo_response = requests.get(
        FACEBOOK_USER_INFO_URL,
        headers={'Authorization': f'Bearer {facebook_client.token["access_token"]}'},
    )
    userinfo = userinfo_response.json()

    if userinfo.get("email"):
        users_email = userinfo["email"]
        users_name = userinfo["name"]
        unique_id = userinfo["id"]
    else:
        flash(_("Kon geen e-mailadres ophalen van Facebook. Controleer of u toestemming heeft gegeven voor e-mailtoegang."), "error")
        return redirect(url_for("main.register"))

    # Create or update user
    user = User.query.filter_by(email=users_email).first()
    if not user:
        user = User(
            username=users_name,
            email=users_email,
            password_hash=generate_password_hash(unique_id),
            user_type='visitor'
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(_("Succesvol ingelogd via Facebook!"), "success")
    return redirect(url_for("main.index"))

@auth.route("/login/linkedin")
def linkedin_login():
    request_uri = linkedin_client.prepare_request_uri(
        LINKEDIN_AUTH_URL,
        redirect_uri=request.base_url.replace("http://", "https://") + "/callback",
        scope=["r_liteprofile", "r_emailaddress"],
    )
    return redirect(request_uri)

@auth.route("/login/linkedin/callback")
def linkedin_callback():
    code = request.args.get("code")
    token_url, headers, body = linkedin_client.prepare_token_request(
        LINKEDIN_TOKEN_URL,
        authorization_response=request.url.replace("http://", "https://"),
        redirect_url=request.base_url.replace("http://", "https://"),
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET),
    )
    linkedin_client.parse_request_body_response(json.dumps(token_response.json()))

    # Get user info from LinkedIn
    headers = {'Authorization': f'Bearer {linkedin_client.token["access_token"]}'}
    userinfo_response = requests.get(LINKEDIN_USER_INFO_URL, headers=headers)
    email_response = requests.get(LINKEDIN_EMAIL_URL, headers=headers)

    userinfo = userinfo_response.json()
    emailinfo = email_response.json()

    if emailinfo.get("elements") and emailinfo["elements"][0].get("handle~", {}).get("emailAddress"):
        users_email = emailinfo["elements"][0]["handle~"]["emailAddress"]
        users_name = f"{userinfo.get('localizedFirstName', '')} {userinfo.get('localizedLastName', '')}".strip()
        unique_id = userinfo["id"]
    else:
        flash(_("Kon geen e-mailadres ophalen van LinkedIn. Controleer of u toestemming heeft gegeven voor e-mailtoegang."), "error")
        return redirect(url_for("main.register"))

    # Create or update user
    user = User.query.filter_by(email=users_email).first()
    if not user:
        user = User(
            username=users_name,
            email=users_email,
            password_hash=generate_password_hash(unique_id),
            user_type='visitor'
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(_("Succesvol ingelogd via LinkedIn!"), "success")
    return redirect(url_for("main.index"))
