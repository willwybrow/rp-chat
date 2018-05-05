import uuid

import sqlalchemy

from web import db


def new_uuid():
    return str(uuid.uuid4()).lower()


def new_double_uuid():
    return u"{}-{}".format(uuid.uuid4(), uuid.uuid4()).lower()


class RecipientTypes(object):
    campaign = 0
    character = 1
    chat = 2


class MessageTypes(object):
    action = 0
    speech = 1


group_users = db.Table('group_user',
                       db.Column('user_id', db.String(36), db.ForeignKey("user.id"), nullable=False, primary_key=True),
                       db.Column('group_id', db.String(36), db.ForeignKey("group.id"), nullable=False, primary_key=True)
                       )


campaign_characters = db.Table('campaign_character',
                               db.Column('character_id', db.String(36), db.ForeignKey("character.id"), nullable=False, primary_key=True),
                               db.Column('campaign_id', db.String(36), db.ForeignKey("campaign.id"), nullable=False, primary_key=True)
                               )


chat_participants = db.Table('chat_participant',
                             db.Column('chat_id', db.String(36), db.ForeignKey("chat.id"), nullable=False, primary_key=True),
                             db.Column('character_id', db.String(36), db.ForeignKey("character.id"), nullable=False, primary_key=True)
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
    chats = db.relationship('Chat', secondary=chat_participants, back_populates='participants')
    played_by = db.relationship('User', backref='characters', uselist=False)
    recipient_type_id = db.Column(db.Integer, db.ForeignKey("recipient_type.id"), nullable=False, default=RecipientTypes.character)
    __table_args__ = (
        db.ForeignKeyConstraint(['id', 'recipient_type_id'], ['recipient.id', 'recipient.recipient_type_id']),
    )


class Campaign(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    characters = db.relationship('Character', secondary=campaign_characters, back_populates='campaigns')
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=True)
    run_by = db.relationship('User', backref='campaigns', uselist=False)
    recipient_type_id = db.Column(db.Integer, db.ForeignKey("recipient_type.id"), nullable=False, default=RecipientTypes.campaign)
    __table_args__ = (
        db.ForeignKeyConstraint(['id', 'recipient_type_id'], ['recipient.id', 'recipient.recipient_type_id']),
    )


class Chat(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    topic = db.Column(db.Text)
    participants = db.relationship('Character', secondary=chat_participants, back_populates='chats')
    recipient_type_id = db.Column(db.Integer, db.ForeignKey("recipient_type.id"), nullable=False, default=RecipientTypes.chat)
    __table_args__ = (
        db.ForeignKeyConstraint(['id', 'recipient_type_id'], ['recipient.id', 'recipient.recipient_type_id']),
    )


class Message(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    message_type_id = db.Column(db.Integer, db.ForeignKey("message_type.id"), nullable=False, default=MessageTypes.speech)
    content = db.Column(db.Text)
    sender_id = db.Column(db.String(36), db.ForeignKey("character.id"), nullable=True)
    sender = db.relationship('Character', backref='messages', uselist=False)
    recipient_id = db.Column(db.String(36), db.ForeignKey("recipient.id"), nullable=False)
    timestamp = db.Column(db.DateTime)
    __table_args__ = (
        db.Index("messages_by_timestamp", "timestamp"),
    )


class ChatReadUpTo(db.Model):
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), primary_key=True, nullable=False)
    recipient_id = db.Column(db.String(36), db.ForeignKey("recipient.id"), primary_key=True, nullable=False)
    timestamp = db.Column(db.DateTime)


class MessageType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)


class RecipientType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text)


class Recipient(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=new_uuid)
    recipient_type_id = db.Column(db.Integer, db.ForeignKey("recipient_type.id"), nullable=False)
    __table_args__ = (
        db.UniqueConstraint('id', 'recipient_type_id', name='unique_recipients'),
    )


db.create_all()
try:
    db.session.add(RecipientType(id=RecipientTypes.campaign, name="campaign"))
    db.session.commit()
except sqlalchemy.exc.IntegrityError:
    db.session.rollback()
try:
    db.session.add(RecipientType(id=RecipientTypes.character, name="character"))
    db.session.commit()
except sqlalchemy.exc.IntegrityError:
    db.session.rollback()
try:
    db.session.add(RecipientType(id=RecipientTypes.chat, name="chat"))
    db.session.commit()
except sqlalchemy.exc.IntegrityError:
    db.session.rollback()
try:
    db.session.add(MessageType(id=MessageTypes.action, name="action"))
    db.session.commit()
except sqlalchemy.exc.IntegrityError:
    db.session.rollback()
try:
    db.session.add(MessageType(id=MessageTypes.speech, name="speech"))
    db.session.commit()
except sqlalchemy.exc.IntegrityError:
    db.session.rollback()

db.session.execute("""
CREATE TRIGGER IF NOT EXISTS create_linked_character_recipient BEFORE INSERT ON character
BEGIN
  INSERT INTO recipient VALUES(NEW.id, NEW.recipient_type_id);
END;
""")

db.session.execute("""
CREATE TRIGGER IF NOT EXISTS create_linked_campaign_recipient BEFORE INSERT ON campaign
BEGIN
  INSERT INTO recipient VALUES(NEW.id, NEW.recipient_type_id);
END;
""")

db.session.execute("""
CREATE TRIGGER IF NOT EXISTS create_linked_chat_recipient BEFORE INSERT ON chat
BEGIN
  INSERT INTO recipient VALUES(NEW.id, NEW.recipient_type_id);
END;
""")

db.session.execute("""
CREATE TRIGGER IF NOT EXISTS delete_linked_character_recipient AFTER DELETE ON character
BEGIN
  DELETE FROM recipient WHERE recipient.id = OLD.id AND recipient.recipient_type_id = OLD.recipient_type_id;
END;
""")

db.session.execute("""
CREATE TRIGGER IF NOT EXISTS delete_linked_campaign_recipient AFTER DELETE ON campaign
BEGIN
  DELETE FROM recipient WHERE recipient.id = OLD.id AND recipient.recipient_type_id = OLD.recipient_type_id;
END;
""")

db.session.execute("""
CREATE TRIGGER IF NOT EXISTS delete_linked_chat_recipient AFTER DELETE ON chat
BEGIN
  DELETE FROM recipient WHERE recipient.id = OLD.id AND recipient.recipient_type_id = OLD.recipient_type_id;
END;
""")
