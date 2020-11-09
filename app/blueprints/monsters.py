from flask import Blueprint, render_template, abort
from flask_login import current_user
from dnd_character.monsters import SRD_monsters


blueprint = Blueprint("monsters", __name__, template_folder="../templates/monsters")


@blueprint.route("/view/<monster>")
def view_monster(monster):
    if monster not in SRD_monsters:
        abort(404)
    return render_template(
        "view_monster.html",
        logged_in=current_user.is_authenticated,
        SRD_disclaimer=True,
        monster=SRD_monsters[monster],
    )
