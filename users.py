import mysql.connector
from mysql.connector import errorcode
from db import db_config, get_db_connection


# Check if user exists
def user_exists(username):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM students WHERE username=%(username)s", {'username': username})
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user is not None


# Add a new user
def add_user(data):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (major_id, username, password, first_name, last_name, email, phone, address, city, state, zip_code) "
            "VALUES (%(major_id)s, %(username)s, %(password)s, %(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(address)s, %(city)s, %(state)s, %(zip_code)s)",
            data)
        connection.commit()
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
    finally:
        cursor.close()
        connection.close()


# Update an existing user
def update_user(data):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE students SET "
            "first_name = %(first_name)s, "
            "last_name = %(last_name)s, "
            "email = %(email)s, "
            "phone = %(phone)s, "
            "address = %(address)s, "
            "city = %(city)s, "
            "state = %(state)s, "
            "zip_code = %(zip_code)s "
            "WHERE username = %(username)s",
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
    cursor.execute(
        "SELECT * FROM students WHERE username=%(username)s", {'username': username})
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user
