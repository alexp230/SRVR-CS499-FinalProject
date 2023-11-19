import pymysql

def connect_to_database():
    # Database connection parameters
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

def create_tables(cursor):
    # Create a table
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
    # create_mealTable_query = '''
    # CREATE TABLE IF NOT EXISTS mealTable (
    #     meal_id INT AUTO_INCREMENT PRIMARY KEY,
    #     user_id INT,
    #     name TEXT NOT NULL,
    #     category TEXT NOT NULL,
    #     photo_URL TEXT NOT NULL,
    #     instructions TEXT NOT NULL,
    #     allergens TEXT NOT NULL, 
        # FOREIGN KEY (user_id) 
        # REFERENCES userTable(user_id)
    # )
    # '''

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
    # cursor.execute(create_mealTable_query)
    # cursor.execute(create_boxTable_query)
    cursor.execute(create_pymntTable_query)
    # cursor.execute(create_pastOrdersTable_query)
    # cursor.execute(create_subscriptionTable_query)

def delete_table(cursor, table_name):
    # Delete a table
    delete_table_query = f'DROP TABLE IF EXISTS {table_name}'
    cursor.execute(delete_table_query)

def insert_data(cursor, data, table_name):
    # Insert data
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
    cursor.executemany(insert_query, data)

def select_data(cursor, table_name):
    # Select data
    select_query = f"SELECT * FROM {table_name}"
    cursor.execute(select_query)
    return cursor.fetchall()

def update_data(cursor, new_age, target_name, table_name):
    # Update data
    update_query = "UPDATE userTable SET age=%s WHERE name=%s"
    cursor.execute(update_query, (new_age, target_name))

def delete_data(cursor, target_name, table_name):
    # Delete data
    delete_query = "DELETE FROM userTable WHERE name=%s"
    cursor.execute(delete_query, (target_name,))

def main():
    conn = connect_to_database()
    try:
        # Create a cursor
        cursor = conn.cursor()

        # Delete table if exists. (Testing Purposes)
        # delete_table(cursor, "userTable")
        # print("Tables deleted.\n")

        # Create table if not exists
        create_tables(cursor)
        print("Tables created.\n")
        
        # Insert data userTable(firstname, lastname, email, password, address)
        schema = "(firstname, lastname, email, password, address)"
        valueformat = "(%s, %s, %s, %s, %s)"
        user_data_to_insert = [('Josh', 'Patton', 'jpatt@uab.edu', 'password1', '555 Main St, Birmingham AL'), 
                               ('Alex', 'Pruit', 'alexp@uab.edu', 'password2', '556 Main St, Birmingham AL'), 
                               ('Obie', 'Carnathan', 'obiec@uab.edu', 'password3', '557 Main St, Birmingham AL')]
        insert_data(cursor, user_data_to_insert, "userTable")
        conn.commit()

        # Insert data pymntTable(card_number, card_holder_name, card_exp_date, card_CCV)
        pymnt_data_to_insert = [('1111222233334444', 'Josh Patton', '12/30', '222'), 
                                ('2222444466668888', 'Alex Pruit', '3/30', '333'), 
                                ('9999888877776666', 'Obie Carnathan', '4/28', '444')]
        insert_data(cursor, pymnt_data_to_insert, "pymntTable")
        conn.commit()

        # Select data
        rows = select_data(cursor, "userTable")
        print("Data in userTable:")
        for row in rows:
            print(row)

        rows = select_data(cursor, "pymntTable")
        print("Data in pymntTable:")
        for row in rows:
            print(row)

        # # Update data
        # update_data(cursor, 28, 'Jack')
        # conn.commit()

        # # Select data after update
        # updated_rows = select_data(cursor)
        # print("\nData in userTable after update:")
        # for row in updated_rows:
        #     print(row)

        # # Delete data
        # delete_data(cursor, 'Bobby')
        # conn.commit()

        # # Select data after delete
        # remaining_rows = select_data(cursor)
        # print("\nData in userTable after delete:")
        # for row in remaining_rows:
        #     print(row)

    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()