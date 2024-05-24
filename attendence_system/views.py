import base64
from datetime import datetime
from fileinput import filename
import pickle
from sqlite3 import OperationalError
from flask_mail import *
import face_recognition
import os
import time
from io import BytesIO
import pandas as pd
from flask import  render_template, flash, redirect, request, send_file,url_for,Response
from attendence_system import app , mail, db, stop_task
from attendence_system.form import AddStud, AttendanceForm, LoginForm, TaskForm, addHOD, Branchform
from attendence_system.model import Attendance, BranchName, Employee, FaceEncoding, User,Student
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError
import cv2

from attendence_system.function import FaceEncode, capture_images, compare_face_encodings, download_excel, find_file, generate_frames, generate_password, rename_images, stop_camera, background_task
from threading import Thread 
import threading

camera_active = False

@app.route('/')
@app.route('/home')
def home():
    with app.app_context():
        # Create all database tables
        db.create_all()
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home',
        year=datetime.now().year,
    )



@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            flash(f'Sucess Fully Login {form.email.data}!','success' )
            return redirect(url_for('admindashboard'))
        except BuildError as  e:
            flash(f'{e}', "danger")
    return render_template(
        'admin_login.html',
        title='Admin Login',
        form=form,
        year=datetime.now().year,
        
    )

@app.route('/hod',  methods=['GET','POST'])
def hod():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            flash(f'Sucess Fully Login {form.email.data}!','success' )
            return redirect(url_for('hoddashboard'))
        except BuildError as  e:
            flash(f'{e}', "danger")
    return render_template(
        'hod_login.html',
        title='HOD_Login',
        form=form,
        year=datetime.now().year
     
    )

@app.route('/admindashboard',  methods=['GET','POST'])
def admindashboard():
    return render_template(
        'admin/admindashboard.html',
        title='Admin Dashboard',
        year=datetime.now().year
     
    )


@app.route('/hoddashboard',  methods=['GET','POST'])
def hoddashboard():
    return render_template(
        "hodpg/hoddashboard.html",
        title='HOD Dashboard',
        year=datetime.now().year
     
    )

@app.route('/addStud',  methods=['GET','POST'])
def addStud():
    try:
        camera_active = False
        form = AddStud() 
        if request.method == 'POST':
            Name = form.Full_name.data
            dob = form.DOB_field1.data
            doa = form.admission_date.data
            year = form.year.data
            email = form.email.data
            phone_number = form.phone_number.data
            student_id = form.student_id.data
            BranchName = form.branch_name.data
            password = generate_password()
            if form.image_source.data == 'webcam':
                directory_path = "captured_images"
                rename_images(directory_path, Name) 
                image_files = os.listdir(directory_path)                        
                serialized_encoding_list = FaceEncode(image_files, directory_path)
                try:
                    existing_student = Student.query.filter_by(student_id_2=student_id).first()
                    if existing_student:
                        flash(f"Student ID {student_id} already exists!", "danger")
                        return redirect(url_for("addStud")) 
                    else:
                        new_student = Student(name=Name, dob=dob,  
                                                admission_date= doa,  
                                                studying_year=year,
                                                student_id_2=student_id, 
                                                branch_id=BranchName,
                                                email = email ,
                                                phone_number= phone_number
                                                )
                        db.session.add(new_student)
                        db.session.commit()  
                        for item in serialized_encoding_list :
                            new_face_encoding = FaceEncoding(encoding=item,student_id =new_student.id)         
                            db.session.add(new_face_encoding)
                            db.session.commit() 
                        # newuser = User(username=new_student,password = password ,role="Student")
                        # db.session.add(newuser)
                        # db.session.commit()
                        # serial_data = db.session.query(FaceEncoding.encoding).filter(FaceEncoding.id == 1).first()
                        # serialized_data = serial_data.encoding
                        # compare_face_encodings(serialized_encoding_list[0],bytes(serialized_data))  
                        stop_camera(camera_active)
                        msg = Message('HOD ID and Password ', sender='nayanthakre379@gmail.com', recipients=[email] )
                        msg.body = f"Use this to Login into the HOD Dashboard \n Login id :- {student_id}\n Password:-{password}"
                        mail.send(msg)
                        flash(f'{form.Full_name.data} added successfully and Login Credential Is send to the Email Address ', 'success')
                        return redirect(url_for("addStud")) 
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    flash(f"An error occurred: {str(e)}", "danger")
                    return redirect(url_for("addStud")) 
            else:
                
                flash("Invalid image source", "danger")
                return redirect(url_for("addStud"))  
        else:
            return render_template(
                "hodpg/addstudent.html",
                title='Add Student',
                form=form,
                year=datetime.now().year
            )
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for("addStud")) 

    
@app.route('/video')
def video():
    global camera_active
    camera_active = True
    return Response(generate_frames(camera_active),mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/stop_camera', methods=['POST'])
def stop_camera_route():
    global camera_active 
    camera_active = False
    stop_camera(camera_active)
    return 'Camera stopped!'


@app.route('/capture_images', methods=['POST'])
def capture_images_route():
    return capture_images()
  
@app.route('/addhod', methods=['GET', 'POST'])
def addhod():
    try:
        camera_active = False
        form = addHOD()  
        if request.method == 'POST':
            Name = form.Full_name.data
            dob = form.DOB_field2.data
            doj = form.date_of_joining.data
            email = form.email.data
            teacher_id = form.teacher_id.data
            BranchName = form.branch_name.data
            teacher_id = form.teacher_id.data
            password = generate_password()
            if form.image_source.data == 'webcam':
                directory_path = "captured_images"
                rename_images(directory_path, Name) 
                image_files = os.listdir(directory_path)                        
                serialized_encoding_list = FaceEncode(image_files, directory_path)
                try:
                    existing_employee = Employee.query.filter_by(teacher_id=teacher_id).first()
                    if existing_employee:
                        flash(f"Teacher ID {teacher_id} already exists!", "danger")
                        return redirect(url_for("addhod")) 
                    else:
                        new_employee = Employee(name=Name, dob=dob,  
                                                joining_date=doj,  
                                                email=email,
                                                teacher_id=teacher_id, 
                                                is_teacher = True,
                                                is_hod=False,
                                                branch_id=BranchName
                                                )
                        db.session.add(new_employee)
                        db.session.commit()  
                        for item in serialized_encoding_list :
                            new_face_encoding = FaceEncoding(encoding=item,employee_id=new_employee.id)         
                            db.session.add(new_face_encoding)
                            db.session.commit() 
                        newuser = User(username=teacher_id,password = password ,role="Teacher")
                        db.session.add(newuser)
                        db.session.commit()
                        serial_data = db.session.query(FaceEncoding.encoding).filter(FaceEncoding.id == 1).first()
                        print(type(serial_data))
                        serialized_data = serial_data.encoding
                        print(serial_data)
                        compare_face_encodings(serialized_encoding_list[0],bytes(serialized_data))  
                        stop_camera(camera_active)
                        msg = Message('HOD ID and Password ', sender='nayanthakre379@gmail.com', recipients=[email] )
                        msg.body = f"Use this to Login into the HOD Dashboard \n Login id :- {teacher_id}\n Password:-{password}"
                        mail.send(msg)
                        flash(f'{form.Full_name.data} added successfully and Login Credential Is send to the Email Address ', 'success')
                        return redirect(url_for("addhod")) 
                except Exception as e:
                    db.session.rollback()
                    flash(f"An error occurred: {str(e)}", "danger")
                    return redirect(url_for("addhod")) 
            else:
                flash("Invalid image source", "danger")
                return redirect(url_for("addhod"))  
        else:
            return render_template(
                "admin/addhodnew.html",
                title='Add Student',
                form=form,
                year=datetime.now().year
            )
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for("addhod")) 




@app.route('/Branch', methods=['GET', 'POST'])
def Branch():
    try:  
        form = Branchform()
        if request.method == 'POST':
            if form.validate_on_submit():
                if 'submit_button1' in request.form:
                    try:
                        branch_name = form.Branch_name.data.strip()
                        newbranch = BranchName(name=branch_name)
                        db.session.add(newbranch)
                        db.session.commit()
                        flash(f"Succesfully Added the branch Name", "success")
                        return redirect(url_for("Branch"))
                    except InvalidRequestError:
                        db.session.rollback()
                        flash(f"Something went wrong!", "danger")
                        return redirect(url_for("Branch"))
                    except IntegrityError:
                        db.session.rollback()
                        flash(f"Branch already exists!.", "warning")
                        return redirect(url_for("Branch"))
                    except DataError:
                        db.session.rollback()
                        flash(f"Invalid Entry", "warning")
                        return redirect(url_for("Branch"))
                    except InterfaceError:
                        db.session.rollback()
                        flash(f"Error connecting to the database", "danger")
                        return redirect(url_for("Branch"))
                    except DatabaseError:
                        db.session.rollback()
                        flash(f"Error connecting to the database", "danger")
                        return redirect(url_for("Branch"))
                    except BuildError:
                        db.session.rollback()
                        flash(f"An error occured !", "danger")
                        return redirect(url_for("Branch"))
                elif 'submit_button2' in request.form:
                    try:
                        branch_name = form.Branch_name.data
                        bn = BranchName.query.filter_by(name=branch_name).first()
                        db.session.delete(bn)
                        db.session.commit()
                        flash(f"Succesfully Deleted the branch Name", "danger")
                        return redirect(url_for("Branch"))
                    except InvalidRequestError as e:
                        db.session.rollback()
                        flash(f"Something went wrong!", "danger")
                        return redirect(url_for("Branch"))
                    except IntegrityError:
                        db.session.rollback()
                        flash(f"Username already exists!.", "warning")
                        return redirect(url_for("Branch"))
                    except DataError:
                        db.session.rollback()
                        flash(f"Invalid Entry", "warning")
                        return redirect(url_for("Branch"))
                    except InterfaceError:
                        db.session.rollback()
                        flash(f"Error connecting to the database", "danger")
                        return redirect(url_for("Branch"))
                    except DatabaseError:
                        db.session.rollback()
                        flash(f"Error connecting to the database", "danger")
                        return redirect(url_for("Branch"))
                    except BuildError:
                        db.session.rollback()
                        flash(f"An error occured !", "danger")
                        return redirect(url_for("Branch"))
                else:
                    print("choose corect option")
                try:
                    return redirect(url_for("Branch"))
                except BuildError as  e:
                    flash(f'{e}', "danger")
                    return redirect(url_for("Branch"))
        else:
            branches = BranchName.query.all()
            return render_template(
                "admin/Branch.html",
                title='Profile',
                form=form,
                branches = branches,
                year=datetime.now().year
            
            )  
    except OperationalError as e:
        flash(f"{e}", "danger")
        
@app.route('/Profile', methods=['GET', 'POST'])
def Profile():
    if request.method == 'POST':
            try:
                return redirect(url_for("profile"))
            except BuildError as  e:
                flash(f'{e}', "danger")
    else:
        return render_template(
            "admin/profile.html",
            title='Profile',
            year=datetime.now().year
        
        )
   

@app.route('/control_task', methods=['GET', 'POST'])
def control_task():
    task_from = TaskForm()
    attendance_form = AttendanceForm()
    attendance_records = [] 
    if request.method == 'POST':
        if task_from.validate_on_submit():  
            global stop_task
            if 'Start' in request.form:
                if not stop_task.is_set():
                    stop_task.clear()
                    thread = threading.Thread(target=background_task)
                    thread.daemon = True  # Daemonize thread
                    thread.start()
                    print("working task")
                    return redirect(url_for('control_task')) 
            elif 'Stop' in request.form:
                stop_task.set()
                return redirect(url_for('control_task')) 
        if attendance_form.validate_on_submit(): 
            if 'Generate_attendance' in request.form:
                Selected_brach_ID = attendance_form.branch_name.data
                Selected_brach_name = dict(attendance_form.branch_name.choices).get(Selected_brach_ID) 
                selected_value = attendance_form.name.data
                Candidate_selected =  dict(attendance_form.name.choices).get(selected_value)
              
                # attendance_records = Attendance.query.all()
                if Candidate_selected == 'Students':
                 
    # Selected students and a particular branch is selected
                    if Selected_brach_name != 'all':
                    
                        attendance_records =(db.session.query(
                                        Attendance,
                                        Student.name.label('student_name'),  # Include student name in the result
                                        BranchName.name.label('branch_name')  # Include branch name in the result
                                    )
                                    .join(Student, Attendance.student_id == Student.id)  # Join with Student table
                                    .join(BranchName,Student.branch_id == Selected_brach_ID)  # Join with BranchName table
                                    .filter(Attendance.student_id != None)  # Filter only student records
                                    
                                ).all()


                        print(attendance_records)
                    else:
                        # All branches are selected, select all students with their branch name
                        attendance_records = (
                            Attendance.query
                            .join(Student, Attendance.student_id == Student.id)
                            .join(BranchName, Student.branch_id == Selected_brach_ID)
                            .add_column(Student.name)
                            .all()
                        )
                elif Candidate_selected == 'Teachers':
                    # Selected employees and a particular branch is selected
                    if Selected_brach_name != 'all':
                        attendance_records =(db.session.query(
                                        Attendance,
                                        Employee.name.label('student_name'),  # Include student name in the result
                                        BranchName.name.label('branch_name')  # Include branch name in the result
                                    )
                                    .join(Employee, Attendance.employee_id == Employee.id)  # Join with Student table
                                    .join(BranchName,Employee.branch_id == Selected_brach_ID)  # Join with BranchName table
                                    .filter(Attendance.employee_id != None)  # Filter only student records
                                    
                                ).all()
                        print(attendance_records)
                    else:
                        # All branches are selected, select all employees with their branch name
                        attendance_records = (
                            Attendance.query
                            .join(Employee, Attendance.employee_id == Employee.id)
                            .join(BranchName, Student.branch_id == Selected_brach_ID)
                            .add_columns(Employee.name) 
                            .all()
                        )
                elif Candidate_selected == 'Both':
                    # Both students and employees are selected
                    if Selected_brach_name != 'all':
                        # Select students and employees related to the selected branch
                        attendance_records = (
                            Attendance.query
                            .join(Student, Attendance.student_id == Student.id)
                            .filter(Student.branch_id == Selected_brach_ID)
                            .add_columns(Student.name)  # Add student name to the query
                            .filter(Student.branch_id == Selected_brach_ID)
                            .union(
                                Attendance.query
                                .join(Employee, Attendance.employee_id == Employee.id)
                                .filter(Employee.branch_id == Selected_brach_ID)
                                .add_columns(Employee.name)  # Add employee name to the query
                                .filter(Employee.branch_id == Selected_brach_ID)
                            )
                            .all()
                        )
                        print(attendance_records)
                    else:
                        # All branches are selected, select all students and employees with their branch name
                        attendance_records = (
                            Attendance.query
                              .join(Student, Attendance.student_id == Student.id)
                              .join(BranchName, Student.branch_id == BranchName.id)
                               .add_columns(Student.name)
                            .union(
                                Attendance.query
                                 .join(Employee, Attendance.employee_id == Employee.id)
                                 .join(BranchName, Employee.branch_id == BranchName.id)
                                 .add_columns(Employee.name)  
                            )
                            .all()
                        )
                else:
                    # Handle the case when no value is selected
                    attendance_records = []
            elif'Download' in request.form:
                attendance_records = Attendance.query.all()
    # Convert the records to a list of dictionaries
                print(attendance_records)
                attendance_data = [{
                    'ID': record.id,
                    'Date': record.date,
                    'In Time': record.in_time,
                    'Out Time': record.out_time,
                    'Employee ID': record.employee_id,
                    'Student ID': record.student_id
                } for record in attendance_records]
                download_excel(attendance_data)
                
            
       
    else:
        return render_template( "admin/attendance.html",
            title='Attendance',
            task_from = task_from,
            attendance_form = attendance_form,
            attendance_records = attendance_records,
            year=datetime.now().year)
        
    return render_template("admin/attendance.html",
                           title='Attendance',
                           task_from = task_from,
                           attendance_form=attendance_form,
                           attendance_records = attendance_records,
                           year=datetime.now().year)
        
