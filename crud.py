"""
This file is used to create, read, update, and delete data from the database for testing purposes.
It is not used in the final version of the project.
"""
from main import db, app, User, Meal, Payment_Methods, Subscription, Box
import os
import csv


with app.app_context():

    def pdf_names_to_csv():
        script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

        pdf_files = {}

        junk_files = [".DS_Store", "images", "js", "styles.css"]
        for category in os.listdir(script_dir):

            if (category in junk_files):
                continue

            pdf_folder_path = os.path.join(script_dir, category, 'Instructions')
            csv_file_path = os.path.join(os.path.dirname(__file__), 'CSV_File', 'meal_data.csv')

            for file in os.listdir(pdf_folder_path):
                if (file.endswith(".pdf")):
                    pdf_files[(file.replace(".pdf", ""))] = category


        # Open the CSV file in append mode to add data
        ignore = []
        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            # Check if the CSV file already contains the PDF filenames
            for row in reader:
                meal_name = row['Name']
                if meal_name in pdf_files:
                    ignore.append(meal_name)

        csvfile.close()

        with open(csv_file_path, 'a', newline='', encoding='utf-8-sig') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write each PDF filename to a new row in the CSV file
            for name, category in pdf_files.items():
                if name in ignore:
                    continue
                else:
                    csv_writer.writerow([name, category])
        csvfile.close()
        # Construct the path to the "static" folder in the same directory


    def add_meal_to_database(csv_file_path):
        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            #Used to add meals to the database
            for row in reader:
                if Meal.query.filter_by(name=row['Name']).first() is not None:
                    continue
                else:
                    name = row['Name']
                    meal = Meal(name=name, category=row['category'], photo_URL="NULL", instructions="NULL", allergens="NULL")
                    db.session.add(meal)
                    db.session.commit()


    def delete_csv(csv_file_path):
        #Used to delete meals from the database
        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for meal in Meal.query.all():
                    if meal.name == row['Name']:
                        db.session.delete(meal)
                        db.session.commit()

    
    def delete_all_Subscriptions():
        for week in Subscription.query.all():
            db.session.delete(week)
            db.session.commit()

    def delete_all_Payment_Methods():
        for card in Payment_Methods.query.all():
            db.session.delete(card)
            db.session.commit()

    def delete_all_Boxes():
        for box in Box.query.all():
            db.session.delete(box)
            db.session.commit()
    
    def delete_all_Meals():
        for meal in Meal.query.all():
            db.session.delete(meal)
            db.session.commit()

    # Iterate through meals and update instructions and photo_URL if a matching PDF file is found
    # category parameter is used to specify the folder to search in
    # picture_extension parameter is used to specify the file extension to search for
    def update_pdf_jpg_files(): # category is a string
        
        script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

        meal_files = {}

        junk_files = [".DS_Store", "images", "js", "styles.css"]
        for category in os.listdir(script_dir):

            if (category in junk_files):
                continue
        
            pdf_folder_path = os.path.join(script_dir, category, 'Instructions')

            for file in os.listdir(pdf_folder_path):
                if (file.endswith(".pdf")):
                    meal_files[(file.replace(".pdf", ""))] = category

        # # Get the directory of the current script
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # # Construct the path to the "static" folder in the same directory
        # pdf_folder = os.path.join(script_dir, "static", category, "Instructions")
        # # List all PDF files in the folder
        # pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

        # Iterate through meals and update instructions if a matching PDF file is found
        for meal in Meal.query.all():
            meal_name = meal.name
            if meal_name in meal_files:
                meal.instructions = "/static/" + meal_files[meal_name] + "/Instructions/" + meal_name + ".pdf"
                meal.photo_URL = "/static/" + meal_files[meal_name] + "/Pictures/" + meal_name + ".jpg"

        db.session.commit()

        # picture_folder = os.path.join(script_dir, "static", value, "Pictures")
        # picture_files = [f for f in os.listdir(picture_folder) if f.endswith(picture_extension)] #

        # # Iterate through meals and update photo_URL if a matching PDF file is found
        # for meal in Meal.query.all():
        #     for picture in picture_files:
        #         if meal.name == os.path.splitext(picture)[0]:
        #             meal.photo_URL = "/static/"+category+"/Pictures/" + picture
        # # Commit the changes to the database
        # db.session.commit()



    csv_file_path = os.path.join(os.path.dirname(__file__), 'CSV_File', 'meal_data.csv')

    #change row[uffef] to row[1]
    def update_database():  
        pdf_names_to_csv()

        add_meal_to_database(csv_file_path)

        update_pdf_jpg_files()

    # update_database()

    meal = Meal.query.filter_by(name="Chicken Parmesan").first()
    meal.name = "Cajun_Baked_Catfish"
    db.session.commit()


