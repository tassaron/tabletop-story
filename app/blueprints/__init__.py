from . import (
    inventory,
    dashboard,
    account,
    character,
    campaign,
    campaign_location,
    location_scene,
    scene_npc,
    spells,
    monsters,
)


def register_blueprints(app):
    app.register_blueprint(dashboard.blueprint)
    for blueprint in (
        account.blueprint,
        inventory.blueprint,
        character.blueprint,
        campaign.blueprint,
        campaign_location.blueprint,
        location_scene.blueprint,
        scene_npc.blueprint,
        spells.blueprint,
        monsters.blueprint,
    ):
        app.register_blueprint(blueprint, url_prefix=f"/{blueprint.name}")
