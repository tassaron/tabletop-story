from flask import *
import flask_login
from werkzeug.utils import secure_filename
from tabletop_story.plugins import bcrypt, db


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
    return render_template(
        "dashboard.html",
        logged_in=flask_login.current_user.is_authenticated,
        characters=[],
    )
