# import the required libraries/modules
from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3 as sql
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from sqlalchemy import LargeBinary, func, desc
import os
import re


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
    fname = db.Column(db.Text)
    lname = db.Column(db.Text)
    email = db.Column(db.Text)
    password = db.Column(db.Text)
    address = db.Column(db.Text)
    subscriptionType = db.Column(db.Text)

    def __init__(self, fname, lname, email, password, address, subscriptionType):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = password
        self.address = address
        self.subscriptionType = subscriptionType

    def __repr__(self):
        return f"Name: {self.fname} {self.lname} [({self.email}) - {self.password}] | UserAddress: {self.address} | UserSubscriptionType: {self.subscriptionType}"

with app.app_context():
    # Create the tables (if not already created)
    db.create_all()

# Use this function to contain all the code for the signup.html attributes and logic
# eg. Saving the users input and creating a record to hold their account in the database.
@app.route('/signup', methods = ["GET", "POST"])
def signup():
    msg = None
    if(request.method == "POST"):
        firstname = request.form["fName"]
        lastname = request.form["lName"]
        email = request.form["email"]
        password = request.form["psw"]
        if(request.form["email"] != "" and passwordValidation(request.form["psw"]) == True and request.form["psw"] == request.form["conpsw"]):
            msg = "Account created successfully. Thank you for creating an account with us!"
            return redirect(url_for("thankyou")) 
        
            # ---------- Connect to SQLAlchemy ----------
            # conn = sql.connect("jpm.db")
            # c = conn.cursor()
            # c.execute("INSERT INTO accounts VALUES('"+firstname+"', '"+lastname+"', '"+email+"', '"+password+"') ")           
            # conn.commit()
            # conn.close()


        else:
            msg = "Something went wrong. Please make sure your email is not blank, and both of your passwords match"
    return render_template("signup.html", msg = msg)

# All this function needs to do is display a thankyou message / give conformation that 
# the account was created, then redirect the user to the login page.
@app.route('/thankyou', methods = ["GET", "POST"])
def thankyou():
    msg = "Account created successfully. Thank you for creating an account with us!"
    return render_template("thankyou.html", msg = msg)

# Use this function to contain all the code for the login.html attributes and logic
# eg. Validating user input and granting user access to their account.
@app.route('/login', methods = ["GET", "POST"])
def login():
    msg = None
    global Sign_IN
    if(request.method == "POST"):
        email = request.form["email"]
        password = request.form["psw"]

        # ---------- Connect to SQLAlchemy ----------
        # con = sql.connect("jpm.db")
        # c = con.cursor()
        # c.execute("SELECT * FROM accounts WHERE email = '"+email+"' and password = '"+password+"'")
        # rows = c.fetchall()
        # for i in rows:
        #     if(email == i[2] and password == i[3]):
        #         session["logedin"]  = True
        #         session["email"] = email
        #         Sign_IN = True
        #         if Sign_IN == True:
        #             return redirect(url_for("userhome"))
        #     else:
        #         msg = "Email or Password is invalid. Please try again."

        #     con.commit()
        #     con.close()


    return render_template("login.html", msg = msg)

# Use this function to contain all the code for the main.html attributes and logic
# eg. hold any logic behind the html attributes if any are added.
@app.route('/')
def home():
    global Sign_IN
    Sign_IN = False

    return render_template("main.html")

if __name__ == "__main__":
     app.run(host="127.0.0.1", port=8080, debug=True) # Run the app on local host