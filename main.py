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
import dbms as srvrdb

basedir = os.path.abspath(os.path.dirname(__file__)) 
app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRAC_MODIFICATIONS']=False

app.config['SECRET_KEY'] = 'oursecretkey'

db = SQLAlchemy(app)
Migrate(app,db)

conn = srvrdb.connect_to_database()
cursor = conn.cursor()

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
    - Is less than or equal to 15 characters long
    Otherwise, it returns False.
    """
    regexCapLetter = r'[A-Z]'
    regexLowLetter = r'[a-z]'
    regexNumber = r'\d'
    regexList = [regexCapLetter, regexLowLetter, regexNumber]
    count = 0
    for regex in range(0,3):
        match = re.search(regexList[regex],PWD)
        if match:
            count+=1
    if count == 3 and len(PWD) <= 15:
        return True
    else:
        return False

def update_user_info(data):
    srvrdb.update_data5(cursor, "userTable", "firstname")

# All this function needs to do is display a thankyou message / give conformation that 
# the account was created, then redirect the user to the login page.
@app.route('/thankyou', methods = ["GET", "POST"])
def thankyou():
    msg = "Account created successfully. Thank you for creating an account with us!"
    return render_template("thankyou.html", msg = msg)

# Function is used to display the signupform.html only, the uses add() to process the data.
# Function works properly, do not touch. - Josh Patton
@app.route('/signup', methods = ["GET", "POST"])
def signup():
    msg = None
    return render_template("signupform.html", msg = msg)

# Function is used to display the loginform.html only, the uses submitlogin() to process the data.
# Function works properly, do not touch. - Josh Patton
@app.route('/login', methods = ["GET", "POST"])
def login():
    return render_template("loginform.html")

# Function is used to display the tempusrhome.html only, the uses changepass() to process the data.
# Function works properly, do not touch. - Josh Patton
@app.route('/usrhome/<string:email>', methods = ["GET", "POST"])
def usrhome(email):
    user = srvrdb.select_specific_data(cursor, "userTable", "email", email)
    return render_template("tempusrhome.html", email=session["email"], user=user)

# Function is used to display the paymentform.html only, the uses manageSubscription() to process the data.
# Function works properly, do not touch. - Josh Patton
@app.route('/paymentmethod/<string:email>', methods = ["GET", "POST"])
def paymentmethod(email):
    user = srvrdb.select_specific_data(cursor, "userTable", "email", session["email"])
    return render_template("paymentform.html", email=user[3], user=user)

# Function is used to display the tempusrsettings.html only, the uses updateInfo() to process the data.
# Function works properly, do not touch. - Josh Patton
@app.route('/usrsettings/<string:email>', methods = ["GET", "POST"])
def usrsettings(email):
    user = srvrdb.select_specific_data(cursor, "userTable", "email", session["email"])
    return render_template("usrsettings.html", email=user[3], user=user)

# Function is used to display the changepass.html only, the uses changepass() to process the data.
# Function works properly, do not touch. - Josh Patton
@app.route('/changepwd/<string:email>', methods = ["GET", "POST"])
def changepwd(email):
    user = srvrdb.select_specific_data(cursor, "userTable", "email", session["email"])
    return render_template("changepass.html", email=session["email"], user=user)

# Function used to process the input from usrsettings.html. Upon sucessful submission, redirects user to tempusrhome.html
# Function works properly, do not touch. - Josh Patton
@app.route('/updateInfo/<string:email>', methods = ["GET", "POST"])
def updateInfo(email):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user = srvrdb.select_specific_data(cursor, "userTable", "email", session["email"])

    msg=None
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        input_email = request.form.get("email")
        address = request.form.get("address")
        password = request.form.get("password")
        pwdhash = hashlib.md5(request.form["password"].encode()).digest()

        if not ((str(pwdhash) == user[4]) and passwordValidation(password)):
            msg = "Incorrect password. Please try again."
            return render_template("usrsettings.html", email=user[3], user=user, msg=msg)
        
        emailCheck = srvrdb.select_specific_data(cursor, "userTable", "email", input_email)
        if emailCheck and not (user[3]): # If email already exists in database
            msg = "The email you entered is already taken."
            return render_template("usrsettings.html", email=user[3], user=user, msg=msg)

        # Updating session variables to reflect the users changes.
        session["fname"] = fname
        session["lname"] = lname
        session["email"] = input_email
        session["address"] = address
        
        # Updating the users record in the database. 
        srvrdb.update_data4(cursor, "userTable", "firstname", fname, "lastname", lname, "email", input_email, "address", address, "email", email)
        conn.commit()

        return redirect(url_for("usrhome", email=user[3]))
              
# Function is used to process data from changepass.html. Upon sucessful submission redirects user to tempusrhome.html
# Function is working properly. Still need to implement hashing for password. - Josh Patton
@app.route('/changepass/<string:email>', methods = ["GET", "POST"])
def changepass(email):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user = srvrdb.select_specific_data(cursor, "userTable", "email", session["email"])    

    msg=None
    if request.method == "POST":
        oldpassword = request.form.get("oldpassword")
        curpwdhash = hashlib.md5(request.form["oldpassword"].encode()).digest()
        newpassword = request.form.get("newpassword")
        newpwdhash = hashlib.md5(request.form["newpassword"].encode()).digest()
        confirmpassword = request.form.get("confirmpassword")
        conpwdhash = hashlib.md5(request.form["confirmpassword"].encode()).digest()

        if not (oldpassword and newpassword and confirmpassword):
            msg = "Please fill out all fields!"

        # # Leave here as a reminder to implement hashing for passwords.
        # elif (hashlib.md5(newpassword.encode()).digest() == user["password"]):
        #     msg = "New password matches old password!"

        # elif (hashlib.md5(oldpassword.encode()).digest() != user["password"]):
        #     msg = "Incorrect password. Please try again!"

        elif (str(newpwdhash) == user[4]):
            msg = "New password is the same as the old password. Please try again!"
            return render_template('changepass.html', email=user[3], msg=msg)

        elif (str(curpwdhash) != user[4]):
            msg = "The current password you entered does not match your original password. Please try again!"
            return render_template('changepass.html', email=user[3], msg=msg)
        
        elif (str(newpwdhash) != str(conpwdhash)):
            msg = "New passwords do not match! Please try again!"
            return render_template('changepass.html', email=user[3], msg=msg)

        elif not passwordValidation(newpassword):
            msg = "Password must contain at least one capital letter, one lowercase letter, and a number!"
            return render_template('changepass.html', email=user[3], msg=msg)   
        
        # hash = hashlib.md5(request.form["newpassword"].encode()).digest()
    
    srvrdb.update_data1(cursor, "userTable", "password", str(newpwdhash), "email", session["email"])
    conn.commit()

    return redirect(url_for("usrhome", email=session["email"]))

# Function is used to process data from signupform.html. Upon sucessful submission redirects user to thankyou.html
# Function works properly, do not touch. - Josh Patton
@app.route("/add", methods = ["POST"])
def add():
    fName = request.form.get("fname")
    lName = request.form.get("lname")
    email = request.form.get("email")
    address = request.form.get("address")
    password = request.form.get("password")
    confirmpassword = request.form.get("confirm_password")

    # Using MD5 to hash the password to be more secure.
    hash = hashlib.md5(request.form["password"].encode()).digest()

    emailCheck = srvrdb.select_specific_data(cursor, "userTable", "email", email)
    if emailCheck: # If email already exists in database
        error = "The email you entered is already taken."
        return render_template('signupform.html', error=error, fName=fName, lName=lName, email=email, address=address, password=password, confirmpassword=confirmpassword)

    if not passwordValidation(password):
        error = "Password must contain at least one capital letter, one lowercase letter, and a number."
        return render_template('signupform.html', error=error, fName=fName, lName=lName, email=email, address=address, password=password, confirmpassword=confirmpassword)
    
    if password != confirmpassword:
        error = "Passwords do not match."
        return render_template('signupform.html', error=error, fName=fName, lName=lName, email=email, address=address, password=password, confirmpassword=confirmpassword)


    srvrdb.insert_data(cursor, (fName, lName, email, str(hash), address), "userTable")
    conn.commit()

    return redirect('thankyou')

# Function is used to grab the input from loginform.html and validate the users input to determine wether the account actually exists.
# If account exists, redirect the user to the tempusrhome.html
@app.route('/submitlogin', methods = ["GET", "POST"])
def submitlogin():
    msg = None
    global Sign_IN
    session.clear()
    
    if(request.method == "POST"):
        email = request.form["email"]
        hash = hashlib.md5(request.form["password"].encode()).digest()

        user = srvrdb.select_specific_data(cursor, "userTable", "email", email)

        if user:
            if user[4] == str(hash):
                Sign_IN = True
                session["logged_in"] = True
                session["user_id"] = user[0]
                session["fname"] = user[1]
                session["lname"] = user[2]
                session["email"] = user[3]
                session["address"] = user[5]
                # New session variable to keep track of the user's subscription status
                session["subscription_status"] = False
                subscriber = srvrdb.select_specific_data(cursor, "subscriptionTable", "user_id", user[0])
                if subscriber:
                    session["subscription_status"] = True
                else:
                    session["subscription_status"] = False
                msg = "Login Successful"
                print("Subscription status: ")
                print(session["subscription_status"])

                payment = srvrdb.select_specific_data(cursor, "pymntTable", "user_id", user[0])
                if not payment:
                    # send use to payment method page
                    msg = "Please add a payment method to continue login."
                    
                    return render_template("paymentform.html", email=email, msg=msg)

                return redirect(url_for("usrhome", email = email))
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
        user = srvrdb.select_specific_data(cursor, "userTable", "email", email)
        return render_template("main.html", user=user, Sign_IN=Sign_IN)

    return render_template("main.html")

@app.route('/browsemenu/') #not logged in
@app.route('/browsemenu/<string:fname>') #logged in
def browsemenu(fname=None):
    if session.get("logged_in") == True:
        fname = session["fname"]
        
        all_meals = srvrdb.fetch_all_rows("mealTable")
        return render_template("browsemenu.html", all_meals=all_meals,fname=fname)
    else:
        all_meals = srvrdb.fetch_all_rows("mealTable")
        return render_template("browsemenu.html", all_meals=all_meals)

# May not need this anymore. - Obie C
@app.route('/category/<string:category>')
def get_meals_by_category(category):
    
    meals = srvrdb.select_specific_data_many(cursor, "mealTable", "category", category)
    
    meals_data = [{'name': meal.name.replace("_", " "), 'photo_URL': meal.photo_URL} for meal in meals]

    return jsonify(meals_data)


@app.route('/cart')
def cart():
    selected_meals = session.get('selected_meals', [])
    print(selected_meals) # For debugging purposes  
    
    selected_meals = [meal.replace("_", " ") for meal in selected_meals]

    return render_template('cart.html', selected_meals=selected_meals)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    meal_name = request.json.get('mealName')
    selected_meals = session.get('selected_meals', [])
    box_capacity = 7 

    if len(selected_meals) < box_capacity and meal_name not in selected_meals:
        selected_meals.append(meal_name)
        session['selected_meals'] = selected_meals
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/subscribe', methods=['GET','POST'])
def subscribe():
    selected_meals = session.get('selected_meals', [])  # Assuming meals are stored in the session

    # Get user information (email, ID, etc.) from the session
    user_email = session.get('email')
    fname = session.get('fname')
    print(fname)
   
    cards = srvrdb.select_specific_data_many(cursor, "pymntTable", "user_id", session["user_id"])

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

# This function allows the user to change subscription type
@app.route('/manageSubscription', methods = ["GET", "POST"])
def manageSubscription():
    cards = srvrdb.select_specific_data_many(cursor, "pymntTable", "user_id", session["user_id"])
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    msg = None
    if request.method == "POST":
        delivery_date = request.form.get("delivery-date")

        if delivery_date == '':
            msg = "Please enter a valid delivery date."
            return render_template("subscribe.html", selected_meals=session['selected_meals'], email=session["email"], msg=msg, cards=cards)
        else:
            given_date = datetime.strptime(delivery_date, "%Y-%m-%d")
            seven_days_from_now = datetime.now() + timedelta(days=7)
            if given_date > seven_days_from_now or given_date <= datetime.now():
                msg = "Your delivery date must be within 7 days."
                return render_template("subscribe.html", selected_meals=session['selected_meals'], email=session["email"], msg=msg, cards=cards)
        day_of_week = datetime.strptime(delivery_date, "%Y-%m-%d").weekday() # returns a number from 0-6
        day = numtoDayOfWeek(day_of_week) # returns the day of the week as a string
        subtype = request.form.get("household-size")
        cardNum = request.form.get("card")
        # if checkDeliveryDate(delivery_date):
        print("Delivery date is valid")
        print(f"Delivery date: {delivery_date}")
        print(f"Subscription type: {subtype}")
        print(f"Card number: {cardNum}")

        selected_meals = session.get('selected_meals', [])
        if len(selected_meals) != 7 or cardNum == None or subtype == None:
            if cardNum == None:
                msg = "You do not have a payment on file."
            elif subtype == None:
                msg = "Please select a subscription type."
            else:
                msg = "Please select 7 meals."
            return render_template("subscribe.html",selected_meals=selected_meals, msg=msg, cards=cards)
        
        if delivery_date and subtype and cardNum:
            srvrdb.insert_data(cursor, (session["user_id"], day, subtype), "subscriptionTable")
            conn.commit()

            selected_meals = session.get('selected_meals', [])
            selected_meals_str = ", ".join(selected_meals)

            srvrdb.insert_data(cursor, (session["user_id"], selected_meals_str), "boxTable")
            conn.commit()

            current_time = datetime.now().time()
            order_datetime = datetime.combine(datetime.strptime(delivery_date, "%Y-%m-%d").date(), current_time)

            box = srvrdb.select_specific_data(cursor, "boxTable", "user_id", session["user_id"])
            srvrdb.insert_data(cursor, (session["user_id"], box[0], cardNum, session["address"], subtype, str(delivery_date), str(order_datetime)), "pastOrdersTable")
            conn.commit()

            msg = f"Subscription updated successfully. Your reoccurring delivery is scheduled for every {day}."

    return render_template("thankyou.html", msg=msg)

# Function is used to process data from paymentform.html. Upon sucessful submission redirects user to tempusrhome.html
# Function works properly, do not touch. - Josh Patton 
@app.route('/addNewCard/<string:email>', methods = ["GET", "POST"])
def addNewCard(email):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user = srvrdb.select_specific_data(cursor, "userTable", "email", session["email"]) 

    if request.method == "POST":
        delivery_date = request.form.get("delivery-date")
        subtype = request.form.get("SubPlan")
        cardNum = request.form.get("CardNum")
        cardHolder = request.form.get("CardName")
        cvv = request.form.get("CVV")


        expire_month = request.form.get("ExpiryMonth")
        expire_year = request.form.get("ExpiryYear")
        expiry = str(expire_month) + "/" + str(expire_year)
        

        if not (cardNum or cardHolder or expire_month or expire_year or cvv):
            error = "Please fill out all fields!"
            return render_template("paymentform.html", email=user[3], error=error)

        if ((len(cardNum) != 16) or (not cardNum.isdigit())):
            error = "Invalid card number!"
            return render_template("paymentform.html", email=user[3], error=error)
        
        if ((expire_year == None) or (expire_month == None)):
            error = "Enter valid expiration date!"
            return render_template("paymentform.html", email=user[3], error=error)

        expire_month = int(expire_month)
        expire_year = int(expire_year)
        today = datetime.today()
        expire_date = datetime(expire_year, expire_month, 1)
        if today > expire_date:
            error = "Card is expired!"
            return render_template("paymentform.html", email=user[3], error=error)
        
        if ((len(cvv) != 3 or (not cvv.isdigit()))):
            error = "Invalid CVV number!"
            return render_template("paymentform.html", email=user[3], error=error)

        srvrdb.insert_data(cursor, (user[0], cardNum, cardHolder, expiry, cvv), "pymntTable")
        conn.commit()

    return redirect(url_for("usrhome", email=user[3]))

# This function allows past order data of a user to be retrieved
@app.route('/pastorders/<string:email>', methods = ["GET", "POST"])
def pastOrders(email):

    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    user_id = session["user_id"]

    past_orders = srvrdb.select_specific_data_many(cursor, "pastOrdersTable", "user_id", user_id)
    meals = srvrdb.fetch_all_rows("mealTable")# Get all meals
    boxes = srvrdb.select_specific_data_many(cursor, "boxTable", "user_id", user_id)# Get all boxes for the user

    return render_template("pastorders.html", past_orders=past_orders, email=email, meals=meals, boxes=boxes)

@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html") 

@app.route('/howitworks')
def howitworks():
    return render_template("howitworks.html")

if __name__ == "__main__":
     app.run(host="127.0.0.1", port=8080, debug=True) # Run the app on local host