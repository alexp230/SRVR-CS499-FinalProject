import pymysql
# from main import db, app, User, Meal, Payment_Methods, Subscription, Box
import os
import csv


csv_file_path = os.path.join(os.path.dirname(__file__), 'CSV_File', 'meal_data.csv')

# Database connection parameters. Connects to srvr_db in Amazon RDS. (DO NOT TOUCH!!!)
def connect_to_database():
    host = 'srvr-db.cuwkkpw7lnan.us-east-2.rds.amazonaws.com'
    user = 'admin'
    password = 'srvradmin'
    database = 'srvr_db'

    # Connect to MySQL
    conn = pymysql.connect(
        host=host, 
        user=user, 
        password=password, 
        database=database
    )

    return conn

# Create a table if it does not already exist. 
def create_tables(cursor):
    create_userTable_query = '''
    CREATE TABLE IF NOT EXISTS userTable (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        address TEXT NOT NULL
    )
    '''
    create_mealTable_query = '''
    CREATE TABLE IF NOT EXISTS mealTable (
        meal_id INT AUTO_INCREMENT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        photo_URL TEXT NOT NULL,
        instructions TEXT NOT NULL,
        allergens TEXT NOT NULL 
    )
    '''

    # create_boxTable_query = '''
    # CREATE TABLE IF NOT EXISTS boxTable (
    #     box_id INT AUTO_INCREMENT PRIMARY KEY,
    #     user_id INT,
    #     ordered_meals TEXT NOT NULL,
        # FOREIGN KEY (user_id) 
        # REFERENCES userTable(user_id)
    # )
    # '''

    create_pymntTable_query = '''
    CREATE TABLE IF NOT EXISTS pymntTable (
        card_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        card_number TEXT NOT NULL,
        card_holder_name TEXT NOT NULL,
        card_exp_date TEXT NOT NULL,
        card_CCV TEXT NOT NULL,
        FOREIGN KEY (user_id) 
        REFERENCES userTable(user_id)
    )
    '''
    
    # create_pastOrdersTable_query = '''
    # CREATE TABLE IF NOT EXISTS pastOrdersTable (
    #     transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    #     user_id INT,
    #     box_id INT,
    #     payment_method TEXT NOT NULL,
    #     shipping_address TEXT NOT NULL,
    #     subscription_type TEXT NOT NULL,
    #     order_date TEXT NOT NULL,
    #     order_time TEXT NOT NULL,
    #     FOREIGN KEY (user_id) 
        # REFERENCES userTable(user_id)
        # FOREIGN KEY (box_id) 
        # REFERENCES boxTable(box_id)
    # )
    # '''

    # create_subscriptionTable_query = '''
    # CREATE TABLE IF NOT EXISTS subscriptionTable (
    #     sub_id INT AUTO_INCREMENT PRIMARY KEY,
    #     user_id INT,
    #     delivery_day TEXT NOT NULL,
    #     house_size TEXT NOT NULL,
    #     FOREIGN KEY (user_id) 
        # REFERENCES userTable(user_id)
    # )
    # '''

    cursor.execute(create_userTable_query)
    cursor.execute(create_mealTable_query)
    # cursor.execute(create_boxTable_query)
    cursor.execute(create_pymntTable_query)
    # cursor.execute(create_pastOrdersTable_query)
    # cursor.execute(create_subscriptionTable_query)

# Delete a specfied table by table_name 
def delete_table(cursor, table_name):
    delete_table_query = f'DROP TABLE IF EXISTS {table_name}'
    cursor.execute(delete_table_query)

# Insert data into specified table by table_name.
def insert_data(cursor, data, table_name):
    if table_name == "userTable":
        schema = "(firstname, lastname, email, password, address)"
        valueformat = "(%s, %s, %s, %s, %s)"
    elif table_name == "mealTable":
        schema = "(name, category, photo_URL, instructions, allergens)"
        valueformat = "(%s, %s, %s, %s, %s)"
    elif table_name == "boxTable":
        schema = "(ordered_meals)"
        valueformat = "(%s)"
    elif table_name == "pymntTable":
        schema = "(card_number, card_holder_name, card_exp_date, card_CCV)"
        valueformat = "(%s, %s, %s, %s)"
    elif table_name == "pastOrdersTable":
        schema = "(payment_method, shipping_address, subscription_type, order_date, order_time)"
        valueformat = "(%s, %s, %s, %s, %s)"
    elif table_name == "subscriptionTable":
        schema = "(delivery_day, house_size)"
        valueformat = "(%s, %s)"
    else:
        print("Please check your data to make sure it has the correct table name")

    insert_query = "INSERT INTO "+table_name+" "+schema+" VALUES "+valueformat+""
    cursor.execute(insert_query, data)

# Select all data from specified table by table_name.
def select_data(cursor, table_name):
    select_query = f"SELECT * FROM {table_name}"
    cursor.execute(select_query)
    return cursor.fetchall()

def select_specific_data(cursor, table_name, match_column_name, match_val):
    select_query = f"SELECT * FROM {table_name} WHERE "+match_column_name+"=%s LIMIT 1"
    cursor.execute(select_query, (match_val))
    return cursor.fetchall()

# Updates column(s) in a specified table by table_name. update_data1() modifies 1 column only, update_data5() updates 5 columns (max amount for our purposes) etc...
# mod_column_name is the name of the column as it shows in database (ie. to change firstname from John to Jane; mod_column_name = "firstname").
# mod_val is the value you are updating the existing value to (ie. to change firstname from John to Jane; mod_val = "Jane").
# match_column_name is the name of the column as it shows is database that is used to identify which record you want to look for (ie. to change firstname from John to Jane; match_column_name = "firstname").
# match_val is the value existing value you wish to modify (ie. to change firstname from John to Jane; match_val = "John").
def update_data1(cursor, table_name, mod_colum_name, mod_val, match_colum_name, match_val):
    # Update one column of data
    update_query = "UPDATE "+table_name+" SET "+mod_colum_name+"=%s WHERE "+match_colum_name+"=%s"
    cursor.execute(update_query, (mod_val, match_val))

def update_data2(cursor, table_name, mod_colum_name1, mod_val1, mod_colum_name2, mod_val2, match_colum_name, match_val):
    # Update one column of data
    update_query = "UPDATE "+table_name+" SET "+mod_colum_name1+"=%s, "+mod_colum_name2+"=%s WHERE "+match_colum_name+"=%s"
    cursor.execute(update_query, (mod_val1, mod_val2, match_val))

def update_data3(cursor, table_name, mod_colum_name1, mod_val1, mod_colum_name2, mod_val2, mod_colum_name3, mod_val3, match_colum_name, match_val):
    # Update one column of data
    update_query = "UPDATE "+table_name+" SET "+mod_colum_name1+"=%s, "+mod_colum_name2+"=%s, "+mod_colum_name3+"=%s WHERE "+match_colum_name+"=%s"
    cursor.execute(update_query, (mod_val1, mod_val2, mod_val3, match_val))

def update_data4(cursor, table_name, mod_colum_name1, mod_val1, mod_colum_name2, mod_val2, mod_colum_name3, mod_val3, mod_colum_name4, mod_val4, match_colum_name, match_val):
    # Update one column of data
    update_query = "UPDATE "+table_name+" SET "+mod_colum_name1+"=%s, "+mod_colum_name2+"=%s, "+mod_colum_name3+"=%s, "+mod_colum_name4+"=%s WHERE "+match_colum_name+"=%s"
    cursor.execute(update_query, (mod_val1, mod_val2, mod_val3, mod_val4, match_val))

def update_data5(cursor, table_name, mod_colum_name1, mod_val1, mod_colum_name2, mod_val2, mod_colum_name3, mod_val3, mod_colum_name4, mod_val4, mod_colum_name5, mod_val5, match_colum_name, match_val):
    # Update one column of data
    update_query = "UPDATE "+table_name+" SET "+mod_colum_name1+"=%s, "+mod_colum_name2+"=%s, "+mod_colum_name3+"=%s, "+mod_colum_name4+"=%s, "+mod_colum_name5+"=%s WHERE "+match_colum_name+"=%s"
    cursor.execute(update_query, (mod_val1, mod_val2, mod_val3, mod_val4, mod_val5, match_val))

# Deletes a record from a specified table by table_name.
# match_column_name is the name of the column as it shows is database that is used to identify which record you want to delete (ie. to delete John's record; match_column_name = "firstname").
# match_val is the value used to loacate the specific record to delete (ie. to delete John's record; match_val = "John").
def delete_data(cursor, table_name, match_column_name, match_val):
    # Delete data
    delete_query = "DELETE FROM "+table_name+" WHERE "+match_column_name+"=%s"
    cursor.execute(delete_query, (match_val,))

def add_meal_to_database(csv_file_path):
    # Connect to the database
    conn = connect_to_database()

    try:
        # Create a cursor
        cursor = conn.cursor()

        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            # Used to add meals to the database
            for row in reader:
                # Check if the meal already exists by name
                select_query = "SELECT * FROM mealTable WHERE name = %s"
                cursor.execute(select_query, (row['Name'],))
                existing_meal = cursor.fetchone()

                if existing_meal:
                    continue
                else:
                    name = row['Name']
                    category = row['Category']
                    # Insert the meal into the database
                    insert_query = "INSERT INTO mealTable (name, category, photo_URL, instructions, allergens) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(insert_query, (name, category, 'NULL', 'NULL', 'NULL'))
                    conn.commit()

    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

def print_all_rows():
    # Connect to the database
    conn = connect_to_database()

    try:
        # Create a cursor
        cursor = conn.cursor()

        # Query to select all rows from the table
        select_query = "SELECT * FROM mealTable"

        # Execute the query
        cursor.execute(select_query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Print all rows
        for row in rows:
            print(row)

    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()
def update_pdf_jpg_files():
    # Connect to the database
    conn = connect_to_database()

    try:
        # Create a cursor
        cursor = conn.cursor()

        # Fetch meal files information
        meal_files = {}
        script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        junk_files = [".DS_Store", "images", "js", "styles.css"]

        for category in os.listdir(script_dir):
            if category in junk_files:
                continue

            pdf_folder_path = os.path.join(script_dir, category, 'Instructions')
            for file in os.listdir(pdf_folder_path):
                if file.endswith(".pdf"):
                    meal_files[(file.replace(".pdf", ""))] = category
        for meal in meal_files:
            meal_name = meal   
            photo_URL = "/static/" + meal_files[meal_name] + "/Pictures/" + meal_name + ".jpg"   
            instructions = "/static/" + meal_files[meal_name] + "/Instructions/" + meal_name + ".pdf" 
            update_data3(cursor, "mealTable", "photo_URL", photo_URL, "instructions", instructions, "allergens", "NULL", "name", meal)
        # Update meals in the database based on files found in directories
        
        # Commit the changes to the database
        conn.commit()

    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

def fetch_all_rows(table_name):
    # Connect to the database
    conn = connect_to_database()

    try:
        # Create a cursor
        cursor = conn.cursor()

        # Query to select all rows from the specified table
        select_query = f"SELECT * FROM {table_name}"

        # Execute the query
        cursor.execute(select_query)

        # Fetch all rows
        rows = cursor.fetchall()

        return rows  # Return the rows fetched from the table as a list of tuples

    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

def main():
    conn = connect_to_database()
    try:
        # Create a cursor
        cursor = conn.cursor()

        # # Delete table if exists. (Testing Purposes)
        # # To delete a table with a key that is referenced by others as a foreign key, you must delete the table with the foreign key first, 
        # # then delete the table that it references to.
        # delete_table(cursor, "userTable")
        # print("Tables deleted.\n")

        # Create table if not exists
        create_tables(cursor)
        print("Tables created.\n")
        add_meal_to_database(csv_file_path)
        update_pdf_jpg_files()
        # print_all_rows()
        result = fetch_all_rows("mealTable")

        print("ID: [0][0]")
        print(result[0][0])
        print("\nName: [0][1]")
        print(result[0][1])
        print("\nCategory: [0][2]")
        print(result[0][2])
        print("\nPicture: [0][3]")
        print(result[0][3])
        print("\nInstructions: [0][4]")
        print(result[0][4])
        print("\nAllergens: [0][5]")
        print(result[0][5])
        # # Insert data into userTable(firstname, lastname, email, password, address)
        # schema = "(firstname, lastname, email, password, address)"
        # valueformat = "(%s, %s, %s, %s, %s)"
        # user_data_to_insert = [('Josh', 'Patton', 'jpatt@uab.edu', 'password1', '555 Main St, Birmingham AL'), 
        #                        ('Alex', 'Pruit', 'alexp@uab.edu', 'password2', '556 Main St, Birmingham AL'), 
        #                        ('Obie', 'Carnathan', 'obiec@uab.edu', 'password3', '557 Main St, Birmingham AL')]
        # insert_data(cursor, user_data_to_insert, "userTable")
        # conn.commit()

        # # Insert data into pymntTable(card_number, card_holder_name, card_exp_date, card_CCV)
        # pymnt_data_to_insert = [('1111222233334444', 'Josh Patton', '12/30', '222'), 
        #                         ('2222444466668888', 'Alex Pruit', '3/30', '333'), 
        #                         ('9999888877776666', 'Obie Carnathan', '4/28', '444')]
        # insert_data(cursor, pymnt_data_to_insert, "pymntTable")
        # conn.commit()

        # Select all data from userTable
        # rows = select_data(cursor, "userTable")
        # rows = select_specific_data(cursor, "userTable", "email", "alexp@uab.edu")
        # print("Data in userTable:")
        # for row in rows:
        #     print(row)

        # # # Select all data from pymntTable
        # # rows = select_data(cursor, "pymntTable")
        # # print("Data in pymntTable:")
        # # for row in rows:
        # #     print(row)

        # # # Updating records in userTable from just 1 column (update_data1) to all 5 columns (update_data5).
        # # update_data1(cursor, "userTable", "firstname", "Jack", "email", "jpatt@uab.edu")
        # # update_data2(cursor, "userTable", "firstname", "James", "lastname", "Smith", "email", "jpatt@uab.edu")
        # update_data3(cursor, "userTable", "firstname", "Jack", "lastname", "Frost", "address", "111 2nd Ave N, Birmingham AL", "email", "jpatt@uab.edu")
        # # update_data4(cursor, "userTable", "firstname", "James", "lastname", "Smith", "address", "333 6th Ave N, Birmingham AL", "password", "newpassword", "email", "jpatt@uab.edu")
        # # update_data5(cursor, "userTable", "firstname", "Jack", "lastname", "Frost", "address", "111 2nd Ave N, Birmingham AL", "password", "newnewpass", "email", "jfrost@uab.edu", "email", "jpatt@uab.edu")
        # conn.commit()

        # # # Select data after update
        # updated_rows = select_data(cursor, "userTable")
        # print("\nData in userTable after update:")
        # for row in updated_rows:
        #     print(row)

        # # # Delete data
        # delete_data(cursor, "userTable", "firstname", "Jack")
        # conn.commit()

        # # Select data after delete
        # remaining_rows = select_data(cursor, "userTable")
        # print("\nData in userTable after delete:")
        # for row in remaining_rows:
        #     print(row)

    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()