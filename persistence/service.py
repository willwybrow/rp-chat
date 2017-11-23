from models import OAuthCredential, User, db, Reservation

import uuid

import json


def which_user_just_logged_in(credential_json, id_token_json):
    oauth_credential = find_user_from_google_sub(id_token_json['sub'])
    if oauth_credential is None or oauth_credential.user is None:
        # new user
        reservation = Reservation.query.filter_by(email=id_token_json['email']).first()
        if 'email' in id_token_json and id_token_json['email'] and reservation:
            return create_user_from_credential(credential_json, id_token_json, new_user=User.query.filter_by(id=reservation.user_id).first())
        return create_user_from_credential(credential_json, id_token_json)
    else:
        refresh_credential(id_token_json['sub'], credential_json, id_token_json=id_token_json)
        db.session.commit()
        return oauth_credential.user


def find_user_from_google_sub(google_sub):
    return OAuthCredential.query.filter_by(sub=google_sub).first()


def reserve_user(email):
    new_user = create_and_save_new_user()
    new_reservation = Reservation(email=email, user_id=new_user.id)

    db.session.add(new_reservation)
    db.session.commit()

    return new_reservation


def create_and_save_new_user():
    new_user = User()
    db.session.add(new_user)
    db.session.commit()
    return new_user


def create_user_from_credential(credential_json, id_token_json, new_user=None):
    if new_user is None:
        new_user = create_and_save_new_user()

    user_credential = OAuthCredential(sub=id_token_json['sub'],
                                      refresh_token=credential_json['refresh_token'],
                                      id_token_json=json.dumps(id_token_json),
                                      credential_json=json.dumps(credential_json),
                                      user_id=new_user.id)

    db.session.add(user_credential)
    db.session.commit()

    return new_user


def refresh_credential(google_sub, credential_json, id_token_json=None):
    oauth_credential = find_user_from_google_sub(google_sub)
    if credential_json['refresh_token']:
        oauth_credential.refresh_token = credential_json['refresh_token']
    if id_token_json:
        oauth_credential.id_token_json = json.dumps(id_token_json)
    oauth_credential.credential_json = json.dumps(credential_json)
    return db.session.commit()


def load_user(user_id):
    return User.query.filter_by(id=user_id).first()