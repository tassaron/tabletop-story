from flask import Blueprint, render_template, abort, jsonify
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


@blueprint.route("/get/<monster>/<attr>")
def get_monster(monster, attr):
    if attr == "card":
        monster_json = SRD_monsters[monster]
        monster_json["html"] = render_template(
            "view_monster.html",
            monster=SRD_monsters[monster],
            embedded_card=True,
        )
        return monster_json
    elif attr not in monster:
        abort(400)
    return jsonify(SRD_monsters[monster][attr])
