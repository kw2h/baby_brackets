from flask_wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, PasswordField, \
                    SubmitField, SelectField, SelectMultipleField, HiddenField
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import InputRequired, DataRequired, Length, Email, \
                               EqualTo
from models import User

class LoginForm(Form):
    user_name = StringField('', validators=[DataRequired()])
    password = PasswordField('', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(Form):
    user_name = StringField('', validators=[DataRequired()])
    first_name = StringField('')
    last_name = StringField('')
    password = PasswordField('',
                             validators=[InputRequired(),
                             EqualTo('pw_confirm', 'Passwords must match')])
    pw_confirm = PasswordField('')
    email = EmailField('', [DataRequired(), Email()])
    referral = HiddenField()
    submit = SubmitField('Submit')

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(user_name=self.user_name.data).first()
        user_email = User.query.filter_by(email=self.email.data).first()
        if user != None:
            self.user_name.errors.append('User name already taken.')
            return False
        elif user_email != None:
            self.email.errors.append('Email address already associated with a user name.')
            return False
        return True

class CreateForm(Form):
    name = StringField('', validators=[DataRequired()])
    #parent = BooleanField('I want to choose the list of names')
    submit = SubmitField('Submit')

class EditForm(Form):
    size = SelectField('Bracket Size',
                       choices=[('16','16'),
                           #    ('32','32'),
                           #    ('64','64')
                               ],
                       validators=[DataRequired()])
    sex = SelectField('Sex',
                       choices=[('',"It's a Surprise!"), ('M', 'M'), ('F', 'F'),])
    name1 = StringField('', validators=[DataRequired()])
    name2 = StringField('', validators=[DataRequired()])
    name3 = StringField('', validators=[DataRequired()])
    name4 = StringField('', validators=[DataRequired()])
    name5 = StringField('', validators=[DataRequired()])
    name6 = StringField('', validators=[DataRequired()])
    name7 = StringField('', validators=[DataRequired()])
    name8 = StringField('', validators=[DataRequired()])
    name9 = StringField('', validators=[DataRequired()])
    name10 = StringField('', validators=[DataRequired()])
    name11 = StringField('', validators=[DataRequired()])
    name12 = StringField('', validators=[DataRequired()])
    name13 = StringField('', validators=[DataRequired()])
    name14 = StringField('', validators=[DataRequired()])
    name15 = StringField('', validators=[DataRequired()])
    name16 = StringField('', validators=[DataRequired()])
    name17 = StringField('')
    name18 = StringField('')
    name19 = StringField('')
    name20 = StringField('')
    name21 = StringField('')
    name22 = StringField('')
    name23 = StringField('')
    name24 = StringField('')
    name25 = StringField('')
    name26 = StringField('')
    name27 = StringField('')
    name28 = StringField('')
    name29 = StringField('')
    name30 = StringField('')
    name31 = StringField('')
    name32 = StringField('')
    name33 = StringField('')
    name34 = StringField('')
    name35 = StringField('')
    name36 = StringField('')
    name37 = StringField('')
    name38 = StringField('')
    name39 = StringField('')
    name40 = StringField('')
    name41 = StringField('')
    name42 = StringField('')
    name43 = StringField('')
    name44 = StringField('')
    name45 = StringField('')
    name46 = StringField('')
    name47 = StringField('')
    name48 = StringField('')
    name49 = StringField('')
    name50 = StringField('')
    name51 = StringField('')
    name52 = StringField('')
    name53 = StringField('')
    name54 = StringField('')
    name55 = StringField('')
    name56 = StringField('')
    name57 = StringField('')
    name58 = StringField('')
    name59 = StringField('')
    name60 = StringField('')
    name61 = StringField('')
    name62 = StringField('')
    name63 = StringField('')
    name64 = StringField('')
    submit = SubmitField('Submit')
