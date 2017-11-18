from web import app, config

from flask import url_for, redirect, render_template, session, jsonify, request

import requests

import google.oauth2.credentials
import google.oauth2.id_token
import google_auth_oauthlib.flow
import googleapiclient.discovery
import google.auth.transport.requests

oauth_scopes = ['openid', 'email', 'profile']


@app.route('/')
def index():
    return ("<html><head><title>test</title></head><body><h1>Welcome</h1></body></html>")


@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(config['secrets']['oauth2_client_secret_file'],
                                                                   scopes=oauth_scopes)

    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true', prompt='consent')

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
        return redirect(url_for('test_api_request'))


    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    session['id_token'] = google.oauth2.id_token.verify_oauth2_token(credentials.id_token, google.auth.transport.requests.Request(), credentials.client_id)

    return redirect(url_for('test_api_request'))


@app.route('/revoke')
def revoke():
    if 'credentials' not in session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        del session['credentials']
        return ('Credentials successfully revoked.')
    else:
        return ('An error occurred.')



@app.route('/clear')
def clear():
    if 'credentials' not in session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    del session['credentials']
    return ('Credentials cleared!')



@app.route('/test')
def test_api_request():
    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])  # .refresh(google.auth.transport.requests.Request())

    credentials.refresh(google.auth.transport.requests.Request())

    service = googleapiclient.discovery.build("identitytoolkit", "v3", credentials=credentials)

    # things = dir(service.relyingparty().getAccountInfo(body={'idToken': credentials.id_token}).execute())

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    session['credentials'] = credentials_to_dict(credentials)

    return jsonify(id_token=session['id_token'], new_id_token=google.oauth2.id_token.verify_oauth2_token(credentials.id_token, google.auth.transport.requests.Request(), credentials.client_id))


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
