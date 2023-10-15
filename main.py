# import the required libraries/modules
from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3 as sql
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import re
from sqlalchemy import LargeBinary, func, desc
import os


basedir = os.path.abspath(os.path.dirname(__file__)) 
app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRAC_MODIFICATIONS']=False

app.config['SECRET_KEY'] = 'oursecretkey'

db = SQLAlchemy(app)
Migrate(app,db)

# Initialize a global variable to keep track of the user's login status
Sign_IN = False

def passwordValidation(PWD):
    """
    This function takes a password string as input and returns True if it meets the following criteria:
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Ends with a number
    Otherwise, it returns False.
    """
    regexCapLetter = r'[A-Z]'
    regexLowLetter = r'[a-z]'
    regexEndNumber = r'[0-9]$'
    regexList = [regexCapLetter, regexLowLetter, regexEndNumber]
    count = 0
    for regex in range(0,3):
        match = re.search(regexList[regex],PWD)
        if match:
            count+=1
    if count == 3:
        return True
    else:
        return False

def registrationForm(FlaskForm):
    name = StringField(validators = [DataRequired()])
    email = StringField(validators = [DataRequired()])
    address = StringField(validators = [DataRequired()])
    password = StringField(validators = [DataRequired()])
    confirmpassword = StringField(validators = [DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField(validators = [DataRequired()])
    password = StringField(validators = [DataRequired()])
    submit = SubmitField('Login')


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text)
    password = db.Column(db.Text)
    address = db.Column(db.Text)
    subscriptionType = db.Column(db.Text)

    def __init__(self, name, email, password, address, subscriptionType):
        self.name = name
        self.email = email
        self.password = password
        self.address = address
        self.subscriptionType = subscriptionType

    def __repr__(self):
        return f"User {self.name} has been created."

with app.app_context():
    # Create the tables (if not already created)
    db.create_all()

@app.route('/')
def home():
    global Sign_IN
    Sign_IN = False

    return render_template("main.html")

if __name__ == "__main__":
     app.run(host="127.0.0.1", port=8080, debug=True) # Run the app on local host