from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/course_search')
def course_search():
    return render_template('course_search.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/signup')
def register():
    return render_template('signup.html')

@app.route('/registered_courses')
def registered_courses():
    return render_template('registered_courses.html')

@app.route('/logout')
def logout():
    return "logging out..."

if __name__ == '__main__':
    app.run(debug=True)