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
    name1 = StringField('1 Seed')
    name2 = StringField('1 Seed')
    name3 = StringField('1 Seed')
    name4 = StringField('1 Seed')
    name5 = StringField('2 Seed')
    name6 = StringField('2 Seed')
    name7 = StringField('2 Seed')
    name8 = StringField('2 Seed')
    name9 = StringField('3 Seed')
    name10 = StringField('3 Seed')
    name11 = StringField('3 Seed')
    name12 = StringField('3 Seed')
    name13 = StringField('4 Seed')
    name14 = StringField('4 Seed')
    name15 = StringField('4 Seed')
    name16 = StringField('4 Seed')
    name17 = StringField('5 Seed')
    name18 = StringField('5 Seed')
    name19 = StringField('5 Seed')
    name20 = StringField('5 Seed')
    name21 = StringField('6 Seed')
    name22 = StringField('6 Seed')
    name23 = StringField('6 Seed')
    name24 = StringField('6 Seed')
    name25 = StringField('7 Seed')
    name26 = StringField('7 Seed')
    name27 = StringField('7 Seed')
    name28 = StringField('7 Seed')
    name29 = StringField('8 Seed')
    name30 = StringField('8 Seed')
    name31 = StringField('8 Seed')
    name32 = StringField('8 Seed')
    name33 = StringField('9 Seed')
    name34 = StringField('9 Seed')
    name35 = StringField('9 Seed')
    name36 = StringField('9 Seed')
    name37 = StringField('10 Seed')
    name38 = StringField('10 Seed')
    name39 = StringField('10 Seed')
    name40 = StringField('10 Seed')
    name41 = StringField('11 Seed')
    name42 = StringField('11 Seed')
    name43 = StringField('11 Seed')
    name44 = StringField('11 Seed')
    name45 = StringField('12 Seed')
    name46 = StringField('12 Seed')
    name47 = StringField('12 Seed')
    name48 = StringField('12 Seed')
    name49 = StringField('13 Seed')
    name50 = StringField('13 Seed')
    name51 = StringField('13 Seed')
    name52 = StringField('13 Seed')
    name53 = StringField('14 Seed')
    name54 = StringField('14 Seed')
    name55 = StringField('14 Seed')
    name56 = StringField('14 Seed')
    name57 = StringField('15 Seed')
    name58 = StringField('15 Seed')
    name59 = StringField('15 Seed')
    name60 = StringField('15 Seed')
    name61 = StringField('16 Seed')
    name62 = StringField('16 Seed')
    name63 = StringField('16 Seed')
    name64 = StringField('16 Seed')
    submit = SubmitField('Submit')
