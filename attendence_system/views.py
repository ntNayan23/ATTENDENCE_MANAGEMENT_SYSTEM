from datetime import datetime
from flask import render_template, flash, redirect,url_for
from attendence_system import app
from attendence_system.form import AddStud, LoginForm
from werkzeug.routing import BuildError
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
    if form.validate_on_submit():
        try:
            flash(f'Sucess Fully Login {form.Full_name.data}!','success' )
            return redirect(url_for('hoddashboard'))
        except BuildError as  e:
            flash(f'{e}', "danger")
    return render_template(
        "hodpg/addstudent.html",
        title='HOD Dashboard',
        form=form,
        year=datetime.now().year
     
    )