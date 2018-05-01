from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user

from chat import forms

from chat.web import app

from chat.persistence import models


@app.route('/')
def home():
    return render_template("index.html")


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
            return redirect(url_for('campaign', campaign_id=new_campaign.id))


@login_required
@app.route('/campaigns/', methods=['GET', 'POST'])
def campaigns():
    if request.method == 'GET':
        campaigns = models.db.session.query(models.Campaign).join(models.campaign_characters).join(models.Character).filter(
            models.Character.user_id == current_user.id).paginate(page=int(request.args.get('page', 1)))
        return render_template("campaigns.html", campaigns=campaigns)


@login_required
@app.route('/campaigns/<campaign_id>')
def campaign(campaign_id):
    campaign = models.Campaign.query.filter_by(id=campaign_id, user_id=current_user.id).first_or_404()
    return render_template("campaign.html", campaign=campaign)



@login_required
@app.route('/characters/', methods=['GET', 'POST'])
def characters():
    new_form = forms.NewCharacterForm(request.form)
    if request.method == 'GET':
        characters = models.Character.query.filter_by(user_id=current_user.id).paginate(page=int(request.args.get('page', 1)))
        return render_template("characters.html", characters=characters, new_form=new_form)
    elif request.method == 'POST':
        if new_form.validate_on_submit():
            new_character = models.Character(name=new_form.name.data, bio=new_form.bio.data, user_id=current_user.id)
            models.db.session.add(new_character)
            models.db.session.commit()
            return redirect(url_for('character', character_id=new_character.id))


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
    return redirect(url_for('campaign', campaign_id=campaign.id))


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


