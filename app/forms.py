from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    SelectField,
    IntegerField,
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange


class CharacterForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=1, max=127)])
    age = StringField("Age")
    gender = StringField("Gender", validators=[Length(max=127)])
    alignment = SelectField(
        "Alignment",
        choices=[
            ("LG", "LG"),
            ("NG", "NG"),
            ("CG", "CG"),
            ("LN", "LN"),
            ("TN", "TN"),
            ("CN", "CN"),
            ("LE", "LE"),
            ("NE", "NE"),
            ("CE", "CE"),
        ],
        validate_choice=False,
    )
    description = StringField("Physical Description", validators=[Length(max=127)])
    biography = StringField("Backstory", validators=[Length(max=2048)])
    class_name = StringField("Class Name", validators=[Length(max=127)])
    constitution = IntegerField("CON", validators=[NumberRange(min=3, max=20)])
    strength = IntegerField("STR", validators=[NumberRange(min=3, max=20)])
    dexterity = IntegerField("DEX", validators=[NumberRange(min=3, max=20)])
    wisdom = IntegerField("WIS", validators=[NumberRange(min=3, max=20)])
    intelligence = IntegerField("INT", validators=[NumberRange(min=3, max=20)])
    charisma = IntegerField("CHA", validators=[NumberRange(min=3, max=20)])
    submit = SubmitField("Save Changes")


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
