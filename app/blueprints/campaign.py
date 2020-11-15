from flask import Blueprint, render_template, abort, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.datastructures import MultiDict
from tabletop_story.models import GameCampaign, GameCharacter
from tabletop_story.forms import CreateCampaignForm, EditCampaignForm
from tabletop_story.plugins import db


blueprint = Blueprint("campaign", __name__, template_folder="../templates/campaign")


@blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create_campaign():
    form = CreateCampaignForm()

    if form.validate_on_submit():
        campaign = GameCampaign(
            name=form.name.data, gamemaster=int(current_user.get_id())
        )
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for(".edit_campaign", campaign_id=campaign.id))

    return render_template(
        "create_campaign.html",
        logged_in=True,
        form=form,
    )


@blueprint.route("/edit/<campaign_id>/", methods=["GET", "POST"])
@login_required
def edit_campaign(campaign_id):
    campaign = GameCampaign.query.get(campaign_id)
    if campaign is None:
        abort(404)
    user_id = int(current_user.get_id())
    if user_id != campaign.gamemaster:
        abort(403)

    form = EditCampaignForm()
    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.character1 = form.character1.data
        campaign.character2 = form.character2.data
        campaign.character3 = form.character3.data
        campaign.character4 = form.character4.data
        campaign.character5 = form.character5.data
        campaign.character6 = form.character6.data
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for(".view_campaign", campaign_id=campaign_id))

    filled_form = {"name": campaign.name}
    form = EditCampaignForm(formdata=MultiDict(filled_form))
    return render_template(
        "edit_campaign.html",
        logged_in=True,
        form=form,
        campaign_id=campaign_id,
        campaign=campaign,
    )


@blueprint.route("/view/<campaign_id>")
@login_required
def view_campaign(campaign_id):
    campaign = GameCampaign.query.get(campaign_id)
    if campaign is None:
        abort(404)
    user_id = int(current_user.get_id())
    is_gamemaster = user_id == campaign.gamemaster
    if not is_gamemaster:
        characters = GameCharacter.query.filter_by(user_id=user_id).all()
        for character in characters:
            if character in campaign.characters:
                break
        else:
            # none of this user's characters are invited to this campaign
            abort(403)
    return render_template(
        "view_campaign.html",
        logged_in=True,
        can_edit=is_gamemaster,
        campaign_id=campaign_id,
        campaign=campaign,
        combat=campaign.combat,
    )
