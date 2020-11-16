from flask import Blueprint, render_template, abort, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.datastructures import MultiDict
from tabletop_story.models import GameCampaign, CampaignLocation
from tabletop_story.forms import CreateCampaignForm, EditLocationForm
from tabletop_story.plugins import db


blueprint = Blueprint(
    "campaign/location", __name__, template_folder="../templates/campaign"
)


@blueprint.route("/<campaign_id>/create", methods=["GET", "POST"])
@login_required
def create_campaign_location(campaign_id):
    campaign = GameCampaign.query.get(campaign_id)
    user_id = int(current_user.get_id())
    if campaign is None:
        abort(404)
    elif campaign.gamemaster != user_id:
        abort(403)

    form = CreateCampaignForm()
    if form.validate_on_submit():
        location = CampaignLocation(
            name=form.name.data,
            campaign_id=campaign_id,
        )
        db.session.add(location)
        db.session.commit()
        return redirect(
            url_for(
                ".edit_campaign_location",
                location_id=location.id,
            )
        )

    return render_template(
        "create_campaign.html",
        logged_in=True,
        form=form,
        title="Location",
    )


@blueprint.route("/edit/<location_id>/", methods=["GET", "POST"])
@login_required
def edit_campaign_location(location_id):
    location = CampaignLocation.query.get(location_id)
    if location is None:
        abort(404)
    campaign = GameCampaign.query.get(location.campaign_id)
    if campaign is None:
        abort(404)
    user_id = int(current_user.get_id())
    if user_id != campaign.gamemaster:
        abort(403)

    form = EditLocationForm()
    if form.validate_on_submit():
        location.name = form.name.data
        location.description = form.description.data
        db.session.add(location)
        db.session.commit()
        return redirect(
            url_for(
                ".view_campaign_location",
                location_id=location_id,
            )
        )

    filled_form = {
        "name": location.name,
        "description": location.description,
    }
    form = EditLocationForm(formdata=MultiDict(filled_form))
    return render_template(
        "edit_location.html",
        logged_in=True,
        form=form,
        campaign_id=campaign.id,
        campaign=campaign,
        location_id=location_id,
        location=location,
    )


@blueprint.route("/view/<location_id>")
@login_required
def view_campaign_location(location_id):
    location = CampaignLocation.query.get(location_id)
    if location is None:
        abort(404)
    campaign = GameCampaign.query.get(location.campaign_id)
    if campaign is None:
        abort(404)
    if campaign.gamemaster != int(current_user.get_id()):
        abort(403)

    return render_template(
        "view_location.html",
        logged_in=True,
        campaign=campaign,
        location=location,
    )
