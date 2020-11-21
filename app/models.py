from .plugins import plugins
from itsdangerous import TimedJSONWebSignatureSerializer
import os
from dnd_character import Character
from .dnd_campaign import Combat, NPC
from ast import literal_eval

# plugins = create_plugins()
db, migrate, bcrypt, login_manager = plugins


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False)

    def __init__(self, **kwargs):
        if kwargs["password"] is not None:
            kwargs["password"] = bcrypt.generate_password_hash(
                kwargs["password"]
            ).decode("utf-8")
        super().__init__(**kwargs)

    def __repr__(self):
        return str(self.email)

    def create_password_reset_token(self):
        serializer = TimedJSONWebSignatureSerializer(os.environ("SECRET_KEY"), 1800)
        return serializer.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_password_reset_token(token):
        serializer = TimedJSONWebSignatureSerializer(os.environ("SECRET_KEY"))
        try:
            user_id = serializer.loads(token)["user_id"]
        except KeyError:
            return None
        return User.query.get(user_id)

    def check_password_hash(self, alleged_password):
        return bcrypt.check_password_hash(self.password, alleged_password)

    @property
    def is_anonymous(self):
        return False if self.password else True

    @property
    def is_authenticated(self):
        return False if self.is_anonymous else True

    @property
    def is_active(self):
        return False if self.is_anonymous else True

    @property
    def is_admin_authenticated(self):
        return self.password and self.is_admin

    def get_id(self):
        return str(self.id)


class SceneNPC(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    scene_id = db.Column(db.Integer, db.ForeignKey("location_scene.id"), nullable=False)
    name = db.Column(db.String(127), nullable=False)
    # string literal for a dict
    data = db.Column(db.String(2048), nullable=False)

    def as_dict(self):
        return literal_eval(self.data)

    @property
    def npc(self):
        return NPC(**self.as_dict())


class LocationScene(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    location_id = db.Column(
        db.Integer, db.ForeignKey("campaign_location.id"), nullable=False
    )
    name = db.Column(db.String(127), nullable=False)
    description = db.Column(db.String(2048), nullable=True)

    @property
    def npcs(self):
        return SceneNPC.query.filter_by(scene_id=self.id).all()


class CampaignLocation(db.Model):
    """
    A location within a GameCampaign which has a name, description, and scenes
    """

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("game_campaign.id"), nullable=False
    )
    name = db.Column(db.String(127), nullable=False)
    description = db.Column(db.String(2048), nullable=True)


class GameCampaign(db.Model):
    """
    A campaign of D&D with 1 gamemaster (User) and 2-6 GameCharacters
    """

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(127), nullable=False)
    gamemaster = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    active_location = db.Column(
        db.Integer, db.ForeignKey("campaign_location.id"), nullable=False
    )
    # the gamemaster is a user, but the players are characters
    character1 = db.Column(
        db.Integer, db.ForeignKey("game_character.id"), nullable=True
    )
    character2 = db.Column(
        db.Integer, db.ForeignKey("game_character.id"), nullable=True
    )
    character3 = db.Column(
        db.Integer, db.ForeignKey("game_character.id"), nullable=True
    )
    character4 = db.Column(
        db.Integer, db.ForeignKey("game_character.id"), nullable=True
    )
    character5 = db.Column(
        db.Integer, db.ForeignKey("game_character.id"), nullable=True
    )
    character6 = db.Column(
        db.Integer, db.ForeignKey("game_character.id"), nullable=True
    )
    # string literal for a dict which creates a Combat object
    combat_data = db.Column(db.String(1024), nullable=False)

    def __init__(self, **kwargs):
        if "combat_data" not in kwargs:
            kwargs["combat_data"] = str(Combat())
        super().__init__(**kwargs)

    def get_combat(self):
        return Combat(**literal_eval(self.combat_data))

    def set_combat(self, scene_id, characters):
        scene = LocationScene.query.get(scene_id)
        characters = [GameCharacter.query.get(char_id) for char_id in characters]
        self.combat_data = str(
            Combat(
                scene_id=scene_id,
                characters=[
                    (character.id, character.character.dexterity)
                    for character in characters
                ],
                npcs=[(npc.id, npc.npc.dexterity) for npc in scene.npcs],
            )
        )

    def characters(self):
        return [
            self.character1,
            self.character2,
            self.character3,
            self.character4,
            self.character5,
            self.character6,
        ]


class GameCharacter(db.Model):
    """
    A D&D character owned by a user
    """

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(127), nullable=False)
    data_keys = db.Column(db.String(1024), nullable=False)
    data_vals = db.Column(db.String(4096), nullable=False)
    visual_design = db.Column(db.String(512), nullable=False)

    def __init__(self, **kwargs):
        if "visual_design" not in kwargs:
            kwargs["visual_design"] = str(
                {
                    "body": "0",
                    "head": "headoval",
                    "face": "faceneutral",
                    "hair": "None",
                    "hat": "None",
                }
            )
        super().__init__(**kwargs)

    @property
    def design(self):
        """Returns dict of visual design configuration for this character"""
        return literal_eval(self.visual_design)

    def keys(self):
        return self.data_keys[2:-2].split("', '")

    def values(self):
        return literal_eval(self.data_vals)

    def as_dict(self):
        return dict(zip(self.keys(), self.values()))

    def update_data(self, data):
        # remove armour class so it will be recalculated properly
        del data["armour_class"]
        new = Character(**data)
        self.data_keys = str(new.keys())
        self.data_vals = str(new.values())

    @property
    def character(self):
        """
        Return a real Character object using the data in this database row
        """
        i = 0
        return Character(**self.as_dict())
