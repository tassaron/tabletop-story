from flask import Blueprint, render_template, abort
from flask_login import current_user
from dnd_character.spellcasting import SRD_spells


blueprint = Blueprint("spells", __name__, template_folder="../templates/spells")


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
