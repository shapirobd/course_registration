import mysql.connector
from mysql.connector import errorcode
from db import db_config, get_db_connection

# get list of registered courses
def get_next_semester():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM semesters "
                   "WHERE start_date > NOW() ORDER BY start_date LIMIT 1")
    semester = cursor.fetchone()
    cursor.close()
    connection.close()
    return semester[0]

# get list of registered courses
def get_registered_courses(semester_id, student_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT sc.* FROM student_courses stc "
                   "INNER JOIN semester_courses smc ON stc.course_id = smc.course_id"
                   "WHERE stc.student_id=%(student_id)s AND smc.semester_id = %(semester_id)s", {'student_id': student_id, 'semester_id': semester_id})
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return courses

# get list of courses the student can sign up for
def search_courses(semester_id, student_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(f"""SELECT c.* FROM students s 
                   INNER JOIN courses c ON c.major_id = s.major_id 
                   WHERE s.id = {student_id} 
                    AND c.id NOT IN (
                      SELECT course_id FROM student_courses sc WHERE sc.semester_id = {semester_id} AND sc.student_id = s.id
                    )
                    AND c.id NOT IN (
                      SELECT course_id FROM student_courses sc
                      WHERE sc.semester_id = {semester_id}
                      GROUP BY sc.course_id
                      HAVING COUNT(sc.id) >= 15
                    )""")
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return courses

# register for a single course
def register_for_course(semester_id, student_id, course_id):
    try:
      connection = get_db_connection()
      cursor = connection.cursor()
      cursor.execute("INSERT INTO student_courses (student_id, course_id, semester_id) VALUES (%(student_id)s, %(course_id)s, %(semester_id)s)", 
                     {'student_id': student_id, 'course_id': course_id, 'semester_id': semester_id})
      connection.commit()
      cursor.close()
      connection.close()
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return f"Database error: {db_err}"
    finally:
        cursor.close()
        connection.close()
    return "Success!"


# drop a single course
def drop_course(semester_id, student_id, course_id):
    try:
      connection = get_db_connection()
      cursor = connection.cursor()
      cursor.execute("DELETE FROM student_courses WHERE (student_id = %(student_id)s AND course_id = %(course_id)s AND semester_id = %(semester_id)s)", 
                     {'student_id': student_id, 'course_id': course_id, 'semester_id': semester_id})
      connection.commit()
      cursor.close()
      connection.close()
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return f"Database error: {db_err}"
    finally:
        cursor.close()
        connection.close()
    return "Success!"