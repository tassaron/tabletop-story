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
from wtforms import BooleanField
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
    new_char = Character(
        classs=CLASSES[class_key],
        name="New Character",
        age="Unknown",
        gender="Unknown",
        alignment="LG",
        description="A human",
        biography="",
    )
    db_char = GameCharacter(
        user_id=int(flask_login.current_user.get_id()),
        name=new_char.name,
        data_keys=str(new_char.keys()),
        data_vals=str(new_char.values()),
        image="potato.jpg",
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

    # Subclass the edit form so we can add fields dynamically
    class ThisEditCharacterForm(EditCharacterForm):
        pass

    for i, class_feature in enumerate(data["class_features"].values()):
        setattr(
            ThisEditCharacterForm,
            f"class_feature_{i}",
            BooleanField(class_feature["name"]),
        )

    if request.method == "POST":
        form = ThisEditCharacterForm()
        if form.validate_on_submit():
            for field in form._fields:
                data[field] = form._fields[field].data
            del data["csrf_token"]
            del data["submit"]
            data["class_features_enabled"] = [
                not data.pop(f"class_feature_{i}")
                for i in range(len(data["class_features"]))
            ]
            new_data = {}
            removals = []
            for field in data:
                if not field.startswith("skills_"):
                    continue
                try:
                    key1, key2, key3 = field.split("_", 2)
                except ValueError:
                    continue
                key = "_".join((key1, key2))
                if key3 == "hagrid":
                    key3 = "animal-handling"
                elif key3 == "raistlin":
                    key3 = "sleight-of-hand"
                if key not in new_data:
                    new_data[key] = {}
                new_data[key].update({key3: data[field]})
                removals.append(field)
            for field in removals:
                data.pop(field)
            data.update(new_data)
            LOG.info(data)
            db_character.name = form.name.data
            db_character.update_data(data)
            db.session.add(db_character)
            db.session.commit()
    character = db_character.character
    filled_form = {
        "name": character.name,
        "age": character.age,
        "gender": character.gender,
        "description": character.description,
        "biography": character.biography,
        "class_name": character.class_name,
        "alignment": character.alignment,
        "constitution": character.constitution,
        "strength": character.strength,
        "dexterity": character.dexterity,
        "wisdom": character.wisdom,
        "intelligence": character.intelligence,
        "charisma": character.charisma,
        "skills_strength_athletics": character.skills_strength["athletics"],
        "skills_dexterity_acrobatics": character.skills_dexterity["acrobatics"],
        "skills_dexterity_raistlin": character.skills_dexterity["sleight-of-hand"],
        "skills_dexterity_stealth": character.skills_dexterity["stealth"],
        "skills_wisdom_hagrid": character.skills_wisdom["animal-handling"],
        "skills_wisdom_insight": character.skills_wisdom["insight"],
        "skills_wisdom_medicine": character.skills_wisdom["medicine"],
        "skills_wisdom_perception": character.skills_wisdom["perception"],
        "skills_wisdom_survival": character.skills_wisdom["survival"],
        "skills_intelligence_arcana": character.skills_intelligence["arcana"],
        "skills_intelligence_history": character.skills_intelligence["history"],
        "skills_intelligence_investigation": character.skills_intelligence[
            "investigation"
        ],
        "skills_intelligence_nature": character.skills_intelligence["nature"],
        "skills_intelligence_religion": character.skills_intelligence["religion"],
        "skills_charisma_deception": character.skills_charisma["deception"],
        "skills_charisma_intimidation": character.skills_charisma["intimidation"],
        "skills_charisma_performance": character.skills_charisma["performance"],
        "skills_charisma_persuasion": character.skills_charisma["persuasion"],
    }
    filled_form.update(
        {
            f"class_feature_{i}": not character.class_features_enabled[i]
            for i in range(len(character.class_features))
        }
    )
    form = ThisEditCharacterForm(formdata=MultiDict(filled_form))
    return render_template(
        "edit_character.html",
        logged_in=True,
        character=character,
        form=form,
        character_id=character_id,
        character_img=db_character.image,
        class_features=[
            form._fields[f"class_feature_{i}"]
            for i in range(len(data["class_features"]))
        ],
    )


@blueprint.route("/view/<character_id>")
def view_character(character_id):
    db_character = GameCharacter.query.get(character_id)
    can_edit = False
    logged_in = flask_login.current_user.is_authenticated
    if logged_in and db_character.user_id == int(flask_login.current_user.get_id()):
        can_edit = True
    return render_template(
        "view_character.html",
        logged_in=logged_in,
        character=db_character.character,
        can_edit=can_edit,
        character_id=character_id,
        character_img=db_character.image,
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
