from flask import Blueprint, render_template, abort
from dnd_character.spellcasting import SRD_spells


blueprint = Blueprint("spells", __name__, template_folder="../templates/spells")


@blueprint.route("/view/<spell>")
def view_spell(spell):
    if spell not in SRD_spells:
        abort(404)
    return render_template("view_spell.html", spell=SRD_spells[spell])
