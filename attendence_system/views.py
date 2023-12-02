from datetime import datetime
from flask import render_template
from attendence_system import app

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )



@app.route('/admin')
def admin():
    """Renders the about page."""
    return render_template(
        'admin_login.html',
        title='Admin_Login',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/hod')
def hod():
    """Renders the about page."""
    return render_template(
        'hod_login.html',
        title='HOD_Login',
        year=datetime.now().year,
        message='Your application description page.'
    )