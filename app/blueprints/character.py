from flask import Blueprint, render_template, request
import flask_login
from werkzeug.datastructures import MultiDict
import logging

from tabletop_story.models import GameCharacter
from tabletop_story.forms import CharacterForm
from tabletop_story.plugins import db


LOG = logging.getLogger(__package__)


blueprint = Blueprint(
    "character",
    __name__,
    static_folder="../static",
    template_folder="../templates/character",
)


@blueprint.route("/edit/<character_id>", methods=["GET", "POST"])
@flask_login.login_required
def edit_character(character_id):
    db_character = GameCharacter.query.get(character_id)
    if db_character.user_id != int(flask_login.current_user.get_id()):
        abort(403)
    data = db_character.as_dict()
    if request.method == "POST":
        form = CharacterForm()
        if form.validate_on_submit():
            for field in form._fields:
                data[field] = form._fields[field].data
            del data["csrf_token"]
            del data["submit"]
            db_character.name = form.name.data
            db_character.update_data(data)
            db.session.add(db_character)
            db.session.commit()
    character = db_character.character
    form = CharacterForm(
        formdata=MultiDict(
            {
                "name": character.name,
                "age": character.age,
                "gender": character.gender,
                "description": character.description,
                "biography": character.biography,
                "class_name": character.class_name,
                "constitution": character.constitution,
                "strength": character.strength,
                "dexterity": character.dexterity,
                "wisdom": character.wisdom,
                "intelligence": character.intelligence,
                "charisma": character.charisma,
                "alignment": character.alignment,
            }
        )
    )
    return render_template(
        "edit_character.html",
        character=character,
        form=form,
    )


@blueprint.route("/view/<character_id>")
@flask_login.login_required
def view_character(character_id):
    db_character = GameCharacter.query.get(character_id)
    if db_character.user_id != int(flask_login.current_user.get_id()):
        abort(403)
    character = db_character.character
    character.image = (
        db_character.image if db_character.image is not None else "potato.jpg"
    )
    return render_template(
        "view_character.html",
        character=character,
    )
