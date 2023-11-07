"""
This file is used to create, read, update, and delete data from the database for testing purposes.
It is not used in the final version of the project.
"""
from main import db, app, User, Meal, Payment_Method
from datetime import datetime as dt

# Create a new user object
new_user = User(fname="John", lname="Doe", email="johndoe@example.com", password="password123", address="123 Main St")

with app.app_context():
    # # Add the user to the database
    db.session.add(new_user)
    db.session.commit()

    # Query the user within the same app context
    user = User.query.filter_by(fname='John').first()
    print(User.query.all())


    pay = Payment_Method(card_number="987987", U_id="1", card_holder_name="John", card_exp_date=dt(2023, 11, 2), card_CCV=908, subscriptionType="2people")
    db.session.add(pay)
    db.session.commit()
    print(pay)

    # for user in User.query.all():
    #     print(f"Deleted {user.fname} {user.lname} from the database.")
    #     print("\n")
    #     db.session.delete(user)
    #     db.session.commit()

    # for user in User.query.all():
    #     print(user)

    # print("\n\n\n")
    
    # for meal in Meal.query.all():
    #     print(meal)

    