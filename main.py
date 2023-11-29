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
from dbms import update_data1

basedir = os.path.abspath(os.path.dirname(__file__)) 
app = Flask (__name__)
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
# app.config['SQLALCHEMY_TRAC_MODIFICATIONS']=False

app.config['SECRET_KEY'] = 'oursecretkey'

# db = SQLAlchemy(app)
# Migrate(app,db)

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

    check_SUBS(user)

    user_id = user[0]   
    upcoming_meals = srvrdb.select_specific_data_many(cursor, "upcomingOrdersTable", "user_id", user_id)

    query = """
    SELECT boxTable.* FROM boxTable JOIN upcomingOrdersTable ON boxTable.box_id = upcomingOrdersTable.box_id WHERE upcomingOrdersTable.user_id = %s
"""
    all_meals = srvrdb.fetch_all_rows("mealTable")

    # Execute the query
    cursor.execute(query, (user_id,))
    boxes = cursor.fetchall()

    # boxes = srvrdb.select_specific_data_many(cursor, "boxTable", )
    
    return render_template("tempusrhome.html", email=session["email"], user=user, upcoming_meals=upcoming_meals, boxes=boxes, all_meals=all_meals)
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

@app.route('/admin', methods = ["GET", "POST"])
def admin():
    users = srvrdb.select_data(cursor, "userTable")
    orders = srvrdb.select_data(cursor, "pastOrdersTable")
    return render_template("admin.html", users=users, orders=orders)

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
    
    srvrdb.update_data1(cursor, "userTable", "password", str(newpwdhash), "email", session["email"])
    conn.commit()

    return redirect(url_for("usrhome", email=session["email"]))

# Function is used to process data from signupform.html. Upon sucessful submission redirects user to thankyou.html
# Function works properly, do not touch. - Josh Patton
@app.route("/add", methods = ["POST"])
def add():
    fName = request.form.get("fname")
    lName = request.form.get("lname")
    email = request.form.get("email").lower()
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
        email = request.form["email"].lower()
        hash = hashlib.md5(request.form["password"].encode()).digest()

        user = srvrdb.select_specific_data(cursor, "userTable", "email", email)

        if email == "admin@srvr.com":
            return redirect(url_for("admin"))

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
    session.clear()
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
        logged_in = True
        all_meals = srvrdb.fetch_all_rows("mealTable")

        return render_template("browsemenu.html", all_meals=all_meals,fname=fname,logged_in=logged_in)
    else:
        all_meals = srvrdb.fetch_all_rows("mealTable")
        not_logged_in = True
        return render_template("browsemenu.html", all_meals=all_meals,not_logged_in=not_logged_in)

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
@app.route('/aboutus/<string:email>')
def aboutus(email=None):
    if session.get("logged_in") == True:
        email = session["email"]
        logged_in = True
        return render_template("aboutus.html", email=email, logged_in=logged_in)
    else:
        not_logged_in = True
        return render_template("aboutus.html", not_logged_in=not_logged_in)

@app.route('/howitworks')
@app.route('/howitworks/<string:email>')
def howitworks():
    if session.get("logged_in") == True:
        email = session["email"]
        logged_in = True
        return render_template("howitworks.html", email=email, logged_in=logged_in)
    else:
        not_logged_in = True
        return render_template("howitworks.html", not_logged_in=not_logged_in)

def is_subscription_due(delivery_day, current_date):
    # Implement logic to check if the subscription is due for renewal
    # For instance, if the delivery_day matches the current day
    # or if the current day is within a renewal window (e.g. 3 days before the delivery day)
    # For demonstration purposes, we will assume that the subscription is due for renewal if the delivery day is in 3 days
    # You would implement your own logic here based on your business requirements
    # For example, you may want to check if the delivery day is today or within a 3 day window
    # You may also want to check if the subscription status is active

    return delivery_day.lower() == current_date.strftime("%A").lower()

def renew_subscription(user_id, household_size):
    # Simulate the subscription renewal process for the user
    # Prepare a random selection of 7 meals for the next 4 weeks

    # Define the number of weeks for meal preparation
    weeks_for_preparation = 4

    # Get the current date
    current_date = datetime.now().date()

    # Calculate the next delivery dates for the upcoming 4 weeks (Friday of each week)
    next_delivery_dates = [
        current_date + timedelta(days=(7 * i - current_date.weekday()) % 7)
        for i in range(1, weeks_for_preparation + 1)
    ]

    # Prepare a random selection of 7 meals for each delivery date
    for delivery_date in next_delivery_dates:
        # Get or generate a random selection of 7 meals (for demonstration, using a list of meals)
        # You would retrieve this from your mealTable in your database
        meals_for_delivery = get_random_meals(household_size)
        
        # Here, meals_for_delivery will be a list of 7 meal items for each delivery date
        # For demonstration purposes, let's print the delivery date and the selected meals
        print(f"Delivery Date: {delivery_date.strftime('%A, %B %d, %Y')}")
        print("Selected Meals:")
        for meal in meals_for_delivery:
            print(f"- {meal}")

        # You would perform actual database updates here if needed
        # For example, insert these meals into the boxTable for the user
        # This would involve creating a new row in the boxTable for each delivery date
        # with the selected meals for that date and the user_id
        
        # Example:
        # srvrdb.insert_data(cursor, (user_id, ', '.join(meals_for_delivery)), "boxTable")
        # conn.commit()

def get_random_meals():
    # Dummy list of meals for demonstration purposes
    all_meals = list(srvrdb.fetch_all_rows("mealTable"))
    
    # For each delivery, randomly select 7 meals for the user
    random.shuffle(all_meals)
    selected_meals = random.sample(all_meals, 7)
    return selected_meals

# Assume this route is triggered periodically to check subscriptions
@app.route('/check_subscriptions')
def check_subscriptions():
    # Retrieve active subscribers from subscriptionTable
    active_subscribers = srvrdb.fetch_all_rows("subscriptionTable")

    
    # Get the current date
    current_date = datetime.now().date()
    next_delivery_dates = [] # List to store the next delivery dates for each subscriber
    for subscriber in active_subscribers:
        user_id = subscriber[1]  # Extract user_id from subscriptionTable
        delivery_day = subscriber[2]  # Extract delivery day
        household_size = subscriber[3]  # Extract household size
        user = srvrdb.select_specific_data(cursor, "userTable", "user_id", user_id)
        last_delivery = srvrdb.get_most_recent_delivery(user_id)
        last_delivery_date_str = last_delivery[0][6]
        print(f"Last delivery date: {last_delivery_date_str}")

        last_delivery_date = datetime.strptime(last_delivery_date_str, "%Y-%m-%d").date()

        delivery_date_list = [
        last_delivery_date + timedelta(days=(7 * i))

        for i in range(1, 5)
        ]

        next_delivery_dates.extend(delivery_date_list)
        random_meals = get_random_meals()
        selected_meals = [meal[1] for meal in random_meals]
        selected_meals_str = ", ".join(selected_meals)

        # for day in next_delivery_dates:
        #     srvrdb.insert_data(cursor, (user_id, selected_meals_str), "boxTable")
        #     conn.commit()

        boxes = srvrdb.select_specific_data_many(cursor, "boxTable", "user_id", user_id)

        for i in range(0, len(next_delivery_dates)):
            print (f"{i+1}. {boxes[i][2]} \nWill be delivered on: {str(next_delivery_dates[i])}")

            # box = srvrdb.select_specific_data(cursor, "boxTable", "user_id", session["user_id"])
            


    for day in next_delivery_dates:
        print(f"Next delivery date: {day}")
       
    print ("Subscription check completed.")
    return "Subscription check completed."

#check_subscriptions()
# print(len(get_random_meals()))

def Update_Payment_Table(user):
    return
    



def check_SUBS(user) -> list:
    """
    Gets a user and adds up to four boxes to their upcoming orders

    RETURN: a list of the IDs of the boxes added
    """
    
    # Initialize important variables
    user_id = user[0]
    user_fname = user[1]
    user_lname = user[2]
    user_email = user[3]
    user_address = user[5]
    user_paymentMethod = srvrdb.select_specific_data(cursor, "pymntTable", "user_id", user_id)[2]

    # Gets user subscription and check if they have one
    active_subscription = srvrdb.select_specific_data(cursor, "subscriptionTable", "user_id", user_id)
    if (not active_subscription):
        print ("user does not have subscription")
        return
    
    user_subscriptionType = active_subscription[3]

    # Gets the next four days for meals to be shipped
    last_delivery = srvrdb.get_most_recent_delivery(user_id) #tuple
    last_delivery_date_str = last_delivery[0][6]
    last_delivery_date = datetime.strptime(last_delivery_date_str, "%Y-%m-%d").date()

    # Puts the for days days in a list
    delivery_date_list = []
    for i in range (1,5):
        delivery_date_list.append(str(last_delivery_date + timedelta(days=(7 * i))))

   # Initialize important variable 
    max_amount_of_orders = 4
    all_upcomingOrders = srvrdb.select_specific_data_many(cursor, "upcomingOrdersTable", "user_id", user_id)
    current_future_orders = len(all_upcomingOrders)

    modify_deadline = 3
    # Loops through all upcoming orders and checks to see if it needs to go past orders
    for order in all_upcomingOrders:
        # Gets the date from upcoming order and turns it into date object
        _date = order[6]
        date_object = datetime.strptime(_date, '%Y-%m-%d')

        # Get today's date
        today = datetime.now().date()

        # Calculate the difference in days between upcoming order and today
        days_difference = (date_object.date() - today).days

        # If upcoming meal date is past deadline
        if (days_difference <= modify_deadline):
            # Get the current date and time
            current_time = datetime.now().time()
            order_datetime = datetime.combine(datetime.strptime(_date, "%Y-%m-%d").date(), current_time)
            
            # Adds the upcoming meal to the past order table
            past_meal_data = [int(user_id), int(order[2]), str(str(order[3])[-4:]), str(order[4]), str(order[5]), str(order[6]), str(order_datetime)]
            srvrdb.insert_data(cursor, past_meal_data, "pastOrdersTable")

            # Delete upcoming meal from the upcoming meals table
            delete_query = "DELETE FROM upcomingOrdersTable WHERE user_id = %s AND order_date = %s"
            cursor.execute(delete_query, (user_id, order[6]))
            conn.commit()

    # Get all upcoming orders if modified in previous forloop
    all_upcomingOrders = srvrdb.select_specific_data_many(cursor, "upcomingOrdersTable", "user_id", user_id)
    current_future_orders = len(all_upcomingOrders)

    # If amount of upcoming orders is/exceeds max
    if (current_future_orders >= max_amount_of_orders):
        print("User needs no more boxes")
        return

    allboxes = [] #Stores id of all the added boxes to upcomingOrders
    # Adds enough meals for four weeks into upcomingOrdersTable
    for i in range(current_future_orders, max_amount_of_orders):
        # Gets seven random meals
        all_meals = get_random_meals()

        # Builds a string of the seven meals
        random_meals_string = ""
        for meals in all_meals:
            random_meals_string += (meals[1] + ", ")
        random_meals_string = random_meals_string[:-2]

        # Creates a new box and inserts it to boxTable with the meals
        box_data = [user_id, random_meals_string]
        srvrdb.insert_data(cursor, box_data, "boxTable")

        # Gets the newly created box id
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_inserted_id = cursor.fetchone()[0]
        
        # Creates a new upcoming box and adds to upcomingOrdersTable
        upcomingOrders_data = [user_id, last_inserted_id, user_paymentMethod, user_address, user_subscriptionType, delivery_date_list[i]]
        srvrdb.insert_data(cursor, upcomingOrders_data, "upcomingOrdersTable")

        conn.commit()
        
        allboxes.append(last_inserted_id)

    return allboxes
    
@app.route('/update_meal', methods=['POST'])
def update_meal():

    # Initialize variables 
    email = session["email"]
    user = srvrdb.select_specific_data(cursor, "userTable", "email", email)
    user_id = user[0]   
    upcoming_meals = srvrdb.select_specific_data_many(cursor, "upcomingOrdersTable", "user_id", user_id)
    all_meals = srvrdb.fetch_all_rows("mealTable")
    query = """
    SELECT boxTable.* FROM boxTable JOIN upcomingOrdersTable ON boxTable.box_id = upcomingOrdersTable.box_id WHERE upcomingOrdersTable.user_id = %s
"""
    
    # Get needed information from tempusrhome.html form
    box_id = request.form.get("box_id")
    current_meal_id = request.form.get("meal_id")
    new_meal_name = request.form.get("new_meal_name")

    # Get ordered meals string from box and current meal name
    ordered_meals = srvrdb.select_specific_data(cursor, "boxTable", "box_id", box_id)[2]
    current_meal_name = srvrdb.select_specific_data(cursor, "mealTable", "meal_id", current_meal_id)[1]

    # Replace current meal in box with new meal and update boxTable in database
    updated_meals = ordered_meals.replace(current_meal_name, new_meal_name)
    update_data1(cursor, "boxTable", "ordered_meals",  updated_meals, "box_id", box_id)
    
    # Execute the query
    cursor.execute(query, (user_id,))
    boxes = cursor.fetchall()
    conn.commit()
    msg = "Meal Updated!"
    return render_template("tempusrhome.html", email=session["email"], user=user, upcoming_meals=upcoming_meals, boxes=boxes, all_meals=all_meals, msg=msg)


if __name__ == "__main__":
     app.run(host="127.0.0.1", port=8080, debug=True) # Run the app on local host