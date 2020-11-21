from flask import Blueprint, render_template, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.datastructures import MultiDict
from tabletop_story.models import (
    GameCampaign,
    GameCharacter,
    CampaignLocation,
    LocationScene,
    SceneNPC,
)
from tabletop_story.forms import GenericCreateForm, EditCampaignForm
from tabletop_story.plugins import db
from tabletop_story.blueprints import charimg
import logging


LOG = logging.getLogger(__package__)


blueprint = Blueprint("campaign", __name__, template_folder="../templates/campaign")


@blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create_campaign():
    form = GenericCreateForm()

    if form.validate_on_submit():
        campaign = GameCampaign(
            name=form.name.data,
            gamemaster=int(current_user.get_id()),
            active_location=0,
        )
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for(".edit_campaign", campaign_id=campaign.id))

    return render_template(
        "create_generic.html",
        logged_in=True,
        form=form,
        title="Campaign",
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

    filled_form = {
        "name": campaign.name,
        "character1": "" if campaign.character1 is None else campaign.character1,
        "character2": "" if campaign.character2 is None else campaign.character2,
        "character3": "" if campaign.character3 is None else campaign.character3,
        "character4": "" if campaign.character4 is None else campaign.character4,
        "character5": "" if campaign.character5 is None else campaign.character5,
        "character6": "" if campaign.character6 is None else campaign.character6,
    }
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

    if is_gamemaster:
        # the gamemaster can edit every character
        editable_characters = [
            GameCharacter.query.get(char_id) if char_id is not None else char_id
            for char_id in campaign.characters()
        ]
        other_characters = []
    else:
        # get list of characters belonging to this player
        all_user_characters = GameCharacter.query.filter_by(user_id=user_id).all()
        editable_characters = []
        other_characters = campaign.characters()
        for db_character in all_user_characters:
            if db_character.id in campaign.characters():
                editable_characters.append(db_character)
                other_characters.remove(db_character.id)
        if not editable_characters:
            # none of this user's characters are invited to this campaign
            abort(403)
        other_characters = [
            GameCharacter.query.get(char_id) if char_id is not None else char_id
            for char_id in other_characters[:]
        ]

    characters = []
    for db_character in editable_characters:
        if db_character is not None:
            character = db_character.character
            character.image = charimg.charimg(*list(db_character.design.values()))
            character.dbid = db_character.id
            characters.append(character)

    for db_character in other_characters:
        if db_character is not None:
            db_character.image = charimg.charimg(*list(db_character.design.values()))

    locations = []
    scenes = {}
    npcs = {}
    if is_gamemaster:
        locations = CampaignLocation.query.filter_by(campaign_id=campaign_id).all()
        scenes = {
            location.id: LocationScene.query.filter_by(location_id=location.id).all()
            for location in locations
        }
        for scene_list in scenes.values():
            for scene in scene_list:
                npcs[scene.id] = SceneNPC.query.filter_by(scene_id=scene.id).all()
    next_page = f"?next={url_for('.view_campaign', campaign_id=campaign_id)}"
    active_location = CampaignLocation.query.get(campaign.active_location)
    combat = campaign.get_combat()
    active_scene = LocationScene.query.get(combat.scene_id)

    LOG.info(combat)

    return render_template(
        "view_campaign.html",
        logged_in=True,
        is_gamemaster=is_gamemaster,
        campaign=campaign,
        combat=combat,
        active_location=active_location,
        active_scene=active_scene,
        locations=locations,
        scenes=scenes,
        npcs=npcs,
        next_page=next_page,
        characters=characters,
        other_characters=other_characters,
    )


@blueprint.route("/combat/<campaign_id>/toggle")
@login_required
def toggle_combat(campaign_id):
    campaign = GameCampaign.query.get(campaign_id)
    if campaign is None:
        abort(404)
    user_id = int(current_user.get_id())
    if user_id != campaign.gamemaster:
        abort(403)
    combat = campaign.get_combat()
    if combat.scene_id == 0:
        abort(400)
    combat.active = not combat.active
    campaign.combat_data = str(combat)
    db.session.add(campaign)
    db.session.commit()
    flash(str(combat))
    return redirect(url_for(".view_campaign", campaign_id=campaign_id))
