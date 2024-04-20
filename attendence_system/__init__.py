
import json
import os
from flask import Flask
from flask_mail import *

app = Flask(__name__)
# Check if the file exist
with open('config.json', 'r') as f:
    params = json.load(f)['params']

app.config['SECRET_KEY']='a4dc9b9243e609c180d6eba249623992'
app.config['MAIL_SERVER']="smtp.gmail.com"
app.config['MAIL_PORT']=587
app.config['MAIL_USERNAME']=params['gmail-user']
app.config['MAIL_PASSWORD']=params['gmail-password']
app.config['MAIL_USE_TLS']= True
app.config['MAIL_USE_SSL']= False
mail = Mail(app)
import attendence_system.views