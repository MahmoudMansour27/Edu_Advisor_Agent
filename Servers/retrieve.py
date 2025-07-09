import mysql.connector

# Database connection
db_conn = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'edu_adv_db'
)

cursor = db_conn.cursor()

# -- 12. Attendance & Behavior Table
# CREATE TABLE AttendanceBehavior (
#     behavior_id SERIAL PRIMARY KEY,
#     student_id VARCHAR(10),
#     course_code VARCHAR(10),
#     attendance_percent INT,
#     behavior_notes TEXT,
#     FOREIGN KEY (student_id) REFERENCES StudentProfile(student_id),
#     FOREIGN KEY (course_code) REFERENCES CourseCatalog(course_code)
# );


# student_id = 'S1000'
# columns = [
#     'behavior_id',
#     'student_id',
#     'course_code',
#     'attendance_percent',
#     'behavior_notes'
# ]
# sql = f"SELECT * FROM AcademicRecords WHERE student_id = '{student_id}'"
# cursor.execute(sql)
# result = cursor.fetchall()
# print(result)
# print(type(result))

print(' std1000     '.strip().upper())

