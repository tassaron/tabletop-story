from .plugins import plugins
from itsdangerous import TimedJSONWebSignatureSerializer
import os
from dnd_character import Character

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


class GameCampaign(db.Model):
    """
    A campaign of D&D with 1 gamemaster and 2-6 players
    """

    gamemaster = db.Column(
        db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False
    )
    # the gamemaster is a user, but the players are characters
    character1 = db.Column(db.String(255), nullable=False)
    character2 = db.Column(db.String(255), nullable=False)
    character3 = db.Column(db.String(255), nullable=False)
    character4 = db.Column(db.String(255), nullable=False)
    character5 = db.Column(db.String(255), nullable=False)
    character6 = db.Column(db.String(255), nullable=False)


class GameCharacter(db.Model):
    """
    A D&D character owned by a user
    """

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(127), nullable=False)
    image = db.Column(db.String(127), nullable=True)
    data_keys = db.Column(db.String(1024), nullable=False)
    data_vals = db.Column(db.String(1024), nullable=False)

    @property
    def character(self):
        keys = self.data_keys[2:][:-2].split("', '")
        vals = self.data_vals[2:][:-2].split("', '")
        return Character(**dict(zip(keys, vals)))
