# import the required libraries/modules
from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3 as sql
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from sqlalchemy import ForeignKey, LargeBinary, func, desc, Enum, UniqueConstraint, Date, Time, PrimaryKeyConstraint
import hashlib
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

    U_id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.Text, nullable=False)
    lname = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)

    def __init__(self, fname, lname, email, password, address):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = password
        self.address = address

    def __repr__(self):
        return f"{self.U_id}. {self.fname} {self.lname} [({self.email}) - {self.password}] | {self.address}" 

class Meal(db.Model):
    __tablename__ = "meals"

    M_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    category = db.Column(Enum('Seafood', 'Italian', 'BBQ', 'Sandwich', 'Chicken', 'Desserts', name='meal_types'), nullable=False)

    def __init__(self, name, category):
        self.name = name
        self.category = category
    
    def __repr__(self):
        return f"{self.M_id}. {self.category} - {self.name}"

class Box(db.Model):
    __tablename__ = "boxes"

    B_id = db.Column(db.Integer, primary_key=True)
    ordered_meals = db.Column(db.String)

    def __init__(self, ordered_meals):
        self.ordered_meals = ordered_meals

    def __repr__(self):
        return f"{self.B_id}. Ordered Meals: {self.ordered_meals}"
    
class Payment_Method(db.Model):
    __tablename__ = "payment_methods"

    PM_id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String)
    U_id = db.Column(db.Integer, ForeignKey('users.U_id'))
    card_holder_name = db.Column(db.String, nullable=False)
    card_exp_date = db.Column(db.Date, nullable=False)
    card_CCV = db.Column(db.Integer, nullable=False)
    subscriptionType = db.Column(db.Text, nullable=False)

    def __init__(self,card_number, U_id, card_holder_name, card_exp_date, card_CCV, subscriptionType):
        self.card_number = card_number
        self.U_id = U_id
        self.card_holder_name = card_holder_name
        self.card_exp_date = card_exp_date
        self.card_CCV = card_CCV
        self.subscriptionType = subscriptionType

    def __repr__(self):
        return f"{self.PM_id}. Payment_Method(card_number={self.card_number}, U_id={self.U_id}, " \
               f"card_holder_name={self.card_holder_name}, card_exp_date={self.card_exp_date}, card_CCV={self.card_CCV}), " \
               f"Subscription Type={self.subscriptionType}"

class PastOrders(db.Model):
    __tablename__ = "past_orders"

    T_ID = db.Column(db.Integer, primary_key=True)
    U_ID = db.Column(db.Integer, ForeignKey('users.U_id'))
    B_ID = db.Column(db.Integer, ForeignKey('boxes.B_id'))
    email = db.Column(db.String, nullable=False)
    payment_method = db.Column(db.String, nullable=False)
    shipping_address = db.Column(db.String, nullable=False)
    subscription_type = db.Column(db.String, nullable=False)
    _Date = db.Column(db.Date, nullable=False)
    _Time = db.Column(db.Time, nullable=False)

    def __init__(self, U_ID, B_ID, email, payment_method, shipping_address, subscription_type, _Date, _Time):
        self.U_ID = U_ID
        self.B_ID = B_ID
        self.email = email
        self.payment_method = payment_method
        self.shipping_address = shipping_address
        self.subscription_type = subscription_type
        self._Date = _Date
        self._Time = _Time

    def __repr__(self):
        return f"PastOrders(T_ID={self.T_ID}, U_ID={self.U_ID}, B_ID={self.B_ID}, email='{self.email}', " \
               f"payment_method='{self.payment_method}', shipping_address='{self.shipping_address}', " \
               f"subscription_type='{self.subscription_type}', Date={self._Date}, Time={self._Time})"

with app.app_context():
    # Create the tables (if not already created)
    db.create_all()

# Use this function to contain all the code for the signup.html attributes and logic
# eg. Saving the users input and creating a record to hold their account in the database.
@app.route('/signup', methods = ["GET", "POST"])
def signup():
    msg = None
    
    return render_template("signup.html", msg = msg)


# Use this function to contain all the code for the add.html attributes and logic
# eg. Saving the users input and creating a record to hold their account in the database.
@app.route("/add", methods = ["POST"])
def add():
    fName = request.form.get("fName")
    lName = request.form.get("lName")
    email = request.form.get("email")
    address = request.form.get("address")
    password = request.form.get("password")
    confirmpassword = request.form.get("confirmPassword")

    # Using MD5 to hash the password to be more secure.
    hash = hashlib.md5(password.encode()) 

    emailCheck = User.query.filter_by(email=email).first()
    if emailCheck: # If email already exists in database
        error = "The email you entered is already taken."
        return render_template ('signup.html', error=error, password=password, confirmpassword=confirmpassword)
    
    if not passwordValidation(password):
        error = "Password must contain at least one capital letter, one lowercase letter, and end with a number."
        return render_template('signup.html', error=error, password=password, confirmpassword=confirmpassword)
    
    if password != confirmpassword:
        error = "Passwords do not match."
        return render_template('signup.html', error=error, password=password, confirmpassword=confirmpassword)

    newUser = User(fname=fName, lname=lName,  email=email, password=hash.digest(), address=address)

    db.session.add(newUser)
    db.session.commit()
    return redirect('thankyou')


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
    session.clear()
    if(request.method == "POST"):
        email = request.form["email"]
        password = hashlib.md5(request.form["psw"].encode())

        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password.digest():
                Sign_IN = True
                session["logged_in"] = True
                session["email"] = email
                return redirect(url_for("home"))
            else:
                msg = "Email or Password is invalid. Please try again."

    return render_template("login.html", msg = msg)

# Use this function to contain all the code for the main.html attributes and logic
# eg. hold any logic behind the html attributes if any are added.
@app.route('/')
def home():
    global Sign_IN
    Sign_IN = False

    if session.get("logged_in") == True:
        Sign_IN = True
        email = session["email"]
        return render_template("main.html", user=User.query.filter_by(email=email).first(), Sign_IN=Sign_IN)

    return render_template("main.html")

# WIP
# This function allows the user to change subsctiption type
@app.route('/manageSubscription', methods = ["GET"])
def manageSubscription():

    #allow user to change subscription

    return render_template("pymtmethod.html")

# WIP
# This function allows past order data of a user to be retrieved
@app.route('/past_orders', methods = ["POST"])
def pastOrders():

    if not session.get("logged_in"):
        # might be wrong url redirect name
        return redirect(url_for("login"))
    
    email = session["email"]

    past_orders = PastOrders.query.filter_by(email=email).all()

    return render_template("past_orders.html", past_orders=past_orders)

if __name__ == "__main__":
     app.run(host="127.0.0.1", port=8080, debug=True) # Run the app on local host