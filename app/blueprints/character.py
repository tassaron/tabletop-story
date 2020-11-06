from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
import flask_login
from werkzeug.datastructures import MultiDict
import logging

from tabletop_story.models import User, GameCharacter
from tabletop_story.forms import EditCharacterForm, DeleteCharacterForm
from tabletop_story.plugins import db
from dnd_character import Character
from dnd_character.classes import CLASSES


LOG = logging.getLogger(__package__)


blueprint = Blueprint(
    "character",
    __name__,
    static_folder="../static",
    template_folder="../templates/character",
)


@blueprint.route("/create")
@flask_login.login_required
def create_character_choice():
    return render_template(
        "new_character.html",
        logged_in=True,
        classes=CLASSES.keys(),
    )


@blueprint.route("/create/<class_key>")
@flask_login.login_required
def create_character_chosen(class_key):
    new_char = Character(classs=CLASSES[class_key], name="New Character")
    db_char = GameCharacter(
        user_id=int(flask_login.current_user.get_id()),
        name=new_char.name,
        data_keys=str(new_char.keys()),
        data_vals=str(new_char.values()),
    )
    db.session.add(db_char)
    db.session.commit()
    return redirect(url_for(".edit_character", character_id=db_char.id))


@blueprint.route("/delete/<character_id>", methods=["GET", "POST"])
@flask_login.login_required
def delete_character(character_id):
    db_character = GameCharacter.query.get(character_id)
    if db_character.user_id != int(flask_login.current_user.get_id()):
        abort(403)
    form = DeleteCharacterForm()
    if form.validate_on_submit() and form.name.data == db_character.name:
        db.session.delete(db_character)
        db.session.commit()
        flash(f"{db_character.name} was deleted forever! 💥", "info")
        return redirect(url_for("dashboard.index"))
    return render_template(
        "delete_character.html",
        logged_in=True,
        form=form,
        name=db_character.name,
    )


@blueprint.route("/edit/<character_id>", methods=["GET", "POST"])
@flask_login.login_required
def edit_character(character_id):
    db_character = GameCharacter.query.get(character_id)
    if db_character.user_id != int(flask_login.current_user.get_id()):
        abort(403)
    data = db_character.as_dict()
    if request.method == "POST":
        form = EditCharacterForm()
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
    form = EditCharacterForm(
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
        logged_in=True,
        character=character,
        form=form,
    )


@blueprint.route("/view/<character_id>")
def view_character(character_id):
    db_character = GameCharacter.query.get(character_id)
    can_edit = False
    logged_in = flask_login.current_user.is_authenticated
    if logged_in and db_character.user_id == int(flask_login.current_user.get_id()):
        can_edit = True
    character = db_character.character
    character.image = (
        db_character.image if db_character.image is not None else "potato.jpg"
    )
    return render_template(
        "view_character.html",
        logged_in=logged_in,
        character=character,
        can_edit=can_edit,
    )


@blueprint.route("/edit/<character_id>/exp/<number>")
@flask_login.login_required
def edit_character_experience(character_id, number):
    db_character = GameCharacter.query.get(character_id)
    if db_character.user_id != int(flask_login.current_user.get_id()):
        abort(403)
    try:
        number = int(number)
    except ValueError:
        abort(400)
    char = db_character.character
    char.experience += number
    db_character.update_data(dict(char))
    db.session.add(db_character)
    db.session.commit()
    plural = "s" if number not in (1, -1) else ""
    if number > -1:
        flash(f"Added {str(number)} experience point{plural} to {char.name}", "info")
    else:
        flash(
            f"Depleted {str(number*-1)} experience point{plural} from {char.name}",
            "info",
        )
    return redirect(url_for(".view_character", character_id=character_id))
