from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from users import user_exists, add_user, find_user_by_username
import os
from dotenv import load_dotenv
import mysql.connector

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configurations using environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')  # Fall back to a default value if not set
app.config['SESSION_TYPE'] = 'filesystem'  # Still using filesystem for session storage
bcrypt = Bcrypt(app)

# Decorator to check if user is logged in
def login_required(f):
    def wrap(*args, **kwargs):
        if 'username' not in session:
            print('REDIRECTING!')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap


# Route for user signup
@app.route('/signup', methods=['POST'])
def doSignup():
    try:
        user_data = {
            'username': request.form.get('username'),
            'password': bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'zip_code': request.form.get('zip_code')
        }

        if not user_data['username'] or not user_data['email'] or not user_data['password']:
            return jsonify({"error": "Please provide username, email, and password"}), 400

        # Check if user already exists
        if user_exists(user_data['username']):
            return jsonify({"error": "User already exists"}), 400

        # Hash the password
        # hashed_password = generate_password_hash(password, method='sha256')

        # Add the new user to the database
        add_user(user_data)
        session['username'] = user_data['username']
        return redirect('/')
        # return jsonify({"message": "User created successfully"}), 201

    except mysql.connector.Error as db_err:
        # Handle specific database errors
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database connection error"}), 500
    
    except KeyError as key_err:
        # Handle missing data in the request JSON
        print(f"Key error: {key_err}")
        return jsonify({"error": f"Missing key: {str(key_err)}"}), 400
    
    except Exception as ex:
        # Catch all other exceptions
        print(f"An error occurred: {ex}")
        return jsonify({"error": "An unexpected error occurred"}), 500


# Route for user login
@app.route('/login', methods=['POST'])
def doLogin():
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({"error": "Please provide username and password"}), 400

        # Find the user by username
        user = find_user_by_username(username)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check the password
        stored_password_hash = user[2]
        if bcrypt.check_password_hash(stored_password_hash, password):
            session['username'] = username
            return redirect('/')
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except mysql.connector.Error as db_err:
        # Handle specific database errors
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database connection error"}), 500

    except KeyError as key_err:
        # Handle missing data in the request JSON
        print(f"Key error: {key_err}")
        return jsonify({"error": f"Missing key: {str(key_err)}"}), 400

    except Exception as ex:
        # Catch all other exceptions
        print(f"An error occurred: {ex}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route('/login', methods=['GET'])
def login():
    if 'username' in session:
        return redirect('/')
    return render_template('login.html')


@app.route('/signup', methods=['GET'])
def signup():
    if 'username' in session:
        return redirect('/')
    return render_template('signup.html')


@app.route('/')
@login_required
def home():
    return render_template('home.html')


@app.route('/course_search')
@login_required
def course_search():
    return render_template('course_search.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/registered_courses')
@login_required
def registered_courses():
    return render_template('registered_courses.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # Check if user is logged in
    if 'username' in session:
        session.pop('username', None)
        return redirect('/login')
        # return jsonify({"message": "Logout successful"}), 200
    else:
        return jsonify({"error": "No user is logged in"}), 400


if __name__ == '__main__':
    app.run(debug=True)