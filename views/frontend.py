from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

import forms

from web import app

from persistence import models


@app.route('/')
def home():
    return render_template("index.html")


@login_required
@app.route('/dm/campaigns/', methods=['GET', 'POST'])
def dm_campaigns():
    new_form = forms.NewCampaignForm(request.form)
    if request.method == 'GET':
        # campaigns = models.db.session.query(models.Campaign).join(models.campaign_characters).join(models.Character).filter(models.Character.user_id == current_user.id).paginate(page=request.args.get('page', 1))
        campaigns = models.Campaign.query.filter_by(user_id=current_user.id).paginate(page=request.args.get('page', 1))
        return render_template("campaigns.html", campaigns=campaigns, new_form=new_form)
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
        campaigns = models.db.session.query(models.Campaign).join(models.campaign_characters).join(models.Character).filter(models.Character.user_id == current_user.id).paginate(page=request.args.get('page', 1))
        return render_template("campaigns.html", campaigns=campaigns)


@login_required
@app.route('/campaigns/<campaign_id>')
def campaign(campaign_id):
    campaign = models.Campaign.query.filter_by(id=campaign_id, user_id=current_user.id).first_or_404()
    return render_template("campaign.html", campaign=campaign)



@login_required
@app.route('/characters/')
def characters():
    characters = models.Character.query.filter_by(user_id=current_user.id).paginate(page=request.args.get('page', 1))
    return render_template("characters.html", characters=characters)


@login_required
@app.route('/dm/characters/')
def dm_characters():
    characters = models.Character.query.filter_by(user_id=current_user.id).paginate(page=request.args.get('page', 1))
    return render_template("characters.html", characters=characters)


@login_required
@app.route('/characters/<character_id>')
def character(character_id):
    character = models.Character.query.filter_by(character_id=character_id, user_id=current_user.id).first_or_404()
    return render_template("character.html", character=character)

