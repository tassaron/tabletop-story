import flask_login
from flask import Blueprint, render_template, flash, request, make_response
from werkzeug.exceptions import NotFound, Forbidden, InternalServerError, BadRequest
from time import sleep
import os


error_routes = Blueprint("errors", __name__)


@error_routes.app_errorhandler(NotFound)
def page_not_found(error):
    flash("Sorry, that page doesn't exist", "danger")
    return (
        render_template(
            "index.html", logged_in=flask_login.current_user.is_authenticated, err=True
        ),
        404,
    )


@error_routes.app_errorhandler(Forbidden)
def page_forbidden(error):
    flash("Unauthorized", "danger")
    return (
        render_template(
            "index.html", logged_in=flask_login.current_user.is_authenticated, err=True
        ),
        403,
    )


@error_routes.app_errorhandler(InternalServerError)
def critical_error(error):
    flash("The server experienced an error", "danger")
    return (
        render_template(
            "index.html", logged_in=flask_login.current_user.is_authenticated, err=True
        ),
        500,
    )


@error_routes.app_errorhandler(BadRequest)
def critical_error(error):
    flash("Your request was invalid", "danger")
    return (
        render_template(
            "index.html", logged_in=flask_login.current_user.is_authenticated, err=True
        ),
        500,
    )


@error_routes.before_app_request
def check_for_malicious_bots():
    if not os.environ.get("TARPIT"):
        # set tarpit in .env to enable screwing with malicious bots
        return
    if request.url_rule == None and flask_login.current_user.get_id() == "None":
        if any(
            [
                bit in request.url.lower()
                for bit in (
                    "wp-",
                    "eval",
                    "actuator",
                    ".env",
                    "php",
                    ".txt",
                    "api/",
                    ";",
                    "console",
                )
            ]
        ):
            # try to slow down script kiddies with invalid json (probably a bad idea but let's see what happens)
            headers = {
                "Content-Type": "application/json",
            }
            resp = make_response(b"allyourbasearebelongtous", 200, headers)
            return resp
