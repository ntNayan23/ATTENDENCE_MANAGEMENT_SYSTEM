from datetime import datetime
import os
from flask import render_template, flash, redirect, request,url_for
from attendence_system import app
from attendence_system.form import AddStud, LoginForm, addHOD
from werkzeug.routing import BuildError
import cv2





@app.route('/')
@app.route('/home')
def home():
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
    

  
@app.route('/addhod', methods=['GET', 'POST'])
def addhod():
    form = addHOD()
    if request.method == 'POST':
        if form.validate_on_submit():
            print(form.cam_fold.data)
            try:
                flash(f'{form.Full_name.data} added sucessfully!','success' )                
                return redirect(url_for("addhod"))
            except BuildError as  e:
                flash(f'{e}', "danger")
    else:
        return render_template(
            "admin/addhod.html",
            title='Add Student',
            form=form,
            year=datetime.now().year
        
        )
    
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
    
