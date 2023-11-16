"""
This file is used to create, read, update, and delete data from the database for testing purposes.
It is not used in the final version of the project.
"""
from main import db, app, User, Meal, Payment_Methods, Subscription
import os
import csv


with app.app_context():
    csv_file_path = os.path.join(os.path.dirname(__file__), 'CSV_File', 'meal_data.csv')
    def read_csv(csv_file_path):
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            #Used to add meals to the database
            for row in reader:
                # print(row)
                print(row['\ufeffname'], row['category'])
                meal = Meal(name=row['\ufeffname'], category=row['category'], photo_URL="NULL", instructions="NULL")
                db.session.add(meal)
                db.session.commit()

    def delete_csv(csv_file_path):
        #Used to delete meals from the database
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for meal in Meal.query.all():
                    if meal.name == row['\ufeffname']:
                        db.session.delete(meal)
                        db.session.commit()

    # for meal in Meal.query.all():
    #     print(meal)
    def delete_all_Subscriptions():
        for week in Subscription.query.all():
            db.session.delete(week)
            db.session.commit()

    def delete_all_Payment_Methods():
        for card in Payment_Methods.query.all():
            db.session.delete(card)
            db.session.commit()

    # Iterate through meals and update instructions and photo_URL if a matching PDF file is found
    def update_pdf_jpg_files(category):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the "static" folder in the same directory
        pdf_folder = os.path.join(script_dir, "static", category, "Instructions")
        # List all PDF files in the folder
        pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

        for meal in Meal.query.all():
            for pdf_file in pdf_files:
                if meal.name == os.path.splitext(pdf_file)[0]:
                    meal.instructions = "/static/"+category+"/Instructions/" + pdf_file

        pdf_folder = os.path.join(script_dir, "static", category, "Pictures")
    # List all PDF files in the folder
        jpg_files = [f for f in os.listdir(pdf_folder) if f.endswith(".jpg")]

    # Iterate through meals and update photo_URL if a matching PDF file is found
        for meal in Meal.query.all():
            for jpg_file in jpg_files:
                if meal.name == os.path.splitext(jpg_file)[0]:
                    meal.photo_URL = "/static/"+category+"/Pictures/" + jpg_file
        # Commit the changes to the database
        db.session.commit()
        print("\n\n\n")
    
    # read_csv(csv_file_path)
    # update_pdf_jpg_files("Seafood")

    print("\nUsers: ")
    print(User.query.all())

    print("\nMeals: ")
    print(Meal.query.all())

    print("\nSubscriptions: ")
    print(Subscription.query.all())

    print("\nPayment Methods: ")
    print(Payment_Methods.query.all())

    