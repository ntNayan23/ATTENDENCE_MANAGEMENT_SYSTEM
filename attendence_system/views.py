import base64
from datetime import datetime
from fileinput import filename
import pickle
from sqlite3 import OperationalError
from flask_mail import *
import face_recognition
import os
import time
from flask import  render_template, flash, redirect, request,url_for,Response
from attendence_system import app , mail, db
from attendence_system.form import AddStud, LoginForm, addHOD, Branchform
from attendence_system.model import BranchName, Employee, FaceEncoding
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError
import cv2

from attendence_system.function import FaceEncode, capture_images, compare_face_encodings, find_file, generate_frames, rename_images, request_camera_permission, stop_camera

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
    form = AddStud()
    if request.method == 'POST':
        if form.validate_on_submit():
            print(form.cam_fold.data)
            try:
                flash(f'{form.Full_name.data} added sucessfully!','success' )                
                return redirect(url_for("addStud"))
            except BuildError as  e:
                flash(f'{e}', "danger")
    else:
        return render_template(
            "hodpg/addstudent.html",
            title='Add Student',
            form=form,
            year=datetime.now().year
        
        )
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
            dob = form.DOB_field.data
            doj = form.date_of_joining.data
            email = form.email.data
            teacher_id = form.teacher_id.data
            BranchName = form.branch_name.data
            teacher_id = form.teacher_id.data
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
                                                is_hod=False,
                                                branch_id=BranchName
                                                )
                        db.session.add(new_employee)
                        db.session.commit()  
                        for item in serialized_encoding_list :
                            new_face_encoding = FaceEncoding(encoding=item,employee_id=new_employee.id)         
                            db.session.add(new_face_encoding)
                            db.session.commit()   
                        serial_data = db.session.query(FaceEncoding.encoding).filter(FaceEncoding.id == 1).first()
                        serialized_data = serial_data.encoding
                        compare_face_encodings(serialized_encoding_list[0],bytes(serialized_data))  
                        stop_camera(camera_active)
                        flash(f'{form.Full_name.data} added successfully!', 'success')
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
   
 
