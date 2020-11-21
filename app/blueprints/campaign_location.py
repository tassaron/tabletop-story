from flask import Blueprint, render_template, abort, redirect, url_for, request
from flask_login import login_required, current_user
from wtforms import SelectField
from werkzeug.datastructures import MultiDict
from tabletop_story.models import GameCampaign, CampaignLocation, LocationScene
from tabletop_story.forms import GenericCreateForm, GenericEditForm, GenericForm
from tabletop_story.plugins import db
from is_safe_url import is_safe_url


blueprint = Blueprint(
    "campaign/location", __name__, template_folder="../templates/campaign"
)


@blueprint.route("/<campaign_id>/activate/<location_id>")
@login_required
def activate_campaign_location_post(campaign_id, location_id):
    return activate_campaign_location(campaign_id, location_id)


@blueprint.route("/<campaign_id>/activate", methods=["GET", "POST"])
@login_required
def activate_campaign_location(campaign_id, location_id=None):
    campaign = GameCampaign.query.get(campaign_id)
    user_id = int(current_user.get_id())
    if campaign is None:
        abort(404)
    elif campaign.gamemaster != user_id:
        abort(403)

    if location_id is None:
        # subclass a generic form and add this campaign's list of locations
        class CampaignLocationListForm(GenericForm):
            pass

        locations = [
            (location.id, location.name)
            for location in CampaignLocation.query.filter_by(
                campaign_id=campaign_id
            ).all()
        ]
        setattr(
            CampaignLocationListForm,
            "location",
            SelectField(
                "Choose a Location",
                choices=[(0, "None"), *locations],
            ),
        )
        form = CampaignLocationListForm()

    if location_id is not None or form.validate_on_submit():
        if request.method == "POST":
            location_id = form.location.data
        if campaign.active_location != location_id:
            campaign.active_location = location_id
            campaign.set_combat(0, [])
            db.session.add(campaign)
            db.session.commit()
        return redirect(url_for("campaign.view_campaign", campaign_id=campaign_id))

    form = CampaignLocationListForm(
        formdata=MultiDict({"location": campaign.active_location})
    )
    return render_template(
        "activate_location.html", logged_in=True, form=form, campaign=campaign
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

    form = GenericCreateForm()
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
        "create_generic.html",
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

    form = GenericEditForm()
    if form.validate_on_submit():
        location.name = form.name.data
        location.description = form.description.data
        db.session.add(location)
        db.session.commit()
        next_page = request.args.get("next")
        return (
            redirect(next_page)
            if next_page and is_safe_url(next_page, url_for("dashboard.index"))
            else redirect(url_for(".view_campaign_location", location_id=location_id))
        )

    filled_form = {
        "name": location.name,
        "description": location.description,
    }
    form = GenericEditForm(formdata=MultiDict(filled_form))
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

    scenes = LocationScene.query.filter_by(location_id=location_id).all()
    return render_template(
        "view_location.html",
        logged_in=True,
        campaign=campaign,
        location=location,
        scenes=scenes,
    )
