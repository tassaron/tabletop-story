import flask_login
from flask import Blueprint, render_template, flash, redirect, url_for
from werkzeug.exceptions import NotFound, Forbidden, InternalServerError, BadRequest
from dnd_character.SRD import SRD_rules
from mistune import create_markdown


main_routes = Blueprint("main", __name__)


@main_routes.app_template_filter("markdown")
def md_to_html(string):
    return create_markdown(
        escape=False, renderer="html", plugins=["strikethrough", "table"]
    )(string)


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
        rules=SRD_rules,
    )


@main_routes.app_errorhandler(NotFound)
def page_not_found(error):
    flash("Sorry, that page doesn't exist", "danger")
    return (
        render_template(
            "index.html", logged_in=flask_login.current_user.is_authenticated, err=True
        ),
        404,
    )


@main_routes.app_errorhandler(Forbidden)
def page_forbidden(error):
    flash("Unauthorized", "danger")
    return (
        render_template(
            "index.html", logged_in=flask_login.current_user.is_authenticated, err=True
        ),
        403,
    )


@main_routes.app_errorhandler(InternalServerError)
def critical_error(error):
    flash("The server experienced an error", "danger")
    return (
        render_template(
            "index.html", logged_in=flask_login.current_user.is_authenticated, err=True
        ),
        500,
    )


@main_routes.app_errorhandler(BadRequest)
def critical_error(error):
    flash("Your request was invalid", "danger")
    return (
        render_template(
            "index.html", logged_in=flask_login.current_user.is_authenticated, err=True
        ),
        500,
    )
