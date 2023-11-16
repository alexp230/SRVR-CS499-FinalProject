# import the required libraries/modules
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import sqlite3 as sql
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy import Enum
import hashlib
import os
import re
import random
import datetime
import calendar
from datetime import datetime, timedelta

basedir = os.path.abspath(os.path.dirname(__file__)) 
app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRAC_MODIFICATIONS']=False

app.config['SECRET_KEY'] = 'oursecretkey'

db = SQLAlchemy(app)
Migrate(app,db)

# Initialize a global variable to keep track of the user's login status
Sign_IN = False

# Get the current date and time
current_date = datetime.now()
# Get the current day of the week as an integer (Monday is 0, Sunday is 6)
day_of_week_int = current_date.weekday()

# Convert the integer representation to the day name
day_name = current_date.strftime("%A")
# Get today's date
today_date = datetime.today().date()

print(f"Today's date is: {today_date}")
print(f"Day of the week (integer representation): {day_of_week_int}")
print(f"Day of the week (name): {day_name}")

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

# Need to encrypt password
def updatePassword(email, password):
    """
    This function takes an email and password as input and updates the password for the user with the matching email.
    """
    user = User.query.filter_by(email=email).first()
    user.password = password
    db.session.commit()

def updateAddress(email, address):
    """
    This function takes an email and address as input and updates the address for the user with the matching email.
    """
    user = User.query.filter_by(email=email).first()
    user.address = address
    db.session.commit()

def updateEmail(email, newEmail):
    """
    This function takes an email and newEmail as input and updates the email for the user with the matching email.
    """
    user = User.query.filter_by(email=email).first()
    user.email = newEmail
    db.session.commit()

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

    user_id = db.Column(db.Integer, primary_key=True)
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
        return f"{self.user_id}. {self.fname} {self.lname} [({self.email}) - {self.password}] | {self.address}" 

class Meal(db.Model):
    __tablename__ = "meals"

    meal_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    category = db.Column(Enum('Seafood', 'Italian', 'BBQ', 'Sandwich', 'Chicken', 'Desserts', name='meal_types'), nullable=False)
    photo_URL = db.Column(db.String, nullable=True)
    instructions = db.Column(db.String, nullable=True)
    allergens = db.Column(db.String, nullable=True)

    def __init__(self, name, category, photo_URL, instructions, allergens):
        self.name = name
        self.category = category
        self.photo_URL = photo_URL
        self.instructions = instructions
        self.allergens = allergens

    
    def __repr__(self):
        return f"{self.meal_id}. \nCategory: {self.category}\nName:- {self.name}\nPhoto:- {self.photo_URL}\nInstructions:- {self.instructions}\n"

class Box(db.Model): # This is the box that will be delivered to the user
    # A box will contain 7 meals times the number of people in the household
    __tablename__ = "boxes"

    box_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    ordered_meals = db.Column(db.String)

    def __init__(self, user_id, ordered_meals):
        self.user_id = user_id
        self.ordered_meals = ordered_meals

    def __repr__(self):
        return f"{self.box_id}. Ordered Meals: {self.ordered_meals}"
    

class Payment_Methods(db.Model):
    __tablename__ = "payment_methods"

    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    card_number = db.Column(db.String)
    card_holder_name = db.Column(db.String, nullable=False)
    card_exp_date = db.Column(db.String, nullable=False)
    card_CCV = db.Column(db.String, nullable=False)
    # subscriptionType = db.Column(db.String, nullable=False) 
    # should have been an enum. I also think this should be in the subscription table.

    def __init__(self, user_id, card_number, card_holder_name, card_exp_date, card_CCV):
        self.user_id = user_id
        self.card_number = card_number
        self.card_holder_name = card_holder_name
        self.card_exp_date = card_exp_date
        self.card_CCV = card_CCV
        # self.subscriptionType = subscriptionType

    def __repr__(self):
        hidden_card_number = '*' * (len(self.card_number) - 4) + self.card_number[-4:]
        # return f"{self.P_id}. Payment_Method(card_number={self.card_number}, user_id={self.user_id}, " \
        #        f"card_holder_name={self.card_holder_name}, card_exp_date={self.card_exp_date}, card_CCV={self.card_CCV}), "
        return hidden_card_number

    def get_card_number(self):
        return self.card_number

    def get_card_holder_name(self):
        return self.card_holder_name

    def get_card_exp_date(self):
        return self.card_exp_date


class PastOrders(db.Model):
    __tablename__ = "past_orders"

    transaction_id = db.Column(db.Integer, primary_key=True) # Transaction ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    box_id = db.Column(db.Integer, db.ForeignKey('boxes.user_id'), nullable=False) # Box ID
    payment_method = db.Column(db.String, nullable=False)
    shipping_address = db.Column(db.String, nullable=False)
    subscription_type = db.Column(db.String, nullable=False)
    order_date = db.Column(db.String, nullable=False)
    order_time = db.Column(db.String, nullable=False)

    def __init__(self, user_id, box_id, payment_method, shipping_address, subscription_type, order_date, order_time):
        self.user_id = user_id
        self.box_id = box_id
        self.payment_method = payment_method
        self.shipping_address = shipping_address
        self.subscription_type = subscription_type
        self.order_date = order_date
        self.order_time = order_time

    def __repr__(self):
        return f"PastOrders(T_ID={self.transaction_id}, user_id={self.user_id}, box_id={self.box_id}" \
               f"payment_method='{self.payment_method}', shipping_address='{self.shipping_address}', " \
               f"subscription_type='{self.subscription_type}', Date={self._Date}, Time={self._Time})"



class Subscription(db.Model):
    __tablename__ = "subscriptions"

    subscription_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    delivery_day = db.Column(db.String)  # Monday, Tuesday, etc.
    household_size = db.Column(db.Integer)  # 2 or 4
    # Other fields as needed...

    def __init__(self, user_id, delivery_day, household_size):
        self.user_id = user_id
        self.delivery_day = delivery_day
        self.household_size = household_size

    def __repr__(self):
        return f"Subscription(subscription_id={self.subscription_id}, user_id={self.user_id}, " \
                f"delivery_day='{self.delivery_day}', household_size={self.household_size})"
                   

with app.app_context():
    # Create the tables (if not already created)
    db.create_all()


# All this function needs to do is display a thankyou message / give conformation that 
# the account was created, then redirect the user to the login page.
@app.route('/thankyou', methods = ["GET", "POST"])
def thankyou():
    msg = "Account created successfully. Thank you for creating an account with us!"
    return render_template("thankyou.html", msg = msg)

# Function is used to display the signupform.html only, the uses add() to process the data.
@app.route('/signup', methods = ["GET", "POST"])
def signup():
    msg = None
    return render_template("signupform.html", msg = msg)

# Function is used to display the loginform.html only, the uses submitlogin() to process the data.
@app.route('/login', methods = ["GET", "POST"])
def login():
    return render_template("loginform.html")

# Function is used to display the tempusrhome.html only
@app.route('/usrhome/<string:fname>', methods = ["GET", "POST"])
def usrhome(fname):
    user = User.query.filter_by(fname=fname).first()
    return render_template("tempusrhome.html", fname=fname, user=user)

# Function is used to display the paymentform.html only, the uses manageSubscription() to process the data.
# FOR SOME ODD REASON I CANT ADD FNAME TO THE URL FOR THIS FUNCTION WITHOUT IT BREAKING
@app.route('/paymentmethod/<string:fname>', methods = ["GET", "POST"])
def paymentmethod(fname):
    email = session["email"]
    user = User.query.filter_by(email=email).first()
    
    return render_template("paymentform.html", fname=fname, user=user)

# Function is used to display the tempusrsettings.html only, the uses TBD function to process the data.
@app.route('/usrsettings/<string:fname>', methods = ["GET", "POST"])
def usrsettings(fname):
    user = User.query.filter_by(fname=fname).first()
    return render_template("usrsettings.html", user=user)

# Function works, but needs to be routed to the correct page
@app.route('/updateInfo/<string:fname>', methods = ["GET", "POST"])
def updateInfo(fname):
    user = User.query.filter_by(email=session["email"]).first()
    msg=None
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        address = request.form.get("address")
        password = request.form.get("password")
        if password:
            print("Made it here")
            passwordEncode = hashlib.md5(request.form["password"].encode())
            if passwordEncode.digest() == user.password and passwordValidation(password):
                print("Made it here too")
                if email and email != user.email:
                    updateEmail(user.email, email)
                    msg = "Email updated successfully."
                if address and address != user.address:
                    updateAddress(user.email, address)
                    msg = "Address updated successfully."
                if fname and fname != user.fname:
                    user.fname = fname
                    db.session.commit()
                    msg = "First name updated successfully."
                if lname and lname != user.lname:
                    user.lname = lname
                    db.session.commit()
                    msg = "Last name updated successfully."
                if not msg:
                    msg = "No changes were made."
        else:
            msg = "Incorrect password. Please try again."
    return render_template("usrsettings.html", user=user, msg=msg)

# Function is used to display the tempchangepass.html only, the uses TBD function to process the data.
# Currently, the function is not working properly. It is not updating the password in the database.
@app.route('/changepass/<string:fname>', methods = ["GET", "POST"])
def changepass(fname):
    user = User.query.filter_by(email=session["email"]).first()
    msg=None
    if request.method == "POST":
        oldpassword = request.form.get("oldpassword")
        newpassword = request.form.get("newpassword")
        confirmpassword = request.form.get("confirmpassword")
        if oldpassword and newpassword and confirmpassword:
            if hashlib.md5(oldpassword.encode()).digest() == user.password:
                if newpassword == confirmpassword:
                    if passwordValidation(newpassword):
                        updatePassword(user.email, hashlib.md5(newpassword.encode()).digest())
                        msg = "Password updated successfully."
                    else:
                        msg = "Password must contain at least one capital letter, one lowercase letter, and end with a number."
                else:
                    msg = "New passwords do not match."
            else:
                msg = "Incorrect password. Please try again."
        else:
            msg = "Please fill out all fields."
    return render_template("changepass.html", user=user, msg=msg)


# Use this function to contain all the code for the signupform.html attributes and logic
# eg. Saving the users input and creating a record to hold their account in the database.
@app.route("/add", methods = ["POST"])
def add():
    fName = request.form.get("fname")
    lName = request.form.get("lname")
    email = request.form.get("email")
    address = request.form.get("address")
    password = request.form.get("password")
    confirmpassword = request.form.get("confirm_password")

    # Using MD5 to hash the password to be more secure.
    hash = hashlib.md5(password.encode()) 

    emailCheck = User.query.filter_by(email=email).first()
    if emailCheck: # If email already exists in database
        error = "The email you entered is already taken."
        return render_template ('signupform.html', error=error, password=password, confirmpassword=confirmpassword)
    
    if not passwordValidation(password):
        error = "Password must contain at least one capital letter, one lowercase letter, and end with a number."
        return render_template('signupform.html', error=error, password=password, confirmpassword=confirmpassword)
    
    if password != confirmpassword:
        error = "Passwords do not match."
        return render_template('signupform.html', error=error, password=password, confirmpassword=confirmpassword)

    newUser = User(fname=fName, lname=lName,  email=email, password=hash.digest(), address=address)

    db.session.add(newUser)
    db.session.commit()
    return redirect('thankyou')


# Function is used to grab the input from loginform.html and validate the users input to determine wether the account actually exists.
# If account exists, redirect the user to the tempusrhome.html
@app.route('/submitlogin', methods = ["GET", "POST"])
def submitlogin():
    msg = None
    global Sign_IN
    session.clear()
    
    if(request.method == "POST"):
        print("request.method == POST")
        email = request.form["email"]
        password = hashlib.md5(request.form["password"].encode())

        user = User.query.filter_by(email=email).first()
        print(user)
        if user:
            print("Is user")
            if user.password == password.digest():
                Sign_IN = True
                session["logged_in"] = True
                session["email"] = email
                session["fname"] = user.fname
                session["lname"] = user.lname
                session["address"] = user.address
                session["user_id"] = user.user_id
                msg = "Login Successful"

                return redirect(url_for("usrhome", fname = session["fname"]))
            else:
                msg = "Email or Password is invalid. Please try again."
        else:
            msg = "Account does not exist. Please try again."

    return render_template("loginform.html", msg = msg)

# Use this function to contain all the code for the main.html attributes and logic
# eg. hold any logic behind the html attributes if any are added.
@app.route('/')
def home():
    global Sign_IN
    # Sign_IN = False

    if session.get("logged_in") == True:
        Sign_IN = True
        email = session["email"]
        return render_template("main.html", user=User.query.filter_by(email=email).first(), Sign_IN=Sign_IN)

    return render_template("main.html")

@app.route('/browsemenu/') #not logged in
@app.route('/browsemenu/<string:fname>') #logged in
def browsemenu(fname=None):
    if session.get("logged_in") == True:
        fname = session["fname"]
        all_meals = Meal.query.all()
        return render_template("browsemenu.html", all_meals=all_meals,fname=fname)
    else:
        all_meals = Meal.query.all()
        return render_template("browsemenu.html", all_meals=all_meals)

@app.route('/category/<string:category>')
def get_meals_by_category(category):
    meals = Meal.query.filter_by(category=category).all()
    
    meals_data = [{'name': meal.name, 'photo_URL': meal.photo_URL} for meal in meals]

    return jsonify(meals_data)


@app.route('/cart')
def cart():
    selected_meals = session.get('selected_meals', [])
    print(selected_meals) # For debugging purposes  
    return render_template('cart.html', selected_meals=selected_meals)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    meal_name = request.json.get('mealName')
    selected_meals = session.get('selected_meals', []) 

    if len(selected_meals) < 7 and meal_name not in selected_meals:
        selected_meals.append(meal_name)
        session['selected_meals'] = selected_meals
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/subscribe', methods=['GET','POST'])
def subscribe():
    # Parse and collect subscription information from the form
    # delivery_day = request.form.get('delivery_day')
    # household_size = request.form.get('household_size')
    selected_meals = session.get('selected_meals', [])  # Assuming meals are stored in the session

    # Get user information (email, ID, etc.) from the session
    user_email = session.get('email')
    user = User.query.filter_by(email=user_email).first()
    fname = user.fname
    print(fname)
    cards = Payment_Methods.query.filter_by(user_id=user.user_id).all()

    # Create a new subscription record
    # new_subscription = Subscription(user_id=user.U_id, delivery_day=delivery_day, household_size=household_size)
    # db.session.add(new_subscription)
    # db.session.commit()

    # Store selected meals for this subscription (you might need a new table or structure for this)
    # ...

    # return redirect(url_for('subscription_confirmation'))  # Redirect to a confirmation page
    # return redirect(url_for('subscribe'))  # Redirect to a confirmation page
    return render_template("subscribe.html", selected_meals=selected_meals, cards=cards, fname=fname)

def checkDeliveryDate(delivery_date):
    # Get the current date
    current_date = datetime.now().date()
    # Parse the delivery_date string into a datetime object
    parsed_delivery_date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
    # Calculate the date range (1 to 7 days ahead of the current date)
    date_range_start = current_date + timedelta(days=1)
    date_range_end = current_date + timedelta(days=7)
    # Check if the parsed_delivery_date falls within the date range
    if date_range_start <= parsed_delivery_date <= date_range_end:
        return True
    else:
        return False

def numtoDayOfWeek(number):
    for day in range(0,7):
        if number == day:
            return calendar.day_name[day]

# This function allows the user to change subsctiption type
@app.route('/manageSubscription', methods = ["GET", "POST"])
def manageSubscription():
    # if session.get("logged_in") == True:
    # Accessing the inputs from paymentmethod.html
    msg = None
    if request.method == "POST":
        delivery_date = request.form.get("delivery-date")
        day_of_week = datetime.strptime(delivery_date, "%Y-%m-%d").weekday() # returns a number from 0-6
        day = numtoDayOfWeek(day_of_week) # returns the day of the week as a string
        subtype = request.form.get("household-size")
        cardNum = request.form.get("card")
        # if checkDeliveryDate(delivery_date):
        print("Delivery date is valid")
        print(f"Delivery date: {delivery_date}")
        print(f"Subscription type: {subtype}")
        print(f"Card number: {cardNum}")
        
        if delivery_date and subtype and cardNum:
            new_subscription = Subscription(user_id=session["user_id"], delivery_day=day, household_size=subtype)
            # Add the subscription to the database
            db.session.add(new_subscription)
            db.session.commit()

            selected_meals = session.get('selected_meals', [])
            selected_meals_str = ", ".join(selected_meals)
            # Create a new box record
            new_box = Box(user_id=session["user_id"], ordered_meals=selected_meals_str)
            # Add the box to the database
            db.session.add(new_box)
            db.session.commit()

            current_time = datetime.now().time()
            order_datetime = datetime.combine(datetime.strptime(delivery_date, "%Y-%m-%d").date(), current_time)
            # Create a new past order record
            new_past_order = PastOrders(
                                user_id=session["user_id"], 
                                box_id=new_box.box_id, payment_method=cardNum, 
                                shipping_address=session["address"], 
                                subscription_type=subtype, 
                                order_date=str(delivery_date), 
                                order_time=str(order_datetime)
                                )
            # Add the past order to the database
            db.session.add(new_past_order)
            db.session.commit()

            msg = f"Subscription updated successfully. Your reoccurring delivery is scheduled for every {day}."
            # Add the subscription to the database
    return render_template("thankyou.html", msg=msg)

# This function allows the user to change subsctiption type
@app.route('/addNewCard', methods = ["GET", "POST"])
def addNewCard():
    # if session.get("logged_in") == True:
    # Accessing the inputs from paymentmethod.html
    if request.method == "POST":
        delivery_date = request.form.get("delivery-date")
        subtype = request.form.get("SubPlan")
        cardNum = request.form.get("CardNum")
        cardHolder = request.form.get("CardName")
        expiry = str(request.form.get("ExpiryMonth")) + "/" + str(request.form.get("ExpiryYear"))
        cvv = request.form.get("CVV")
        # print statements for debugging
        print("Delivery date is valid")
        print(f"Delivery date: {delivery_date}")
        print(f"Subscription type: {subtype}")
        print(f"Card number: {cardNum}")
        print(f"Card holder: {cardHolder}")
        print(f"Expiry date: {expiry}")
        print(f"CVV: {cvv}")

        new_card = Payment_Methods(card_number=cardNum, user_id=session["user_id"], card_holder_name=cardHolder, card_exp_date=expiry, card_CCV=cvv)
        # Add the subscription to the database
        db.session.add(new_card)
        db.session.commit()
        msg = "Card Saved Successfully"
    return render_template("thankyou.html", msg=msg)



    # subtype = request.form.get("household-size")
    # cardnum = request.form.get("CardNum")
    # cardname = request.form.get("CardName")
    # expiry = str(request.form.get("ExpiryMonth")) + "/" + str(request.form.get("ExpiryYear"))
    # cvv = request.form.get("CVV")

    # usremail = session["email"]

    # usr = User.query.filter_by(email=usremail).first()
    # unique_Card_ID = random.randint(usr.U_id, usr.U_id+1000000)
    # # By the very small chance that the random number generated is already in the database, add another random amount to it
    # for card in Payment_Method.query.all():
    #     if card.P_id == unique_Card_ID:
    #         unique_Card_ID += random.randint(1,10)
    
    # newcard = Payment_Method(P_id=unique_Card_ID ,card_number=cardnum, U_id=usr.U_id, card_holder_name=cardname, card_exp_date=expiry, card_CCV=cvv, subscriptionType=subtype)
    # db.session.add(newcard)
    # db.session.commit()
    # msg = "Card Saved Successfully"

    return render_template("thankyou.html")

# WIP
# This function allows past order data of a user to be retrieved
@app.route('/pastorders/<string:fname>', methods = ["GET", "POST"])
def pastOrders(fname):

    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    user_id = session["user_id"]

    past_orders = PastOrders.query.filter_by(user_id=user_id).all()

    meals = Meal.query.all() # Get all meals
    boxes = Box.query.filter_by(user_id=user_id).all() # Get all boxes for the user

    return render_template("temp_past_orders.html", past_orders=past_orders, fname=fname, meals=meals, boxes=boxes)


if __name__ == "__main__":
     app.run(host="127.0.0.1", port=8080, debug=True) # Run the app on local host