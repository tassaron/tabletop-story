from functools import wraps
from flask import Blueprint, current_app, render_template, flash, abort
from flask_login import current_user


blueprint = Blueprint("inventory", __name__, template_folder="../templates/inventory")


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not current_user.is_admin_authenticated:
            abort(403)
        return func(*args, **kwargs)

    return decorated_view


@blueprint.route("/add")
@admin_required
def add_inventory_item():
    def allowed_file(filename):
        return os.path.splitext(filename) in current_app.config["ALLOWED_EXTENSIONS"]

    return ""


@blueprint.route("/remove")
@admin_required
def remove_inventory_item():
    pass
