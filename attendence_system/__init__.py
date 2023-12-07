
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY']='a4dc9b9243e609c180d6eba249623992'

import attendence_system.views