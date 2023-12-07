from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, BooleanField
from wtforms.validators import DataRequired,Length,EqualTo,Email,Regexp
from wtforms import ValidationError,validators


class LoginForm(FlaskForm):
    # username = StringField(validators=[DataRequired(),Length(min=8,max=20,message='Please provide a valid name'),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,message='Usernames must have only letters, " "numbers, dots or underscores')])
    email = StringField('Email',validators=[DataRequired(),Email()])
    Password = PasswordField('Password',validators=[DataRequired(),Length(min=8,max=16),Regexp(regex="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}",flags=0)])
    remember = BooleanField('Remember Me')
    submit = SubmitField(label='Login')
