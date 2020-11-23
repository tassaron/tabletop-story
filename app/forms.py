from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    PasswordField,
    SubmitField,
    BooleanField,
    SelectField,
    IntegerField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    NumberRange,
    Optional,
)
from dnd_character.equipment import SRD_equipment


class EditNPCForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=1, max=127)])
    description = StringField("Description", validators=[Length(min=0, max=255)])
    hit_points = IntegerField("Hit points", validators=[NumberRange(min=0)])
    max_hit_points = IntegerField("Hit point maximum", validators=[NumberRange(min=1)])
    armour_class = IntegerField("Armour class", validators=[NumberRange(min=0)])
    passive_perception = IntegerField(
        "Passive perception", validators=[NumberRange(min=0)]
    )
    constitution = IntegerField("CON", validators=[NumberRange(min=0)])
    strength = IntegerField("STR", validators=[NumberRange(min=0)])
    dexterity = IntegerField("DEX", validators=[NumberRange(min=0)])
    wisdom = IntegerField("WIS", validators=[NumberRange(min=0)])
    intelligence = IntegerField("INT", validators=[NumberRange(min=0)])
    charisma = IntegerField("CHA", validators=[NumberRange(min=0)])
    experience = IntegerField("Recommended XP value", validators=[NumberRange(min=0)])
    actions = TextAreaField("Actions")
    abilities = TextAreaField("Special Abilities")
    proficiencies = TextAreaField("Proficiencies")
    submit = SubmitField("💾 Save Changes")


class EditCampaignForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=1, max=127)])
    character1 = IntegerField(
        "First Character ID", validators=[NumberRange(min=1), Optional()]
    )
    char1uid = StringField("Secret")
    character2 = IntegerField(
        "Second Character ID", validators=[NumberRange(min=1), Optional()]
    )
    char2uid = StringField("Secret")
    character3 = IntegerField(
        "Third Character ID", validators=[NumberRange(min=1), Optional()]
    )
    char3uid = StringField("Secret")
    character4 = IntegerField(
        "Fourth Character ID", validators=[NumberRange(min=1), Optional()]
    )
    char4uid = StringField("Secret")
    character5 = IntegerField(
        "Fifth Character ID", validators=[NumberRange(min=1), Optional()]
    )
    char5uid = StringField("Secret")
    character6 = IntegerField(
        "Sixth Character ID", validators=[NumberRange(min=1), Optional()]
    )
    char6uid = StringField("Secret")
    submit = SubmitField("💾 Save Changes")


class GenericForm(FlaskForm):
    submit = SubmitField("OK")


class GenericEditForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=1, max=127)])
    description = TextAreaField("Notes")
    submit = SubmitField("💾 Save Changes")


class GenericCreateForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=1, max=127)])
    submit = SubmitField("Create 📖")


class DeleteCharacterForm(FlaskForm):
    """
    Ask the user if they're really really sure they want to delete a character
    """

    # Ideally there should be a WTForms validator to check if the name matches
    name = StringField(
        "Type your character's name exactly to confirm deletion: ",
    )
    submit = SubmitField("🗑️ Delete")


class EditCharacterRemoveInventoryForm(FlaskForm):
    submit_remove = SubmitField("Remove Item ➖")


class EditCharacterAddInventoryForm(FlaskForm):
    # custom_item = StringField("Item Name:", validator=[Length(min=1, max=24)])
    new_item = SelectField(
        "Add New Item: ",
        choices=[(item["index"], item["name"]) for item in SRD_equipment.values()],
    )
    submit_add = SubmitField("Add Item ➕")


class EditCharacterForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=1, max=127)])
    age = StringField("Age")
    gender = StringField("Gender", validators=[Length(max=127)])
    alignment = SelectField(
        "Alignment",
        choices=[
            ("LG", "Lawful Good"),
            ("NG", "Neutral Good"),
            ("CG", "Chaotic Good"),
            ("LN", "Lawful Neutral"),
            ("TN", "True Neutral"),
            ("CN", "Chaotic Neutral"),
            ("LE", "Lawful Evil"),
            ("NE", "Neutral Evil"),
            ("CE", "Chaotic Evil"),
        ],
        validate_choice=False,
    )
    description = StringField("Physical Description", validators=[Length(max=127)])
    biography = TextAreaField("Backstory", validators=[Length(max=2048)])
    class_name = StringField("Class Name", validators=[Length(max=127)])
    # ability scores
    constitution = IntegerField("CON", validators=[NumberRange(min=3, max=20)])
    strength = IntegerField("STR", validators=[NumberRange(min=3, max=20)])
    dexterity = IntegerField("DEX", validators=[NumberRange(min=3, max=20)])
    wisdom = IntegerField("WIS", validators=[NumberRange(min=3, max=20)])
    intelligence = IntegerField("INT", validators=[NumberRange(min=3, max=20)])
    charisma = IntegerField("CHA", validators=[NumberRange(min=3, max=20)])
    # skills
    skills_strength_athletics = BooleanField("Strength: Athletics")
    skills_dexterity_acrobatics = BooleanField("Dexterity: Acrobatics")
    skills_dexterity_raistlin = BooleanField("Dexterity: Sleight of Hand")
    skills_dexterity_stealth = BooleanField("Dexterity: Stealth")
    skills_intelligence_arcana = BooleanField("Intelligence: Arcana")
    skills_intelligence_history = BooleanField("Intelligence: History")
    skills_intelligence_investigation = BooleanField("Intelligence: Investigation")
    skills_intelligence_nature = BooleanField("Intelligence: Nature")
    skills_intelligence_religion = BooleanField("Intelligence: Religion")
    skills_wisdom_hagrid = BooleanField("Wisdom: Animal Handling")
    skills_wisdom_insight = BooleanField("Wisdom: Insight")
    skills_wisdom_medicine = BooleanField("Wisdom: Medicine")
    skills_wisdom_perception = BooleanField("Wisdom: Perception")
    skills_wisdom_survival = BooleanField("Wisdom: Survival")
    skills_charisma_deception = BooleanField("Charisma: Deception")
    skills_charisma_intimidation = BooleanField("Charisma: Intimidation")
    skills_charisma_performance = BooleanField("Charisma: Performance")
    skills_charisma_persuasion = BooleanField("Charisma: Persuasion")
    # character visual design
    visual_body = SelectField(
        "Body Shape: ",
        choices=[
            (0, "Loaf"),
            (1, "Trapezoid 1"),
            (2, "Trapezoid 2"),
            (3, "Hourglass"),
            (4, "Egg"),
            (5, "Rectangle"),
        ],
        validate_choice=False,
    )
    visual_head = SelectField(
        "Head Shape: ",
        choices=[
            ("headoval", "Oval"),
            ("headcircle", "Circle"),
            ("headsquare", "Square"),
        ],
        validate_choice=False,
    )
    visual_face = SelectField(
        "Facial Expression: ",
        choices=[
            ("faceneutral", "Neutral"),
            ("faceclosedsmile", "Smile"),
            ("faceopensmile", "Open Smile"),
            ("faceclosedfrown", "Frown"),
            ("faceopenfrown", "Open Frown"),
            ("faceslightfrown", "Slight Frown"),
            ("facesmirk", "Smirk"),
            ("facecloud", "Eugh"),
            ("faceshocked", "Shocked"),
        ],
        validate_choice=False,
    )
    visual_hair = SelectField(
        "Hair: ",
        choices=[
            (None, "None"),
            ("hairlongmess", "Long Mess"),
            ("hairnancy", "Nancy"),
            ("hairwings", "Wings"),
        ],
        validate_choice=False,
    )
    visual_hat = SelectField(
        "Hat: ",
        choices=[
            (None, "None"),
            ("hatcrown", "Crown"),
            ("hatelf", "Elf Hat"),
            ("hatwinter", "Winter Hat"),
            ("hatwizard", "Wizard Hat"),
            ("hatmuffintop", "Muffintop"),
        ],
        validate_choice=False,
    )
    submit = SubmitField("💾 Save Changes")


class LoginForm(FlaskForm):
    email = StringField(
        "email", validators=[DataRequired(), Email(), Length(min=5, max=32)]
    )
    password = PasswordField(
        "password", validators=[Length(min=8, max=64), DataRequired()]
    )
    rememberme = BooleanField("remember me")
    submit = SubmitField("Log In")


class ShortRegistrationForm(FlaskForm):
    """A user registration form with just the email and password fields"""

    email = StringField("email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "password", validators=[Length(min=8, max=64), DataRequired()]
    )
    confirmp = PasswordField(
        "confirm password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")


class RequestPasswordResetForm(FlaskForm):
    """User requests that their password be reset"""

    email = StringField("email", validators=[DataRequired(), Email()])
    submit = SubmitField("Reset Your Password")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email.")


class PasswordResetForm(FlaskForm):
    """User submits a new password after verifying email"""

    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=64)]
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")
