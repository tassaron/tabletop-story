from . import inventory, storefront, account, character


def register_blueprints(app):
    app.register_blueprint(storefront.blueprint)
    for blueprint in (account.blueprint, inventory.blueprint, character.blueprint):
        app.register_blueprint(blueprint, url_prefix=f"/{blueprint.name}")
