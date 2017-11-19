from flask import render_template, request
from flask_login import login_required, current_user

import forms

from web import app

from persistence import models


@app.route('/')
def home():
    return render_template("index.html")


@login_required
@app.route('/campaigns/', methods=['GET', 'POST'])
def my_campaigns():
    if request.method == 'GET':
        new_form = forms.NewCampaignForm()
        characters = models.Character.query.filter_by(user_id=current_user.id).all()
        campaigns = models.Campaign.query.filter(models.Campaign.id.in_(c.id for c in characters)).paginate(page=request.args.get('page', 1))
        return render_template("campaigns.html", campaigns=campaigns, new_form=new_form)

"""
@login_required
@app.route('/campaigns/<campaign_id>')
def my_campaign(campaign_id):
    return render_template("campaign.html", campaign=campaign)
"""


@login_required
@app.route('/characters/')
def my_characters():
    characters = models.Character.query.filter_by(user_id=current_user.id).get_or_404()
    return render_template("characters.html", characters=characters)


@login_required
@app.route('/characters/<character_id>')
def my_character(character_id):
    character = models.Character.query.filter(character_id=character_id, user_id=current_user.id).first_or_404()
    return render_template("character.html", character=character)

