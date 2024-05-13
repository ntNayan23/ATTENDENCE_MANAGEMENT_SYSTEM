from attendence_system import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Role can be 'hod', 'teacher', or 'student'

    # # Additional fields for Flask-Login
    # is_authenticated = db.Column(db.Boolean, default=False)
    # is_active = db.Column(db.Boolean, default=True)
    # is_anonymous = db.Column(db.Boolean, default=False)

    # # Define relationship with Employee
    # employee = db.relationship('Employee', backref='user', uselist=False)

    # # Define relationship with Student
    # student = db.relationship('Student', backref='user', uselist=False)

    def __repr__(self):
        return f'{self.username}'
    
    
class BranchName(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
     # Define relationship with Employee
    employees = db.relationship('Employee', backref='branch', lazy=True)
    
    # Define relationship with Student
    students = db.relationship('Student', backref='branch', lazy=True)
    
  
    
    def __repr__(self):
        return f'{self.name}'

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date)
    joining_date = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True, nullable=False)
    teacher_id = db.Column(db.String(20), unique=True)
    is_teacher = db.Column(db.Boolean, default=False) 
    is_hod = db.Column(db.Boolean, default=False)
     
    # Foreign key column to reference BranchName
    branch_id = db.Column(db.Integer, db.ForeignKey('branch_name.id'), nullable=False)
    
    # Define relationship with FaceEncoding
    face_encodings = db.relationship('FaceEncoding', backref='employee', lazy=True)
    
    # Define relationship with Attendance
    attendances = db.relationship('Attendance', backref='employee', lazy=True)
        
    def __repr__(self):
        return f'{self.name}:{self.dob}:{self.joining_date}:{self.email}:{self.teacher_id}:{self.is_hod}:{self.branch_id}'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    studying_year = db.Column(db.Integer)
    admission_date = db.Column(db.Date)
    dob = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    student_id = db.Column(db.String(20), unique=True)
    # Foreign key column to reference BranchName
    branch_id = db.Column(db.Integer, db.ForeignKey('branch_name.id'), nullable=False)
    
    # Define relationship with FaceEncoding
    face_encodings = db.relationship('FaceEncoding', backref='student', lazy=True)
    
    # Define relationship with Attendance
    attendances = db.relationship('Attendance', backref='student', lazy=True)
    def __repr__(self):
         return f'{self.name}:{self.studying_year}:{self.admission_date}:{self.dob}:{self.email}:{self.phone_number}'
    
class FaceEncoding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    encoding = db.Column(db.PickleType, nullable=False)
       
    # Foreign key column to reference Employee
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    
    # Foreign key column to reference Student
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    
    
    def __repr__(self):
        return  f'FaceEncoding(id={self.id})'
    
    

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    
    # Foreign key column to reference Employee
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    
    # Foreign key column to reference Student
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    
    def __repr__(self):
        return f'{self.timestamp}'

    
    
    
    
    
    
