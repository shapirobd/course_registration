import mysql.connector
from mysql.connector import errorcode
from db import db_config, get_db_connection

# Check if user exists
def user_exists(username):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students WHERE username=%(username)s", {'username': username})
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user is not None

# Add a new user
def add_user(data):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        print(f'username = {data['username']}')
        print(f'password = {data['password']}')
        print(f'first_name = {data['first_name']}')
        print(f'last_name = {data['last_name']}')
        print(f'major = {data['major_id']}')
        print(f'email = {data['email']}')
        print(f'phone = {data['phone']}')
        print(f'address = {data['address']}')
        print(f'city = {data['city']}')
        print(f'state = {data['state']}')
        print(f'zip_code = {data['zip_code']}')
        
        cursor.execute(
            "INSERT INTO students (major_id, username, password, first_name, last_name, email, phone, address, city, state, zip_code) "
            "VALUES (%(major_id)s, %(username)s, %(password)s, %(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(address)s, %(city)s, %(state)s, %(zip_code)s)",
            data
        )
        connection.commit()
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
    finally:
        cursor.close()
        connection.close()


# Find a user by username
def find_user_by_username(username):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE username=%(username)s", {'username': username})
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user