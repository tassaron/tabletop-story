from flask import Blueprint, render_template, abort
from flask_login import current_user
from dnd_character.spellcasting import SRD_spells, spells_for_class_level


blueprint = Blueprint("spells", __name__, template_folder="../templates/spells")


@blueprint.route("")
def list_spells_index():
    return render_template(
        "list_spells_index.html",
        logged_in=current_user.is_authenticated,
    )


@blueprint.route("/list/<classs>")
def list_spells(classs):
    """
    A view that lists spells for a class
    """
    if classs not in (
        "bard",
        "cleric",
        "druid",
        "paladin",
        "ranger",
        "sorcerer",
        "warlock",
        "wizard",
    ):
        abort(404)
    spell_levels = [spells_for_class_level(classs, i) for i in range(10)]
    spells = []
    for i, spell_levels_ in enumerate(spell_levels):
        spells.append([SRD_spells[spell] for spell in spell_levels_])
    return render_template(
        "list_spells.html",
        logged_in=current_user.is_authenticated,
        SRD_disclaimer=True,
        spells=spells,
        class_name=classs.title(),
    )


@blueprint.route("/view/<spell>")
def view_spell(spell):
    if spell not in SRD_spells:
        abort(404)
    return render_template(
        "view_spell.html",
        logged_in=current_user.is_authenticated,
        SRD_disclaimer=True,
        spell=SRD_spells[spell],
    )


@blueprint.route("/get/<spell>")
def get_spell(spell):
    if spell not in SRD_spells:
        abort(400)
    spell_json = SRD_spells[spell]
    spell_json["html"] = render_template(
        "view_spell.html",
        spell=spell_json,
        embedded_card=True,
    )
    return spell_json
