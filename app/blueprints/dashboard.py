from flask import *
import flask_login
from tabletop_story.plugins import bcrypt, db
from tabletop_story.models import GameCharacter


blueprint = Blueprint(
    "dashboard",
    __name__,
    static_folder="../static",
    template_folder="../templates/dashboard",
)


@blueprint.app_template_filter("currency")
def float_to_str_currency(num):
    maj, min = str(num).split(".")
    return str(num) if len(min) == 2 else ".".join((maj, f"{min}0"))


@blueprint.app_template_filter("alignment")
def full_alignment_title(two_letters):
    alignment = {
        "LG": "Lawful Good",
        "NG": "Neutral Good",
        "CG": "Chaotic Good",
        "LN": "Lawful Neutral",
        "TN": "True Neutral",
        "CN": "Chaotic Neutral",
        "LE": "Lawful Evil",
        "NE": "Neutral Evil",
        "CE": "Chaotic Evil",
    }
    return alignment[two_letters]


@blueprint.route("/")
def index():
    characters = []
    is_logged_in = flask_login.current_user.is_authenticated
    if is_logged_in:
        user_id = int(flask_login.current_user.get_id())
        db_characters = (
            []
            if not is_logged_in
            else GameCharacter.query.filter_by(user_id=user_id).all()
        )
        characters = [row.character for row in db_characters]
        for i, character in enumerate(characters):
            img = db_characters[i].image
            character.image = img if img is not None else "potato.jpg"
            character.dbid = db_characters[i].id

    return render_template(
        "dashboard.html",
        logged_in=is_logged_in,
        characters=characters,
    )
