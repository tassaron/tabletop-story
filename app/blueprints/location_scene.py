from flask import Blueprint, render_template, abort, redirect, url_for, request
from flask_login import login_required, current_user
from wtforms import SelectField
from werkzeug.datastructures import MultiDict
from tabletop_story.models import (
    GameCampaign,
    CampaignLocation,
    LocationScene,
    SceneNPC,
)
from tabletop_story.forms import GenericCreateForm, GenericEditForm, GenericForm
from tabletop_story.plugins import db
from is_safe_url import is_safe_url


blueprint = Blueprint(
    "location/scene", __name__, template_folder="../templates/campaign"
)


@blueprint.route("/<location_id>/activate", methods=["GET", "POST"])
@login_required
def activate_location_scene(location_id):
    location = CampaignLocation.query.get(location_id)
    if location is None:
        abort(404)
    campaign = GameCampaign.query.get(location.campaign_id)
    user_id = int(current_user.get_id())
    if campaign is None:
        abort(404)
    elif campaign.gamemaster != user_id:
        abort(403)
    if campaign.active_location != int(location_id):
        abort(400)

    # subclass a generic form and add this location's list of scenes
    class LocationSceneListForm(GenericForm):
        pass

    scenes = [
        (scene.id, scene.name)
        for scene in LocationScene.query.filter_by(location_id=location_id).all()
    ]
    setattr(
        LocationSceneListForm,
        "scene",
        SelectField(
            "Choose a Scene",
            choices=[(0, "None"), *scenes],
        ),
    )

    form = LocationSceneListForm()
    if form.validate_on_submit():
        campaign.set_combat(form.scene.data)
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for("campaign.view_campaign", campaign_id=campaign.id))

    return render_template(
        "activate_scene.html",
        logged_in=True,
        form=form,
        campaign=campaign,
        location=location,
        active_scene=LocationScene.query.get(campaign.get_combat().scene_id),
    )


@blueprint.route("/<location_id>/create", methods=["GET", "POST"])
@login_required
def create_location_scene(location_id):
    location = CampaignLocation.query.get(location_id)
    if location is None:
        abort(404)
    campaign = GameCampaign.query.get(location.campaign_id)
    user_id = int(current_user.get_id())
    if campaign is None:
        abort(404)
    elif campaign.gamemaster != user_id:
        abort(403)

    form = GenericCreateForm()
    if form.validate_on_submit():
        scene = LocationScene(
            name=form.name.data,
            location_id=location_id,
        )
        db.session.add(scene)
        db.session.commit()
        next_page = request.args.get("next")
        return (
            redirect(next_page)
            if next_page and is_safe_url(next_page, url_for("dashboard.index"))
            else redirect(url_for(".edit_location_scene", scene_id=scene.id))
        )

    return render_template(
        "create_generic.html",
        logged_in=True,
        form=form,
        title=f'Scene in "{location.name}"',
    )


@blueprint.route("/edit/<scene_id>/", methods=["GET", "POST"])
@login_required
def edit_location_scene(scene_id):
    scene = LocationScene.query.get(scene_id)
    if scene is None:
        abort(404)
    location = CampaignLocation.query.get(scene.location_id)
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
        scene.name = form.name.data
        scene.description = form.description.data
        db.session.add(scene)
        db.session.commit()
        return redirect(
            url_for(
                ".view_location_scene",
                scene_id=scene_id,
            )
        )

    filled_form = {
        "name": scene.name,
        "description": scene.description,
    }
    form = GenericEditForm(formdata=MultiDict(filled_form))
    return render_template(
        "edit_scene.html",
        logged_in=True,
        form=form,
        campaign=campaign,
        location=location,
        scene=scene,
    )


@blueprint.route("/view/<scene_id>")
@login_required
def view_location_scene(scene_id):
    scene = LocationScene.query.get(scene_id)
    if scene is None:
        abort(404)
    location = CampaignLocation.query.get(scene.location_id)
    if location is None:
        abort(404)
    campaign = GameCampaign.query.get(location.campaign_id)
    if campaign is None:
        abort(404)
    if campaign.gamemaster != int(current_user.get_id()):
        abort(403)

    npcs = SceneNPC.query.filter_by(scene_id=scene_id).all()
    return render_template(
        "view_scene.html",
        logged_in=True,
        campaign=campaign,
        location=location,
        scene=scene,
        npcs=npcs,
    )
