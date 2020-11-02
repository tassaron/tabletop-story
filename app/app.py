"""
Simply initializes the app and registers all blueprints
"""
from .blueprints import register_blueprints
from .plugins import plugins


def init_app(app):
    db, migrate, bcrypt, login_manager = plugins
    for plugin in (db, bcrypt, login_manager):
        plugin.init_app(app)
    migrate.init_app(app, db)
    register_blueprints(app)

    """
    import flask_monitoringdashboard as monitor
    import os

    monitor.config.init_from(file="monitor.cfg")
    try:
        monitor.config.username = os.environ["MONITOR_USERNAME"]
        monitor.config.password = os.environ["MONITOR_PASSWORD"]
    except KeyError:
        raise KeyError("MONITOR_USERNAME and MONITOR_PASSWORD must be added to .env")
    monitor.config.security_token = os.urandom(24)
    monitor.bind(app)
    """

    from .models import User

    @login_manager.user_loader
    def get_user(user_id):
        return User.query.get(int(user_id))

    login_manager.anonymous_user = lambda: User(
        email=None, password=None, is_admin=False
    )
    return app
