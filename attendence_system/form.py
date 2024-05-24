from flask_wtf import FlaskForm
from wtforms import DateField, FileField, RadioField, SelectField, StringField,PasswordField,SubmitField, BooleanField
from wtforms.validators import DataRequired,Length,Email,Regexp,InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import MultipleFileField

from attendence_system.model import BranchName


class LoginForm(FlaskForm):
    # username = StringField(validators=[DataRequired(),Length(min=8,max=20,message='Please provide a valid name'),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,message='Usernames must have only letters, " "numbers, dots or underscores')])
    email = StringField('Email',validators=[DataRequired(),Email()])
    Password = PasswordField('Password',validators=[DataRequired(),Length(min=8,max=16),Regexp(regex="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}",flags=0)])
    remember = BooleanField('Remember Me')
    submit = SubmitField(label='Login')

class AddStud(FlaskForm):
    Full_name = StringField('Name', validators=[DataRequired()])
    DOB_field1 = DateField('Date of Birth (DOB)', format='%Y-%m-%d', validators=[DataRequired()])
    admission_date = DateField('Admission Date', validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[DataRequired()])
    email = StringField(validators=[DataRequired(),Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired(message='Phone number is required'),Regexp(regex=r'^\d{10}$', message='Phone number must be 10 digits')])
    year = SelectField('Year', choices=[('0', 'Select Year'),('1', 'First Year'), ('2', 'Second Year'), ('3', 'Third Year'), ('4', 'Fourth Year')],validators=[DataRequired()])
    branch_name = SelectField('Branch Name', coerce=int, choices=[(0, 'Select Branch...')])
    image_source = RadioField('Image Source', choices=[('upload', 'Upload Image'), ('webcam', 'Capture from Webcam')], default='upload', validators=[InputRequired()])
    image_fold = MultipleFileField('Image File', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!'),Length(max=3, message='You can upload a maximum of 3 files.')])
    cam_fold = MultipleFileField("Cam Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!'),Length(max=3, message='You can upload a maximum of 3 files.')])
    Submit = SubmitField(label='Add')
    
    def __init__(self, *args, **kwargs):
        super(AddStud, self).__init__(*args, **kwargs)
        self.branch_name.choices += [(branch.id, branch.name) for branch in BranchName.query.all()]

class addHOD(FlaskForm):
    Full_name = StringField('Name', validators=[DataRequired()])
    DOB_field2 = DateField('Date of Birth (DOB)', format='%Y-%m-%d', validators=[DataRequired()])
    date_of_joining = DateField('Joining Date', validators=[DataRequired()])
    teacher_id = StringField('Teacher ID', validators=[DataRequired()])
    email = StringField(validators=[DataRequired(),Email()])
    branch_name = SelectField('Branch Name', coerce=int, choices=[(0, 'Select Branch...')])
    image_source = RadioField('Image Source', choices=[('upload', 'Upload Image'), ('webcam', 'Capture from Webcam')], default='upload', validators=[InputRequired()])
    image_fold = MultipleFileField('Image File', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!'),Length(max=3, message='You can upload a maximum of 3 files.')])
    cam_fold = MultipleFileField("Cam Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!'),Length(max=3, message='You can upload a maximum of 3 files.')])
    Submit = SubmitField(label='Add')
    
    
    def __init__(self, *args, **kwargs):
        super(addHOD, self).__init__(*args, **kwargs)
        self.branch_name.choices += [(branch.id, branch.name) for branch in BranchName.query.all()]

class Branchform(FlaskForm):
    Branch_name = StringField('Branch Name', validators=[DataRequired()])
    submit_button1 = SubmitField('ADD')
    submit_button2 = SubmitField('Delete')
    
class TaskForm(FlaskForm):
    Start = SubmitField('Start Attendance')
    Stop = SubmitField('Stop Attendance')

class AttendanceForm(FlaskForm):
    branch_name = SelectField('Select Branch Name', coerce=int, choices=[(0, 'Select Branch...')])
    name = SelectField('Select Candidate', coerce=int, choices=[(0, 'Select Candidate...'),(1, 'Students'),(2, 'Teachers'),(3, 'Both')])
    Generate_attendance = SubmitField('Generate')
    Download  = SubmitField('Download Excel')
    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        branches = BranchName.query.all()
        last_value = branches[-1].id if branches else None
        self.branch_name.choices += [(branch.id, branch.name) for branch in branches ]
        self.branch_name.choices.append((last_value, 'All'))
    
   


