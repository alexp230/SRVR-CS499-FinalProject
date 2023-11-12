"""
This file is used to create, read, update, and delete data from the database for testing purposes.
It is not used in the final version of the project.
"""
from main import db, app, User, Meal, Payment_Method
import os

# Create a new user object
new_user = User(fname="John", lname="Doe", email="johndoe@example.com", password="password123", address="123 Main St")

with app.app_context():

    # new_user = User(fname="John", lname="Doe", email="johndoe@example.com", password="password123", address="123 Main St")
    # new_payment = Payment_Method(P_id=2,card_number="55555555555555", U_id=new_user.U_id, card_holder_name="johndoe@example.com", card_exp_date="Nov 2023", 
    #                             card_CCV="123", subscriptionType="Premium")

    # # Add the user to the database
    # db.session.add(new_user)
    # db.session.add(new_payment)
    # db.session.commit()

    # Query the user within the same app context
    # usr = Payment_Method.query.filter_by(fname='Jane').first()
    print(Payment_Method.query.all())

    # pay = Payment_Method(card_number="987987", U_id="1", card_holder_name="John", card_exp_date=(2023, 11, 2), card_CCV=908, subscriptionType="2people")
    # db.session.add(pay)
    # db.session.commit()
    # print(pay)

    print(User.query.all())

    # for user in User.query.all():
    #     print(f"Deleted {user.fname} {user.lname} from the database.")
    #     print("\n")
    #     db.session.delete(user)
    #     db.session.commit()


    # for payment in Payment_Method.query.all():
    #     print(f"Deleted {payment} from the database.")
    #     print("\n")
    #     db.session.delete(payment)
    #     db.session.commit()
    for meal in Meal.query.all():
        print(meal)

    # Directory where PDF files are located
    # pdf_folder = "/static/Seafood/Instructions/"
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the "static" folder in the same directory
    pdf_folder = os.path.join(script_dir, "static", "Seafood", "Instructions")
    # List all PDF files in the folder
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

    # Iterate through meals and update photo_URL if a matching PDF file is found
    for meal in Meal.query.all():
        for pdf_file in pdf_files:
            if meal.name == os.path.splitext(pdf_file)[0]:
                meal.instructions = "/static/Seafood/Instructions/" + pdf_file

    pdf_folder = os.path.join(script_dir, "static", "Seafood", "Pictures")
    # List all PDF files in the folder
    jpg_files = [f for f in os.listdir(pdf_folder) if f.endswith(".jpg")]

    # Iterate through meals and update photo_URL if a matching PDF file is found
    for meal in Meal.query.all():
        for jpg_file in jpg_files:
            if meal.name == os.path.splitext(jpg_file)[0]:
                meal.photo_URL = "/static/Seafood/Pictures/" + jpg_file

    # Commit the changes to the database
    db.session.commit()
    # print("\n\n\n")
    
    # for meal in Meal.query.all():
    #     print(meal)

    