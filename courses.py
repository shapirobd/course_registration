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


# get details on a list of semesters
def get_semester_details(semester_ids):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(f"SELECT id, season, year FROM semesters WHERE id IN ({
                   ','.join(map(str, semester_ids))}) ORDER BY id")
    semesters = cursor.fetchall()
    cursor.close()
    connection.close()
    return semesters


# get details on student's major
def get_major(student_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        f"SELECT m.* FROM majors m INNER JOIN students s ON m.id = s.major_id WHERE s.id = {student_id} LIMIT 1")
    major = cursor.fetchone()
    cursor.close()
    connection.close()
    return major


# get list of registered courses
def get_registered_courses(next_semester_id, student_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT c.*, s.season, s.year FROM courses c "
        "INNER JOIN student_courses stc ON c.id = stc.course_id "
        "INNER JOIN semesters s ON s.id = stc.semester_id "
        "WHERE stc.student_id=%(student_id)s AND s.id IN (%(next_semester_id)s - 1, %(next_semester_id)s)",
        {
            'student_id': student_id,
            'next_semester_id': next_semester_id})
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return courses


def get_completed_credits(next_semester_id, student_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # cursor.execute("SELECT sc.*, c.course_type FROM student_courses sc "
    #                "INNER JOIN courses c ON c.id = sc.course_id "
    #                "WHERE student_id = %(student_id)s", {'student_id': student_id})
    cursor.execute("SELECT c.id, c.course_type, sc.credits_earned AS credits FROM student_courses sc INNER JOIN courses c ON c.id = sc.course_id WHERE sc.student_id = %(student_id)s AND sc.semester_id < %(next_semester_id)s - 1 AND sc.credits_earned > 0 UNION "
                   "SELECT c.id, c.course_type, c.credits FROM student_courses sc INNER JOIN courses c ON c.id = sc.course_id WHERE student_id = %(student_id)s AND semester_id >= %(next_semester_id)s - 1", {'student_id': student_id, 'next_semester_id': next_semester_id})
    courses = cursor.fetchall()
    print(f'courses = {courses}')
    cursor.close()
    connection.close()
    completed_credits = [0, 0, 0]
    for course in courses:
        completed_credits[course['course_type'] - 1] += course['credits']
    return completed_credits


# get list of courses the student can sign up for
def search_courses(semester_id, student_id, course_type, major):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    print('\n')
    print(f'semester_id = {semester_id}')
    print(f'student_id = {student_id}')
    print(f'course_type = {course_type}')
    print(f'major = {major}')

    # GENERAL ELECGusAndPhoebe7292@@@fTIVES
    if course_type == 2:
        cursor.execute(
            f"""SELECT c.* FROM courses c
            WHERE c.course_type = {course_type}
             AND c.id NOT IN (
               SELECT course_id FROM student_courses sc WHERE sc.semester_id = {semester_id} AND sc.student_id = {student_id}
             )
             AND c.id NOT IN (
               SELECT course_id FROM student_courses sc
               WHERE sc.semester_id = {semester_id}
               GROUP BY sc.course_id
               HAVING COUNT(sc.id) >= 15
             )
             AND (c.prerequisite_course = 0 OR c.prerequisite_course IN (
                SELECT sc.id FROM student_courses sc WHERE sc.student_id = {student_id} AND sc.course_id = c.prerequisite_course AND (
                    sc.semester_id = {semester_id} - 1 OR (sc.semester_id < {semester_id} - 1 AND sc.credits_earned > 0)
                )
             ))
             """)
    # GENERAL EDUCATION
    elif course_type == 1:
        cursor.execute(
            f"""SELECT c.* FROM courses c
             WHERE c.course_type = {course_type} AND c.major IN ({major}, 0)
              AND c.id NOT IN (
                SELECT course_id FROM student_courses sc WHERE sc.semester_id = {semester_id} AND sc.student_id = {student_id}
              )
              AND c.id NOT IN (
                SELECT course_id FROM student_courses sc
                WHERE sc.semester_id = {semester_id}
                GROUP BY sc.course_id
                HAVING COUNT(sc.id) >= 15
              )
              AND (c.prerequisite_course = 0 OR c.prerequisite_course IN (
                SELECT sc.id FROM student_courses sc WHERE sc.student_id = {student_id} AND sc.course_id = c.prerequisite_course AND (
                    sc.semester_id = {semester_id} - 1 OR (sc.semester_id < {semester_id} - 1 AND sc.credits_earned > 0)
                )
              ))
              """)
    # MAJOR COURSEWORK
    else:
        cursor.execute(
            f"""SELECT c.* FROM students s
             INNER JOIN courses c ON c.major = s.major_id
             WHERE s.id = {student_id} AND c.course_type = {course_type}
              AND c.id NOT IN (
                SELECT course_id FROM student_courses sc WHERE sc.semester_id = {semester_id} AND sc.student_id = s.id
              )
              AND c.id NOT IN (
                SELECT course_id FROM student_courses sc
                WHERE sc.semester_id = {semester_id}
                GROUP BY sc.course_id
                HAVING COUNT(sc.id) >= 15
              )
              AND (c.prerequisite_course = 0 OR c.prerequisite_course IN (
                 SELECT sc.id FROM student_courses sc WHERE sc.student_id = {student_id} AND sc.course_id = c.prerequisite_course AND (
                     sc.semester_id = {semester_id} - 1 OR (sc.semester_id < {semester_id} - 1 AND sc.credits_earned > 0)
                 )
              ))
              """)
    courses = cursor.fetchall()
    print(f'courses = {courses}')
    cursor.close()
    connection.close()
    return courses


# register for a single course
def register_for_course(semester_id, student_id, course_id):
    course = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "INSERT INTO student_courses (student_id, course_id, semester_id) VALUES (%(student_id)s, %(course_id)s, %(semester_id)s)", {
                'student_id': student_id, 'course_id': course_id, 'semester_id': semester_id})
        connection.commit()

        cursor.execute(
            "SELECT * FROM courses WHERE id = %(course_id)s", {'course_id': course_id})
        course = cursor.fetchone()
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return f"Database error: {db_err}"
    finally:
        cursor.close()
        connection.close()
    return course


# drop a single course
def drop_course(semester_id, student_id, course_id):
    course = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM courses WHERE id = %(course_id)s", {'course_id': course_id})
        course = cursor.fetchone()

        cursor.execute(
            "DELETE FROM student_courses WHERE (student_id = %(student_id)s AND course_id = %(course_id)s AND semester_id = %(semester_id)s)", {
                'student_id': student_id, 'course_id': course_id, 'semester_id': semester_id})
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return f"Database error: {db_err}"
    finally:
        cursor.close()
        connection.close()
    return course


def get_majors():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, major_name FROM majors")
    majors = cursor.fetchall()
    cursor.close()
    connection.close()
    return majors
