from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import users
import courses
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
        print(f'session = {session}')
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
            'major_id': request.form.get('major'),
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
        if users.user_exists(user_data['username']):
            return jsonify({"error": "User already exists"}), 400

        # Add the new user to the database
        users.add_user(user_data)
        user = users.find_user_by_username(user_data['username'])
        session['username'] = user_data['username']
        session['student_id'] = user['id']
        session['next_semester_id'] = courses.get_next_semester()
        print(f"session['username'] = {session['username']}")
        return redirect('/')

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
        user = users.find_user_by_username(username)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check the password
        stored_password_hash = user['password']
        if bcrypt.check_password_hash(stored_password_hash, password):
            session['username'] = username
            session['student_id'] = user['id']
            session['next_semester_id'] = courses.get_next_semester()
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
        return jsonify({"error": f"An error occurred: {ex}"}), 500


@app.route('/login', methods=['GET'])
def login():
    if 'username' in session:
        return redirect('/')
    return render_template('login.html')


@app.route('/signup', methods=['GET'])
def signup():
    if 'username' in session:
        return redirect('/')
    majors = courses.get_majors()
    print(f'majors = {majors}')
    return render_template('signup.html', majors=majors)


# @app.route('/')
# @login_required
# def home():
#     return render_template('home.html', selected_nav_link='home')


@app.route('/course_search')
@login_required
def course_search():
    semester = courses.get_semester_details([session['next_semester_id']])[0]
    completed_credits = courses.get_completed_credits(session['next_semester_id'], session['student_id'])
    print(f'completed_credits = {completed_credits}')
    major = courses.get_major(session['student_id'])
    return render_template('course_search.html', semester=semester, completed_credits=completed_credits, major=major, selected_nav_link="course_search")


@app.route('/registered_courses')
@login_required
def registered_courses():
    registered_courses = courses.get_registered_courses(session['next_semester_id'], session['student_id'])
    semesters = courses.get_semester_details([session['next_semester_id'] - 1, session['next_semester_id']])
    print(f'semesters = {semesters}')
    return render_template('registered_courses.html', registered_courses=registered_courses, semesters=semesters, selected_nav_link='registered_courses')


@app.route('/search_courses')
@login_required
def search_courses():
    course_type = int(request.args.get('course_type'))
    major = int(request.args.get('major'))
    return courses.search_courses(session['next_semester_id'], session['student_id'], course_type, major)

    
@app.route('/register_for_course', methods=['POST'])
@login_required
def register_for_course():
    data = request.get_json()
    course_id = data.get('course_id')
    print(f'course_id = {course_id}')
    return courses.register_for_course(session['next_semester_id'], session['student_id'], course_id)


@app.route('/drop_course', methods=['POST'])
@login_required
def drop_course():
    data = request.get_json()
    course_id = data.get('course_id')
    return courses.drop_course(session['next_semester_id'], session['student_id'], course_id)


@app.route('/')
@login_required
def profile():
    user = users.find_user_by_username(session['username'])
    return render_template('profile.html', user=user, selected_nav_link="profile")


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        user_data = {
            'username': request.form.get('username'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'zip_code': request.form.get('zip_code')
        }

        if not user_data['username'] or not user_data['email']:
            return jsonify({"error": "Please provide username and email"}), 400

        # Add the new user to the database
        users.update_user(user_data)

        return redirect('/profile')

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


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # Check if user is logged in
    if 'username' in session and 'student_id' in session and 'next_semester_id' in session:
        session.pop('username', None)
        session.pop('student_id', None)
        session.pop('next_semester_id', None)
        return redirect('/login')
    else:
        return jsonify({"error": "No user is logged in"}), 400


if __name__ == '__main__':
    app.run(debug=True)
