from starlette_wtf import StarletteForm
from wtforms import (StringField, BooleanField, TextAreaField, PasswordField,
                    SubmitField, SelectField, SelectMultipleField, HiddenField)
from wtforms.fields import DateField, EmailField
from wtforms.validators import (InputRequired, DataRequired, Length, Email,
                               EqualTo)


class LoginForm(StarletteForm):
    username = StringField("", validators=[DataRequired()])
    password = PasswordField("", validators=[DataRequired()])
    submit = SubmitField("Log In")
