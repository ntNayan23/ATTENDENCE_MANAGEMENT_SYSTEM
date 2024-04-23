from attendence_system import db

class BranchName(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
  
    
    def __repr__(self):
        return f'{self.name}'

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date)
    joining_date = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True, nullable=False)
    teacher_id = db.Column(db.String(20), unique=True)
     face_encodings = db.relationship('FaceEncoding', backref='employee', lazy=True) # PickleType for storing face encoding data
    branch_name_id = db.Column(db.Integer, db.ForeignKey('branch_name.id'), nullable=False)
    branch_name = db.relationship('BranchName', backref=db.backref('employees', lazy=True))
    is_hod = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'{self.name}:{self.dob}:{self.joining_date}:{self.email}:{self.teacher_id}:{self.face_encoding}:{self.branch_name}:{self.is_hod}'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    branch_name_id = db.Column(db.Integer, db.ForeignKey('branch_name.id'), nullable=False)
    branch_name = db.relationship('BranchName', backref=db.backref('students', lazy=True))
    studying_year = db.Column(db.Integer)
    admission_date = db.Column(db.Date)
    dob = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    face_encodings = db.relationship('FaceEncoding', backref='student', lazy=True)
    
    def __repr__(self):
        return f'{self.name}:{self.branch_name}:{self.studying_year}:{self.admission_date}:{self.dob}:{self.email}:{self.phone_number}'
    
    
class FaceEncoding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    encoding = db.Column(db.PickleType, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    employee = db.relationship('Employee', backref=db.backref('face_encodings', lazy=True))
    student = db.relationship('Student', backref=db.backref('face_encodings', lazy=True))
    
    def __repr__(self):
        return f'FaceEncoding(id={self.id}, employee_id={self.employee_id}, student_id={self.student_id})'
    
    

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('attendance_records', lazy=True))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', backref=db.backref('attendance_records', lazy=True))
    
    def __repr__(self):
        return f'{self.timestamp}:{self.employee}::{self.student}'

    
    
    
    
    
    
