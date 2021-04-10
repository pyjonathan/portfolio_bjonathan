from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length
from wtforms import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user
from portfolio_bjonathan.models import User
import re

class LoginForm(FlaskForm):

    def check_username(self, field):
        if User.query.filter_by(username = field.data).first() == None:
            raise ValidationError('Invalid username or password, please try again.')

    username = StringField('Username', validators = [DataRequired(), check_username])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):

    def check_username(self, field):
        if User.query.filter_by(username = field.data).first() != None:
            raise ValidationError('Username already taken.  Please choose another.')

    username = StringField('Username', validators = [DataRequired(), check_username])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Submit')


