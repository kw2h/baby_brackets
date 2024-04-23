from starlette_wtf import StarletteForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField
from wtforms.fields import  EmailField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.widgets import PasswordInput

from app.models import User


class LoginForm(StarletteForm):
    username = StringField("", validators=[DataRequired()])
    password = PasswordField("", validators=[DataRequired()])
    submit = SubmitField("Log In")


class RegisterForm(StarletteForm):
    username = StringField("", validators=[DataRequired()])
    first_name = StringField("")
    last_name = StringField("")
    password = PasswordField(
        "Password",
        widget=PasswordInput(hide_value=False),
        validators=[
            DataRequired("Please enter your password"),
            EqualTo("pw_confirm", "Passwords must match")
        ]
    )
    pw_confirm = PasswordField(
        "",
        widget=PasswordInput(hide_value=False),
        validators=[DataRequired()]
    )
    email = EmailField("", validators=[DataRequired(), Email()])
    referral = HiddenField()
    submit = SubmitField("Submit")

    # async def validate(self):
    #     user = await User.query.filter_by(username=self.username.data).first()
    #     user_email = await User.query.filter_by(email=self.email.data).first()
    #     if user != None:
    #         raise ValidationError("User Name is already in use")
    #     elif user_email != None:
    #         raise ValidationError("Email is already in use")


class CreateForm(StarletteForm):
    name = StringField("", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EditForm(StarletteForm):
    size = SelectField("Bracket Size",
                       choices=[("16","16"),
                           #    ("32","32"),
                           #    ("64","64")
                               ],
                       validators=[DataRequired()])
    sex = SelectField("Sex",
                       choices=[("","It's a Surprise!"), ("M", "M"), ("F", "F"),])
    name1 = StringField("", validators=[DataRequired()])
    name2 = StringField("", validators=[DataRequired()])
    name3 = StringField("", validators=[DataRequired()])
    name4 = StringField("", validators=[DataRequired()])
    name5 = StringField("", validators=[DataRequired()])
    name6 = StringField("", validators=[DataRequired()])
    name7 = StringField("", validators=[DataRequired()])
    name8 = StringField("", validators=[DataRequired()])
    name9 = StringField("", validators=[DataRequired()])
    name10 = StringField("", validators=[DataRequired()])
    name11 = StringField("", validators=[DataRequired()])
    name12 = StringField("", validators=[DataRequired()])
    name13 = StringField("", validators=[DataRequired()])
    name14 = StringField("", validators=[DataRequired()])
    name15 = StringField("", validators=[DataRequired()])
    name16 = StringField("", validators=[DataRequired()])
    name17 = StringField("")
    name18 = StringField("")
    name19 = StringField("")
    name20 = StringField("")
    name21 = StringField("")
    name22 = StringField("")
    name23 = StringField("")
    name24 = StringField("")
    name25 = StringField("")
    name26 = StringField("")
    name27 = StringField("")
    name28 = StringField("")
    name29 = StringField("")
    name30 = StringField("")
    name31 = StringField("")
    name32 = StringField("")
    name33 = StringField("")
    name34 = StringField("")
    name35 = StringField("")
    name36 = StringField("")
    name37 = StringField("")
    name38 = StringField("")
    name39 = StringField("")
    name40 = StringField("")
    name41 = StringField("")
    name42 = StringField("")
    name43 = StringField("")
    name44 = StringField("")
    name45 = StringField("")
    name46 = StringField("")
    name47 = StringField("")
    name48 = StringField("")
    name49 = StringField("")
    name50 = StringField("")
    name51 = StringField("")
    name52 = StringField("")
    name53 = StringField("")
    name54 = StringField("")
    name55 = StringField("")
    name56 = StringField("")
    name57 = StringField("")
    name58 = StringField("")
    name59 = StringField("")
    name60 = StringField("")
    name61 = StringField("")
    name62 = StringField("")
    name63 = StringField("")
    name64 = StringField("")
    submit = SubmitField("Submit")