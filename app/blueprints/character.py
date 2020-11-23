from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    abort,
    make_response,
    jsonify,
)
import flask_login
from wtforms import BooleanField, SelectField, IntegerField
from wtforms.validators import NumberRange
from werkzeug.datastructures import MultiDict
import logging

from tabletop_story.models import User, GameCharacter, GameCampaign
from tabletop_story.forms import (
    EditCharacterForm,
    DeleteCharacterForm,
    EditCharacterRemoveInventoryForm,
    EditCharacterAddInventoryForm,
)
from tabletop_story.routes import ability_modifier
from tabletop_story.plugins import db
from .charimg import charimg
from dnd_character import Character
from dnd_character.classes import CLASSES
from dnd_character.spellcasting import spells_for_class_level, SRD_spells
from dnd_character.equipment import SRD_equipment


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
    if class_key not in CLASSES:
        abort(400)
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
    )
    db.session.add(db_char)
    db.session.commit()
    edit_character(character_id=db_char.id, selected_field=None, autosubmit=True)
    return redirect(url_for(".edit_character", character_id=db_char.id))


@blueprint.route("/delete/<character_id>", methods=["GET", "POST"])
@flask_login.login_required
def delete_character(character_id):
    try:
        character_id = int(character_id)
    except TypeError:
        abort(400)
    db_character = GameCharacter.query.get(character_id)
    if db_character is None:
        abort(404)
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


@blueprint.route(
    "/edit/<character_id>",
    defaults={"selected_field": "all"},
    methods=["GET", "POST"],
)
@blueprint.route("/edit/<character_id>/<selected_field>", methods=["GET", "POST"])
@flask_login.login_required
def edit_character(character_id, selected_field, autosubmit=False):
    try:
        character_id = int(character_id)
    except TypeError:
        abort(400)
    user_id = int(flask_login.current_user.get_id())
    db_character = GameCharacter.query.get(character_id)
    if db_character is None:
        abort(404)
    elif db_character.user_id != user_id:
        # This user does not own the character. Check if the user is a relevant gamemaster
        for campaign in GameCampaign.query.filter_by(gamemaster=user_id).all():
            if any(
                [
                    campaign.character1 == character_id,
                    campaign.character2 == character_id,
                    campaign.character3 == character_id,
                    campaign.character4 == character_id,
                    campaign.character5 == character_id,
                    campaign.character6 == character_id,
                ]
            ):
                break
            else:
                abort(403)

    def create_edit_character_form(data):
        """
        Subclass the edit form so we can add fields dynamically.
        Returns a tuple: (the subclass, number of cantrips, and list of non-cantrip spell choices)
        """

        class ThisEditCharacterForm(EditCharacterForm):
            pass

        setattr(
            ThisEditCharacterForm,
            "hp",
            IntegerField("HP", validators=[NumberRange(min=0, max=data["max_hp"])]),
        )

        for i, class_feature in enumerate(data["class_features"].values()):
            setattr(
                ThisEditCharacterForm,
                f"class_feature_{i}",
                BooleanField(class_feature["name"]),
            )
        cantrips = 0
        spell_slots = []
        if data["class_spellcasting"]:
            if "cantrips_known" in data["class_spellcasting"]:
                cantrips = data["class_spellcasting"]["cantrips_known"]
                for i in range(cantrips):
                    available_cantrips = list(
                        spells_for_class_level(data["class_index"], 0)
                    )
                    setattr(
                        ThisEditCharacterForm,
                        f"spells_known_lvl0_{i}",
                        SelectField(
                            f"Cantrip #{str(i+1)}",
                            choices=[
                                (spell_name, SRD_spells[spell_name]["name"])
                                for spell_name in available_cantrips
                            ],
                        ),
                    )
            for spell_level in range(1, 10):
                try:
                    num_spells = data["class_spellcasting"][
                        f"spell_slots_level_{spell_level}"
                    ]
                except KeyError:
                    # Half-spellcasters have less spell slot levels, so ignore this for now
                    break
                for spell_num in range(num_spells):
                    label = f"spells_known_lvl{spell_level}_{spell_num}"
                    spell_slots.append(label)
                    setattr(
                        ThisEditCharacterForm,
                        label,
                        SelectField(
                            f"Level {spell_level} Spell Slot #{str(spell_num+1)}",
                            choices=[
                                (spell_name, SRD_spells[spell_name]["name"])
                                for spell_name in spells_for_class_level(
                                    data["class_index"], spell_level
                                )
                            ],
                        ),
                    )
        return ThisEditCharacterForm, cantrips, spell_slots

    def extract_and_apply_edit_character_form(form, data, autosubmit=False):
        """
        Receives the dictionary for the previous character.
        Extracts data from the edit_character form and applies it to this dict.
        Returns a tuple: (valid dict for making a new Character, visual_design dict)
        """
        if autosubmit or form.validate_on_submit():
            # Most fields match up with attributes of Character
            for field in form._fields:
                data[field] = form._fields[field].data
            del data["csrf_token"]
            del data["submit"]

            # But we must reassign class_features to different names
            data["class_features_enabled"] = [
                not data.pop(f"class_feature_{i}")
                for i in range(len(data["class_features"]))
            ]
            # Then remove the design bits and put them in their own dict
            design = {}
            removals = []
            for field in data:
                if field.startswith("visual_"):
                    removals.append(field)
                    design[field[7:]] = data[field]
            # Then remove skill fields and put them into the skills dict
            new_data = {}
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
            # Remove the spells_known fields and put them into the dict
            data["spells_known"] = {}
            for i in range(cantrips):
                cantrip = f"spells_known_lvl0_{i}"
                chosen_spell = data.pop(cantrip)
                if i == 0:
                    data["spells_known"] = {0: [chosen_spell]}
                else:
                    data["spells_known"][0].append(chosen_spell)
            for spell_slot in spell_slots:
                chosen_spell = data.pop(spell_slot)
                spell_level = int(spell_slot[16:].split("_")[0])
                if spell_level in data["spells_known"]:
                    data["spells_known"][spell_level].append(chosen_spell)
                else:
                    data["spells_known"][spell_level] = [chosen_spell]
            return data, design

    def create_filled_form_dict(character, design, cantrips, spell_slots):
        """
        Receives Character object, visual_design dict, number of cantrips, list of non-cantrips
        Returns a dict of the filled edit_character form
        """
        filled_form = {
            "visual_body": design["body"],
            "visual_head": design["head"],
            "visual_face": design["face"],
            "visual_hair": design["hair"],
            "visual_hat": design["hat"],
            "name": character.name,
            "age": character.age,
            "gender": character.gender,
            "description": character.description,
            "biography": character.biography,
            "class_name": character.class_name,
            "alignment": character.alignment,
            "hp": character.hp,
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
        for spell_slot in spell_slots:
            spell_level, spell_num = spell_slot[16:].split("_")
            try:
                chosen_spell = character.spells_known[int(spell_level)][int(spell_num)]
            except (KeyError, TypeError, IndexError):
                # default value for blank spell slots
                chosen_spell = list(
                    spells_for_class_level(character.class_index, int(spell_level))
                )[int(spell_num)]

            filled_form[spell_slot] = (chosen_spell, SRD_spells[chosen_spell]["name"])
        if cantrips:
            available_cantrips = list(spells_for_class_level(data["class_index"], 0))
            filled_form.update(
                {
                    f"spells_known_lvl0_{i}": (
                        available_cantrips[i],
                        SRD_spells[available_cantrips[i]]["name"],
                    )
                    if character.spells_known is None
                    or i >= len(character.spells_known[0])
                    else (
                        character.spells_known[0][i],
                        SRD_spells[character.spells_known[0][i]]["name"],
                    )
                    for i in range(cantrips)
                }
            )
        return filled_form

    data = db_character.as_dict()
    ThisEditCharacterForm, cantrips, spell_slots = create_edit_character_form(data)

    if autosubmit:
        filled_form = create_filled_form_dict(
            db_character.character,
            db_character.design,
            cantrips,
            spell_slots,
        )
        form = ThisEditCharacterForm(formdata=MultiDict(filled_form))
    elif request.method == "POST":
        form = ThisEditCharacterForm()
    if autosubmit or (request.method == "POST" and form.validate_on_submit()):
        # Now we have a valid dict to make a new Character
        data, design = extract_and_apply_edit_character_form(
            form, data, autosubmit=True
        )
        db_character.name = form.name.data
        db_character.update_data(data)
        db_character.visual_design = str(design)
        db.session.add(db_character)
        db.session.commit()
        if not autosubmit:
            return redirect(url_for(".view_character", character_id=character_id))

    character = db_character.character
    design = db_character.design

    if not autosubmit and request.method == "GET":
        filled_form = create_filled_form_dict(character, design, cantrips, spell_slots)
        form = ThisEditCharacterForm(formdata=MultiDict(filled_form))

    return render_template(
        "edit_character.html",
        logged_in=True,
        character=character,
        form=form,
        selected_field=selected_field,
        character_id=character_id,
        character_img=charimg(*list(design.values())),
        class_features=[
            form._fields[f"class_feature_{i}"]
            for i in range(len(character.class_features))
        ],
        cantrips=[]
        if cantrips == 0
        else [form._fields[f"spells_known_lvl0_{i}"] for i in range(cantrips)],
        spell_slots=[]
        if not character.class_spellcasting
        else [form._fields[spell_slot] for spell_slot in spell_slots],
    )


@blueprint.route("/img", methods=["POST"])
def get_charimg():
    data = request.get_json()
    response = make_response(jsonify(charimg(*data)), 200)
    return response


@blueprint.route("/view/<character_id>")
def view_character(character_id):
    db_character = GameCharacter.query.get(character_id)
    if db_character is None:
        abort(404)
    can_edit = False
    logged_in = flask_login.current_user.is_authenticated
    if logged_in and db_character.user_id == int(flask_login.current_user.get_id()):
        can_edit = True

    character = db_character.character
    spellcasting_stat = {
        "cha": character.charisma,
        "int": character.intelligence,
        "wis": character.wisdom,
        None: 0,
    }
    return render_template(
        "view_character.html",
        logged_in=logged_in,
        url_root=request.url_root[:-1],
        page_description=character.description,
        character=character,
        can_edit=can_edit,
        character_id=character_id,
        character_img=charimg(*list(db_character.design.values())),
        spells=SRD_spells,
        spell_levels=0
        if character.spells_known is None
        else len(character.spells_known)
        if 0 not in character.spells_known
        else len(character.spells_known) - 1,
        passive_perception=10
        + character.skills_wisdom["perception"]
        + int(ability_modifier(character.wisdom)),
        spell_save_dc=8
        + ability_modifier(spellcasting_stat[character.spellcasting_stat])
        + character.prof_bonus,
        skills={
            "athletics": (
                character.prof_bonus if character.skills_strength["athletics"] else 0
            )
            + ability_modifier(character.strength),
            "acrobatics": (
                character.prof_bonus if character.skills_dexterity["acrobatics"] else 0
            )
            + ability_modifier(character.dexterity),
            "sleight-of-hand": (
                character.prof_bonus
                if character.skills_dexterity["sleight-of-hand"]
                else 0
            )
            + ability_modifier(character.dexterity),
            "stealth": (
                character.prof_bonus if character.skills_dexterity["stealth"] else 0
            )
            + ability_modifier(character.dexterity),
            "arcana": (
                character.prof_bonus if character.skills_intelligence["arcana"] else 0
            )
            + ability_modifier(character.intelligence),
            "history": (
                character.prof_bonus if character.skills_intelligence["history"] else 0
            )
            + ability_modifier(character.intelligence),
            "investigation": (
                character.prof_bonus
                if character.skills_intelligence["investigation"]
                else 0
            )
            + ability_modifier(character.intelligence),
            "nature": (
                character.prof_bonus if character.skills_intelligence["nature"] else 0
            )
            + ability_modifier(character.intelligence),
            "religion": (
                character.prof_bonus if character.skills_intelligence["religion"] else 0
            )
            + ability_modifier(character.intelligence),
            "animal-handling": (
                character.prof_bonus
                if character.skills_wisdom["animal-handling"]
                else 0
            )
            + ability_modifier(character.wisdom),
            "insight": (
                character.prof_bonus if character.skills_wisdom["insight"] else 0
            )
            + ability_modifier(character.wisdom),
            "medicine": (
                character.prof_bonus if character.skills_wisdom["medicine"] else 0
            )
            + ability_modifier(character.wisdom),
            "perception": (
                character.prof_bonus if character.skills_wisdom["perception"] else 0
            )
            + ability_modifier(character.wisdom),
            "survival": (
                character.prof_bonus if character.skills_wisdom["survival"] else 0
            )
            + ability_modifier(character.wisdom),
            "deception": (
                character.prof_bonus if character.skills_charisma["deception"] else 0
            )
            + ability_modifier(character.charisma),
            "intimidation": (
                character.prof_bonus if character.skills_charisma["intimidation"] else 0
            )
            + ability_modifier(character.charisma),
            "performance": (
                character.prof_bonus if character.skills_charisma["performance"] else 0
            )
            + ability_modifier(character.charisma),
            "persuasion": (
                character.prof_bonus if character.skills_charisma["persuasion"] else 0
            )
            + ability_modifier(character.charisma),
        },
    )


@blueprint.route("/edit/<character_id>/inventory", methods=["GET", "POST"])
@flask_login.login_required
def edit_character_inventory(character_id):
    db_character = GameCharacter.query.get(character_id)
    if db_character is None:
        abort(404)
    if db_character.user_id != int(flask_login.current_user.get_id()):
        abort(403)
    character = db_character.character

    # Subclass the remove-item form so we can add the select field
    class ThisRemoveItemForm(EditCharacterRemoveInventoryForm):
        pass

    setattr(
        ThisRemoveItemForm,
        "remove_item",
        SelectField(
            "Remove Item:",
            choices=[(i, item["name"]) for i, item in enumerate(character.inventory)],
        ),
    )

    remove_form = ThisRemoveItemForm()
    add_form = EditCharacterAddInventoryForm()

    if request.method == "POST":
        processed = False

        if remove_form.submit_remove.data and remove_form.validate_on_submit():
            character.removeItem(character.inventory[int(remove_form.remove_item.data)])
            processed = True

        if add_form.submit_add.data and add_form.validate_on_submit():
            character.giveItem(SRD_equipment[add_form.new_item.data])
            processed = True

        if processed:
            db_character.update_data(dict(character))
            db.session.add(db_character)
            db.session.commit()
            return redirect(url_for(".view_character", character_id=character_id))

    # If the player has options relating to equipment, alert them now!
    # TODO Allow this message to be cleared away
    if character.player_options["starting_equipment"]:
        lines = [
            f"<li>{line}</li>"
            for line in character.player_options["starting_equipment"]
        ]
        message = (
            f"Your class recommends this starting equipment: <ul>{''.join(lines)}</ul>"
        )
    else:
        message = ""

    return render_template(
        "edit_character_inventory.html",
        logged_in=True,
        add_form=add_form,
        remove_form=remove_form,
        character=character,
        message=message,
    )


@blueprint.route("/edit/<character_id>/exp/<number>")
@flask_login.login_required
def edit_character_experience(character_id, number):
    db_character = GameCharacter.query.get(character_id)
    if db_character is None:
        abort(404)
    if db_character.user_id != int(flask_login.current_user.get_id()):
        abort(403)
    try:
        number = int(number)
    except ValueError:
        abort(400)
    char = db_character.character
    difference = char.max_hp - char.hp
    char.experience += number
    char.hp = char.max_hp - difference
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
    # autosubmitting edit_character would be nice but it ruins flash() and isn't strictly needed
    # edit_character(character_id=character_id, selected_field=None, autosubmit=True)
    return redirect(url_for(".view_character", character_id=character_id))
