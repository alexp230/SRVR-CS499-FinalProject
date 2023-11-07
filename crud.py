"""
This file is used to create, read, update, and delete data from the database for testing purposes.
It is not used in the final version of the project.
"""
from main import db, app, User, Meal, Payment_Method

# Create a new user object
# new_user = User(fname="John", lname="Doe", email="johndoe@example.com", password="password123", address="123 Main St")

with app.app_context():
    # # Add the user to the database
    # db.session.add(new_user)
    # db.session.commit()

    # Query the user within the same app context
    # usr = Payment_Method.query.filter_by(fname='Jane').first()
    print(Payment_Method.query.all())

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

    

    
