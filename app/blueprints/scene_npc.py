from flask import Blueprint, render_template, abort, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.datastructures import MultiDict
from tabletop_story.models import (
    GameCampaign,
    CampaignLocation,
    LocationScene,
    SceneNPC,
)
from tabletop_story.forms import GenericCreateForm, EditNPCForm
from tabletop_story.plugins import db
from is_safe_url import is_safe_url


blueprint = Blueprint("scene/npc", __name__, template_folder="../templates/campaign")


@blueprint.route("/<scene_id>/create", methods=["GET", "POST"])
@login_required
def create_scene_npc(scene_id):
    scene = LocationScene.query.get(scene_id)
    if scene is None:
        abort(404)
    location = CampaignLocation.query.get(scene.location_id)
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
        npc = SceneNPC(
            name=form.name.data,
            scene_id=scene_id,
            data="{}",
        )
        db.session.add(npc)
        db.session.commit()
        next_page = request.args.get("next")
        return (
            redirect(next_page)
            if next_page and is_safe_url(next_page, url_for("dashboard.index"))
            else redirect(url_for(".view_scene_npc", npc_id=npc.id))
        )

    return render_template(
        "create_generic.html",
        logged_in=True,
        form=form,
        title=f'NPC in "{scene.name}"',
    )


@blueprint.route("/edit/<npc_id>/", methods=["GET", "POST"])
@login_required
def edit_scene_npc(npc_id):
    npc = SceneNPC.query.get(npc_id)
    if npc is None:
        abort(404)
    scene = LocationScene.query.get(npc.scene_id)
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

    form = EditNPCForm()
    if form.validate_on_submit():
        npc.name = form.name.data
        db.session.add(npc)
        db.session.commit()
        return redirect(
            url_for(
                ".view_scene_npc",
                npc_id=npc.id,
            )
        )

    filled_form = {
        "name": npc.name,
    }
    form = EditNPCForm(formdata=MultiDict(filled_form))
    return render_template(
        "edit_npc.html",
        logged_in=True,
        form=form,
        campaign=campaign,
        location=location,
        scene=scene,
        npc=npc,
    )


@blueprint.route("/view/<npc_id>")
@login_required
def view_scene_npc(npc_id):
    npc = SceneNPC.query.get(npc_id)
    if npc is None:
        abort(404)
    scene = LocationScene.query.get(npc.scene_id)
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

    return render_template(
        "view_npc.html",
        logged_in=True,
        campaign=campaign,
        location=location,
        scene=scene,
        npc=npc,
    )
