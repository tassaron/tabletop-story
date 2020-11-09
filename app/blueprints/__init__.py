from . import inventory, dashboard, account, character, spells


def register_blueprints(app):
    app.register_blueprint(dashboard.blueprint)
    for blueprint in (
        account.blueprint,
        inventory.blueprint,
        character.blueprint,
        spells.blueprint,
    ):
        app.register_blueprint(blueprint, url_prefix=f"/{blueprint.name}")
