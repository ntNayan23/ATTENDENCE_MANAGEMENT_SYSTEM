from flask_wtf import FlaskForm
from wtforms import DateField, FileField, RadioField, SelectField, StringField,PasswordField,SubmitField, BooleanField
from wtforms.validators import DataRequired,Length,Email,Regexp,InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import MultipleFileField


class LoginForm(FlaskForm):
    # username = StringField(validators=[DataRequired(),Length(min=8,max=20,message='Please provide a valid name'),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,message='Usernames must have only letters, " "numbers, dots or underscores')])
    email = StringField('Email',validators=[DataRequired(),Email()])
    Password = PasswordField('Password',validators=[DataRequired(),Length(min=8,max=16),Regexp(regex="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}",flags=0)])
    remember = BooleanField('Remember Me')
    submit = SubmitField(label='Login')

class AddStud(FlaskForm):
    Full_name = StringField('Name', validators=[DataRequired()])
    DOB_field = DateField('Date of Birth (DOB)', format='%Y-%m-%d', validators=[DataRequired()])
    admission_date = DateField('Admission Date', validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[DataRequired()])
    year = SelectField('Year', choices=[('0', 'Select Year'),('1', 'First Year'), ('2', 'Second Year'), ('3', 'Third Year'), ('4', 'Fourth Year')],validators=[DataRequired()])
    image_source = RadioField('Image Source', choices=[('upload', 'Upload Image'), ('webcam', 'Capture from Webcam')], default='upload', validators=[InputRequired()])
    image_fold = MultipleFileField('Image File', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!'),Length(max=3, message='You can upload a maximum of 3 files.')])
    cam_fold = MultipleFileField("Cam Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!'),Length(max=3, message='You can upload a maximum of 3 files.')])
    Submit = SubmitField(label='Add')


# class ImageForm(FlaskForm):
#     image_file = FileField('Image File', validators=[DataRequired()])
#     submit = SubmitField('Submit')


