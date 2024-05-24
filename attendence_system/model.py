from datetime import datetime
from attendence_system import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Role can be 'hod', 'teacher', or 'student'


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
    student_id_2 = db.Column(db.String(20), unique=True)
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
        return  f'FaceEncoding(id={self.id}:encoding={self.encoding}:employee_id={self.employee_id}:student_id={self.student_id})'
    
    

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    in_time = db.Column(db.Time, nullable=False, default=datetime.now().time)
    out_time = db.Column(db.Time, nullable=True)
    
    # Foreign key column to reference Employee
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    
    # Foreign key column to reference Student
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)
    
    def __repr__(self):
        return f'Attendance(id={self.id},date={self.date}, in_time={self.in_time}, out_time={self.out_time})'

    
    
    
    
    
    
