from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired


class NewCampaignForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create')


class NewCharacterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[DataRequired()])
    submit = SubmitField('Create')


class UpdateProfileForm(FlaskForm):
    name = StringField('Name')
    submit = SubmitField('Update')


class NewMessageForm(FlaskForm):
    message_type = SelectField('Message Type', choices=[('1', 'speech'), ('0', 'action')])
    content = StringField('Message')
    submit = SubmitField('Send')
