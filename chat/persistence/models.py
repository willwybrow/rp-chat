import uuid

from web import db


def new_uuid():
    return str(uuid.uuid4()).lower()


def new_double_uuid():
    return u"{}-{}".format(uuid.uuid4(), uuid.uuid4()).lower()


group_users = db.Table('group_user',
                       db.Column('user_id', db.String(36), db.ForeignKey("user.id"), nullable=False, primary_key=True),
                       db.Column('group_id', db.String(36), db.ForeignKey("group.id"), nullable=False, primary_key=True)
                       )


campaign_characters = db.Table('campaign_character',
                               db.Column('character_id', db.String(36), db.ForeignKey("character.id"), nullable=False, primary_key=True),
                               db.Column('campaign_id', db.String(36), db.ForeignKey("campaign.id"), nullable=False, primary_key=True)
                               )


class OAuthCredential(db.Model):
    sub = db.Column(db.String(255), primary_key=True)
    refresh_token = db.Column(db.String(255), nullable=False)
    id_token_json = db.Column(db.Text, nullable=False)
    credential_json = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
    user = db.relationship('User', backref=db.backref('oauth_credential', uselist=False), uselist=False)


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    name = db.Column(db.Text)
    groups = db.relationship('Group', secondary=group_users, back_populates='users')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Reservation(db.Model):
    email = db.Column(db.String(320), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)


class Invitation(db.Model):
    id = db.Column(db.String(73), primary_key=True, default=new_double_uuid)
    campaign_id = db.Column(db.String(36), db.ForeignKey("campaign.id"), nullable=False)
    campaign = db.relationship('Campaign', backref='invitations', uselist=False)


class Group(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    name = db.Column(db.Text)
    users = db.relationship('User', secondary=group_users, back_populates='groups')


class Character(db.Model):
    # a character can be in many campaigns
    # a character is played by one user (at a time)
    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    name = db.Column(db.Text)
    bio = db.Column(db.Text)
    notes = db.Column(db.Text)
    dm_notes = db.Column(db.Text)
    dm_secret_notes = db.Column(db.Text)
    can_talk = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=True)
    campaigns = db.relationship('Campaign', secondary=campaign_characters, back_populates='characters')
    
    
class Campaign(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    characters = db.relationship('Character', secondary=campaign_characters, back_populates='campaigns')
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=True)
    run_by = db.relationship('User', backref='campaigns', uselist=False)


db.create_all()
