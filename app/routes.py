import math
import flask_login
from flask import Blueprint, render_template, flash, redirect, url_for
from dnd_character.SRD import SRD_rules
from mistune import create_markdown


main_routes = Blueprint("main", __name__)


@main_routes.app_template_filter("markdown")
def md_to_html(string):
    return create_markdown(
        escape=False, renderer="html", plugins=["strikethrough", "table"]
    )(string)


@main_routes.app_template_filter("index_to_name")
def index_to_name(string):
    return string.replace("_", " ").title()


@main_routes.app_template_filter("url_safe")
def url_safe(string):
    # FIXME
    return (
        string.replace(" ", "-")
        .lower()
        .replace("?", "")
        .replace(":", "")
        .replace("(", "")
        .replace(")", "")
        .replace("'", "")
    )


@main_routes.app_template_filter("ability_modifier")
def ability_modifier(number):
    """
    Jinja filter to turn a Character's ability score into an ability modifier
    """
    return math.floor((number - 10) / 2)


@main_routes.route("/about")
def about_page():
    return render_template(
        "about.html", logged_in=flask_login.current_user.is_authenticated
    )


@main_routes.route("/rules")
def rules_page():
    return render_template(
        "rules.html",
        logged_in=flask_login.current_user.is_authenticated,
        SRD_disclaimer=True,
        rules=SRD_rules,
    )


@main_routes.route("/license/ogl")
def license_ogl():
    return render_template(
        "license/ogl.html",
        logged_in=flask_login.current_user.is_authenticated,
    )


@main_routes.route("/license/mit")
def license_mit():
    return render_template(
        "license/mit.html",
        logged_in=flask_login.current_user.is_authenticated,
    )
