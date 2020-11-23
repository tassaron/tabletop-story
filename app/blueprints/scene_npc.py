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
from tabletop_story.forms import GenericForm, GenericCreateForm, EditNPCForm
from tabletop_story.plugins import db
from tabletop_story.dnd_campaign import NPC
from is_safe_url import is_safe_url
from dnd_character.monsters import SRD_monsters


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

    class CreateNPCForm(GenericCreateForm):
        pass

    setattr(
        CreateNPCForm,
        "template",
        SelectField(
            "Template to base NPC on:",
            choices=[
                (monster["index"], monster["name"]) for monster in SRD_monsters.values()
            ],
        ),
    )

    form = CreateNPCForm()
    if form.validate_on_submit():
        data = NPC.from_template(SRD_monsters[form.template.data]).as_dict()
        data["name"] = form.name.data
        npc = SceneNPC(
            name=form.name.data,
            scene_id=scene_id,
            data=str(data),
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
        "create_npc.html",
        SRD_disclaimer=True,
        logged_in=True,
        form=form,
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
        # Most fields match up with attributes of Character
        data = npc.as_dict()
        for field in form._fields:
            data[field] = form._fields[field].data
        del data["csrf_token"]
        del data["submit"]
        data["actions"] = [line for line in data["actions"].split("\n")]
        data["proficiencies"] = [line for line in data["proficiencies"].split("\n")]
        data["abilities"] = [line for line in data["abilities"].split("\n")]

        npc.data = str(data)
        db.session.add(npc)
        db.session.commit()
        next_page = request.args.get("next")
        return (
            redirect(next_page)
            if next_page and is_safe_url(next_page, url_for("dashboard.index"))
            else redirect(url_for(".view_scene_npc", npc_id=npc.id))
        )

    elif request.method == "GET":
        data = npc.npc
        filled_form = {
            "name": data.name,
            "description": data.description,
            "experience": data.experience,
            "hit_points": data.hit_points,
            "max_hit_points": data.max_hit_points,
            "armour_class": data.armour_class,
            "passive_perception": data.passive_perception,
            "constitution": data.constitution,
            "strength": data.strength,
            "dexterity": data.dexterity,
            "wisdom": data.wisdom,
            "intelligence": data.intelligence,
            "charisma": data.charisma,
            "actions": "\n".join(data.actions),
            "proficiencies": "\n".join(data.proficiencies),
            "abilities": "\n".join(data.abilities),
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


@blueprint.route("/get/<npc_id>/<attr>")
@login_required
def get_npc(npc_id, attr):
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

    NPC = npc.npc
    NPC.id = npc.id
    html = render_template(
        "view_npc.html",
        npc=NPC,
        embedded_card=True,
    )
    data = npc.as_dict()
    if attr == "card":
        monster_json = data
        monster_json["html"] = html
        return monster_json
    elif attr not in data:
        abort(400)
    return jsonify(data[attr])


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

    NPC = npc.npc
    NPC.id = npc.id
    return render_template(
        "view_npc.html",
        logged_in=True,
        campaign=campaign,
        location=location,
        scene=scene,
        npc=NPC,
    )


@blueprint.route("/delete/<npc_id>", methods=["GET", "POST"])
@login_required
def delete_scene_npc(npc_id):
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

    form = GenericForm()
    if form.validate_on_submit():
        db.session.delete(npc)
        db.session.commit()
        return redirect(
            url_for("location/scene.view_location_scene", scene_id=scene.id)
        )

    return render_template(
        "delete_npc.html",
        logged_in=True,
        campaign=campaign,
        location=location,
        scene=scene,
        npc=npc,
        form=form,
    )


@blueprint.route("/copy/<npc_id>", methods=["GET", "POST"])
@login_required
def copy_scene_npc(npc_id):
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
        npc=npc.npc,
    )


@blueprint.route("/move/<npc_id>", methods=["GET", "POST"])
@login_required
def move_scene_npc(npc_id):
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
        npc=npc.npc,
    )
