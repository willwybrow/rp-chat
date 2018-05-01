import json

from chat.web import app, config, login_manager

from flask import url_for, redirect, session, jsonify, request

from flask_login import login_required, login_user, current_user, logout_user

import google.oauth2.credentials
import google.oauth2.id_token
import google_auth_oauthlib.flow
import google.auth.transport.requests

oauth_scopes = ['openid', 'email', 'profile']

login_manager.login_view = "login"
login_manager.session_protection = "strong"


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


@login_manager.user_loader
def load_user(user_id):
    from chat.persistence.models import User
    return User.query.filter_by(id=user_id).first()


@app.route('/login')
def login():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(config['secrets']['oauth2_client_secret_file'],
                                                                   scopes=oauth_scopes)

    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
        # prompt = consent means get a new refresh token each time
        # don't do this under normal circumstances
        prompt='consent')
    # )

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    import oauthlib.oauth2.rfc6749.errors
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        config['secrets']['oauth2_client_secret_file'], scopes=oauth_scopes, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:
        return redirect(url_for('home'))


    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    # session['credentials'] = credentials_to_dict(credentials)
    id_token = google.oauth2.id_token.verify_oauth2_token(credentials.id_token, google.auth.transport.requests.Request(), credentials.client_id)

    login_user(chat.persistence.service.which_user_just_logged_in(credentials_to_dict(credentials), id_token), remember=True)

    return redirect(url_for('home'))

"""
@app.route('/revoke')
def revoke():
    if 'logged_in_user_id' not in session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(**json.loads(current_user.oauth_credential.credential_json))

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        del session['logged_in_user_id']
        del g['logged_in_user']
        return ('Credentials successfully revoked.')
    else:
        return ('An error occurred.')
"""

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@login_required
@app.route('/refresh')
def refresh_token():
    # Load credentials from the session.

    credentials = google.oauth2.credentials.Credentials(
            **json.loads(current_user.oauth_credential.credential_json))

    credentials.refresh(google.auth.transport.requests.Request())

    # service = googleapiclient.discovery.build("identitytoolkit", "v3", credentials=credentials)

    # things = dir(service.relyingparty().getAccountInfo(body={'idToken': credentials.id_token}).execute())

    old_id_token = json.loads(current_user.oauth_credential.id_token_json)
    new_id_token = google.oauth2.id_token.verify_oauth2_token(credentials.id_token, google.auth.transport.requests.Request(), credentials.client_id)
    chat.persistence.service.refresh_credential(current_user.oauth_credential.sub, credentials_to_dict(credentials), id_token_json=new_id_token)

    return jsonify(id_token=old_id_token, new_id_token=new_id_token)


@login_required
@app.route('/email')
def get_emails():
    credentials = google.oauth2.credentials.Credentials(
        **json.loads(current_user.oauth_credential.credential_json))

    credentials.refresh(google.auth.transport.requests.Request())

    new_id_token = google.oauth2.id_token.verify_oauth2_token(credentials.id_token, google.auth.transport.requests.Request(), credentials.client_id)
    chat.persistence.service.refresh_credential(current_user.oauth_credential.sub, credentials_to_dict(credentials), id_token_json=new_id_token)

    return jsonify(new_id_token['email'])
