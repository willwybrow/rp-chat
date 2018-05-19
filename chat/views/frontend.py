import datetime

from flask import render_template, request, redirect, url_for, Response
from flask_login import login_required, current_user

import forms
from persistence import models
from web import app


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/version')
def version():
    import git
    import json
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    version_dict = {'version': sha}
    return app.response_class(response=json.dumps(version_dict), status=200, mimetype="application/json")


@login_required
@app.route('/profile', methods=['GET', 'POST'])
def my_profile():
    user_to_update = models.User.query.filter_by(id=current_user.id).first_or_404()
    if request.method == 'GET':
        update_form = forms.UpdateProfileForm(obj=user_to_update)
        return render_template("profile.html", update_form=update_form)
    elif request.method == 'POST':
        update_form = forms.UpdateProfileForm(request.form)
        if update_form.validate_on_submit():
            user_to_update.name = update_form.name.data
            models.db.session.commit()
            return redirect(url_for('my_profile'))
        else:
            return render_template("profile.html", update_form=update_form)


@login_required
@app.route('/dm/campaigns/', methods=['GET', 'POST'])
def dm_campaigns():
    new_form = forms.NewCampaignForm(request.form)
    if request.method == 'GET':
        my_campaigns = models.Campaign.query.filter_by(user_id=current_user.id).paginate(page=int(request.args.get('page', 1)))
        return render_template("campaigns.html", campaigns=my_campaigns, new_form=new_form)
    elif request.method == 'POST':
        if new_form.validate_on_submit():
            new_campaign = models.Campaign(name=new_form.name.data, description=new_form.description.data, user_id=current_user.id)
            models.db.session.add(new_campaign)
            models.db.session.commit()
            return redirect(url_for('dm_campaign', campaign_id=new_campaign.id))
        else:
            return render_template("campaigns.html", campaigns=my_campaigns, new_form=new_form)


@login_required
@app.route('/dm/campaigns/<campaign_id>', methods=['GET', 'POST'])
def dm_campaign(campaign_id):
    campaign = models.db.session.query(models.Campaign).filter_by(user_id=current_user.id).filter(models.Campaign.id == campaign_id).first_or_404()
    return render_template("campaign.html", campaign=campaign)


@login_required
@app.route('/campaigns/', methods=['GET', 'POST'])
def campaigns():
    if request.method == 'GET':
        campaigns = models.db.session.query(models.Campaign).join(models.Campaign.characters).filter(
            models.Character.user_id == current_user.id).paginate(page=int(request.args.get('page', 1)))
        return render_template("campaigns.html", campaigns=campaigns)


@login_required
@app.route('/campaigns/<campaign_id>')
def campaign(campaign_id):
    campaign = models.db.session.query(models.Campaign).join(models.Campaign.characters).filter(
            models.Character.user_id == current_user.id).filter(models.Campaign.id == campaign_id).first_or_404()
    return render_template("campaign.html", campaign=campaign)


@login_required
@app.route('/campaigns/<campaign_id>/chat/as/<character_id>', methods=['GET', 'POST'])
def campaign_character_chat(campaign_id, character_id):
    new_message_form = forms.NewMessageForm(request.form)
    character = models.Character.query.filter_by(id=character_id, user_id=current_user.id).first_or_404()
    campaign = models.db.session.query(models.Campaign).join(models.Campaign.characters).filter(
            models.Character.user_id == current_user.id).filter(models.Campaign.id == campaign_id).filter(models.Character.id == character_id).first_or_404()
    chat_recipient = models.Recipient.query.filter_by(id=campaign.id).first_or_404()
    if request.method == 'POST':
        if new_message_form.validate_on_submit():
            new_message = models.Message(message_type_id=(models.MessageTypes.action if int(new_message_form.message_type.data) == models.MessageTypes.action else models.MessageTypes.speech), content=new_message_form.content.data, sender_id=character.id, recipient_id=chat_recipient.id, timestamp=datetime.datetime.utcnow())
            models.db.session.add(new_message)
            models.db.session.commit()
    chat_read_up_to = models.ChatReadUpTo.query.filter_by(user_id=current_user.id, recipient_id=chat_recipient.id).first()
    read_from = datetime.datetime.fromtimestamp(0)
    if chat_read_up_to is not None and chat_read_up_to.timestamp is not None:
        read_from = chat_read_up_to.timestamp
    messages = models.Message.query.filter_by(recipient_id=chat_recipient.id).order_by(models.Message.timestamp.desc()).paginate(page=int(request.args.get('page', 1)), per_page=50)
    return render_template("chat.html", messages=messages, new_message_form=new_message_form)


@login_required
@app.route('/characters/', methods=['GET', 'POST'])
def characters():
    new_form = forms.NewCharacterForm(request.form)
    characters = models.Character.query.filter_by(user_id=current_user.id).paginate(page=int(request.args.get('page', 1)))
    if request.method == 'GET':
        return render_template("characters.html", characters=characters, new_form=new_form)
    elif request.method == 'POST':
        if new_form.validate_on_submit():
            new_character = models.Character(name=new_form.name.data, bio=new_form.bio.data, user_id=current_user.id)
            models.db.session.add(new_character)
            models.db.session.commit()
            return redirect(url_for('character', character_id=new_character.id))
        else:
            return render_template("characters.html", characters=characters, new_form=new_form)


@login_required
@app.route('/dm/characters/')
def dm_characters():
    characters = models.Character.query.filter_by(user_id=current_user.id).paginate(page=int(request.args.get('page', 1)))
    return render_template("characters.html", characters=characters)


@login_required
@app.route('/characters/<character_id>')
def character(character_id):
    character = models.Character.query.filter_by(id=character_id, user_id=current_user.id).first_or_404()
    return render_template("character.html", character=character)


@login_required
@app.route('/campaigns/<campaign_id>/invitations/', methods=['POST'])
def invitations(campaign_id):
    campaign = models.Campaign.query.filter_by(id=campaign_id, user_id=current_user.id).first_or_404()
    new_invitation = models.Invitation(campaign_id=campaign.id)
    models.db.session.add(new_invitation)
    models.db.session.commit()
    return redirect(url_for('dm_campaign', campaign_id=campaign.id))


@login_required
@app.route('/invitations/<invitation_id>')
def invitation(invitation_id):
    invitation = models.Invitation.query.filter_by(id=invitation_id).first_or_404()
    characters = models.Character.query.filter_by(user_id=current_user.id).paginate(page=int(request.args.get('page', 1)))
    return render_template("invitation.html", invitation=invitation, characters=characters)


@login_required
@app.route('/invitations/<invitation_id>/fulfilments/<character_id>', methods=['POST'])
def invitation_fulfilment(invitation_id, character_id):
    invitation = models.Invitation.query.filter_by(id=invitation_id).first_or_404()
    character = models.Character.query.filter_by(id=character_id).first_or_404()
    campaign = invitation.campaign
    campaign.characters.append(character)
    models.db.session.delete(invitation)
    models.db.session.commit()
    return redirect(url_for('campaign', campaign_id=campaign.id))


