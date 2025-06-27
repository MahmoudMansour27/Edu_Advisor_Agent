import pandas as pd
import numpy as np
import random
from faker import Faker
import mysql.connector


# Initialize Faker for generating random data
fake = Faker()

# Helper values
departments = ['Computer Science', 'Business', 'Engineering', 'Pharmacy', 'Dentistry']
majors = ['Software Engineering', 'Marketing', 'Mechanical Engineering', 'Clinical Pharmacy', 'Dental Surgery']
courses = [
    {'code': 'CS101', 'name': 'Intro to Programming', 'credits': 3, 'dept': 'Computer Science'},
    {'code': 'CS101', 'name': 'Software Engineering', 'credits': 3, 'dept': 'Computer Science'},
    {'code': 'CS101', 'name': 'Information Security', 'credits': 3, 'dept': 'Computer Science'},
    {'code': 'CS101', 'name': 'Data Science', 'credits': 3, 'dept': 'Computer Science'},
    {'code': 'CS101', 'name': 'Database Systems', 'credits': 3, 'dept': 'Computer Science'},
    {'code': 'CS101', 'name': 'Operating Systems', 'credits': 3, 'dept': 'Computer Science'},
    {'code': 'CS101', 'name': 'Pattern Recognition', 'credits': 3, 'dept': 'Computer Science'},
    {'code': 'BUS201', 'name': 'Marketing Principles', 'credits': 3, 'dept': 'Business'},
    {'code': 'ENG301', 'name': 'Thermodynamics', 'credits': 4, 'dept': 'Engineering'},
    {'code': 'PHA110', 'name': 'Pharmacology Basics', 'credits': 3, 'dept': 'Pharmacy'},
    {'code': 'DEN220', 'name': 'Dental Anatomy', 'credits': 3, 'dept': 'Dentistry'}
]

# 1. Student Profile Table
students = [{
    'student_id': f"S{1000+i}",
    'name': fake.name(),
    'birthdate': fake.date_of_birth(minimum_age=18, maximum_age=25),
    'nationality': fake.country(),
    'contact': fake.phone_number(),
    'enrollment_date': fake.date_between(start_date='-3y', end_date='today'),
    'major': random.choice(majors),
    'advisor': fake.name(),
    'status': random.choice(['active', 'graduated', 'suspended'])
} for i in range(100)]


# 2. Academic Records Table
grades = ['A', 'B+', 'B', 'C+', 'C', 'D', 'F']
academic_records = [{
    'student_id': student['student_id'],
    'course_code': course['code'],
    'course_name': course['name'],
    'semester': f"{random.choice(['Fall', 'Spring'])} {random.choice([2022, 2023, 2024])}",
    'grade': random.choice(grades),
    'credits': course['credits'],
    'GPA': round(random.uniform(2.0, 4.0), 2)
} for student in students for course in random.sample(courses, 3)]

# 3. Course Catalog Table
# df_courses = pd.DataFrame(courses)

# 4. Enrollment Table
enrollment = [{
    'student_id': student['student_id'],
    'course_code': course['code'],
    'semester': f"Fall {2024}",
    'enrollment_status': random.choice(['Enrolled', 'Dropped', 'Withdrawn']),
    'attendance_percent': random.randint(50, 100)
} for student in students for course in random.sample(courses, 2)]

# 5. Advising Notes Table
advising_notes = [{
    'student_id': student['student_id'],
    'advisor_id': f"A{random.randint(1,5)}",
    'date': fake.date_this_year(),
    'meeting_summary': fake.sentence(),
    'recommendations': fake.sentence(),
    'follow_up_date': fake.date_this_year()
} for student in students]

# 6. Academic Calendar Table
academic_calendar = [{
    'semester': f"{term} {year}",
    'start_date': f"{year}-09-01" if term == 'Fall' else f"{year}-02-01",
    'end_date': f"{year}-12-20" if term == 'Fall' else f"{year}-06-01",
    'registration_deadline': f"{year}-08-20" if term == 'Fall' else f"{year}-01-20",
    'exam_period': f"{year}-12-05 to {year}-12-20" if term == 'Fall' else f"{year}-05-15 to {year}-06-01"
} for term in ['Fall', 'Spring'] for year in [2024, 2025]]


# 7. Department and Faculty Table
department_faculty = [{
    'department_id': f"D{i+1}",
    'name': departments[i],
    'contact_info': fake.email(),
    'faculty_members': ', '.join([fake.name() for _ in range(3)]),
    'office_hours': f"{random.randint(9,11)}AM - {random.randint(2,5)}PM"
} for i in range(len(departments))]

# 8. Graduation Requirements Table
graduation_requirements = [{
    'major': major,
    'required_credits': 132,
    'core_courses': ', '.join([course['code'] for course in random.sample(courses, 2)]),
    'electives': ', '.join([course['code'] for course in random.sample(courses, 2)]),
    'capstone_project': f"{major} Capstone"
} for major in majors]


# 9. Internships & Opportunities Table
internships = [{
    'opportunity_id': f"INT{100+i}",
    'company': fake.company(),
    'role': random.choice(['Software Intern', 'Marketing Analyst', 'Research Assistant']),
    'requirements': 'GPA > 3.0, Junior Standing',
    'deadline': fake.date_between(start_date='today', end_date='+60d'),
    'status': random.choice(['Open', 'Closed'])
} for i in range(50)]


# 10. Financial Records Table
financial_records = [{
    'student_id': student['student_id'],
    'tuition_fees': 50000,
    'payments': random.randint(30000, 50000),
    'scholarships': random.choice([0, 5000, 10000]),
    'outstanding_balance': 50000 - random.randint(30000, 50000)
} for student in students]



# Sample student IDs
student_ids = [f"S{1000+i}" for i in range(50)]
activities = ['Debate Club', 'AI Club', 'Football Team', 'Volunteer Group', 'Coding Hackathon']

# 11. Extracurricular Activities Table
extracurricular_activities = [{
    'student_id': random.choice(student_ids),
    'activity_name': random.choice(activities),
    'role': random.choice(['Member', 'Leader', 'Participant']),
    'hours': random.randint(10, 100),
} for _ in range(50)]


# 12. Attendance & Behavior Table
attendance_behavior = [{
    'student_id': sid,
    'course_code': random.choice(['CS101', 'BUS201', 'ENG301', 'PHA110', 'DEN220']),
    'attendance_percent': random.randint(60, 100),
    'behavior_notes': random.choice([
        'No issues reported',
        'Late submissions noted',
        'Excellent participation',
        'Absent during midterms',
        'Disruptive in class'
    ])
} for sid in student_ids for _ in range(2)]


# DataFrames
df_students = pd.DataFrame(students)
df_academic = pd.DataFrame(academic_records)
df_courses = pd.DataFrame(courses)
df_enrollment = pd.DataFrame(enrollment)
df_advising = pd.DataFrame(advising_notes)
df_calendar = pd.DataFrame(academic_calendar)
df_dept_faculty = pd.DataFrame(department_faculty)
df_grad_reqs = pd.DataFrame(graduation_requirements)
df_internships = pd.DataFrame(internships)
df_financial = pd.DataFrame(financial_records)
df_extracurricular = pd.DataFrame(extracurricular_activities)
df_attendance_behavior = pd.DataFrame(attendance_behavior)


# data insertion
db_conn = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'edu_adv_db'
)

cursor = db_conn.cursor()

print(df_courses.info())

# students data insertion
for row in df_students.values:
    student_id = row[0]
    name = row[1]
    birthdate = row[2]
    nationality = row[3]
    contact = row[4]
    enrollment_date = row[5]
    major = row[6]
    advisor = row[7]
    status = row[8]

    sql = f"INSERT INTO StudentProfile (student_id, name, birthdate, nationality, contact, enrollment_date, major, advisor, status) VALUES ('{student_id}', '{name}', '{birthdate}', '{nationality}', '{contact}', '{enrollment_date}', '{major}', '{advisor}', '{status}')"

#     try:
#         cursor.execute(sql)
#     except mysql.connector.Error as err:
#         print(f"Error: {err}")
#         continue
#     print(f"Inserted: {sql}")

# db_conn.commit()

for row in df_academic.values:
    student_id = row[0]
    course_code = row[1]
    course_name = row[2]
    semester = row[3]
    grade = row[4]
    credits = row[5]
    gpa = row[6]

    sql = f"INSERT INTO AcademicRecords (student_id, course_code, course_name, semester, grade, credits, GPA) VALUES ('{student_id}', '{course_code}', '{course_name}', '{semester}', '{grade}', {credits}, {gpa})"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}")

# db_conn.commit()

for row in df_courses.values:
    course_code = row[0]
    name = row[1]
    description = row[2]
    credits = row[3]
    prerequisites = row[4]
    department = row[5]
    instructor = row[6]

    sql = f"INSERT INTO CourseCatalog (course_code, name, description, credits, prerequisites, department, instructor) VALUES ('{course_code}', '{name}', '{description}', {credits}, '{prerequisites}', '{department}', '{instructor}')"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}")

# db_conn.commit()

for row in df_enrollment.values:
    student_id = row[0]
    course_code = row[1]
    semester = row[2]
    enrollment_status = row[3]
    attendance_percent = row[4]

    sql = f"INSERT INTO Enrollment (student_id, course_code, semester, enrollment_status, attendance_percent) VALUES ('{student_id}', '{course_code}', '{semester}', '{enrollment_status}', {attendance_percent})"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}")

# db_conn.commit()

for row in df_advising.values:
    student_id = row[0]
    advisor_id = row[1]
    date = row[2]
    meeting_summary = row[3]
    recommendations = row[4]
    follow_up_date = row[5]

    sql = f"INSERT INTO AdvisingNotes (student_id, advisor_id, date, meeting_summary, recommendations, follow_up_date) VALUES ('{student_id}', '{advisor_id}', '{date}', '{meeting_summary}', '{recommendations}', '{follow_up_date}')"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}") 

# db_conn.commit()

for row in df_calendar.values:
    semester = row[0]
    start_date = row[1]
    end_date = row[2]
    registration_deadline = row[3]
    exam_period = row[4]

    sql = f"INSERT INTO AcademicCalendar (semester, start_date, end_date, registration_deadline, exam_period) VALUES ('{semester}', '{start_date}', '{end_date}', '{registration_deadline}', '{exam_period}')"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}")

# db_conn.commit()

for row in df_dept_faculty.values:
    department_id = row[0]
    name = row[1]
    contact_info = row[2]
    faculty_members = row[3]
    office_hours = row[4]

    sql = f"INSERT INTO DepartmentFaculty (department_id, name, contact_info, faculty_members, office_hours) VALUES ('{department_id}', '{name}', '{contact_info}', '{faculty_members}', '{office_hours}')"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}")

# db_conn.commit()

for row in df_grad_reqs.values:
    major = row[0]
    required_credits = row[1]
    core_courses = row[2]
    electives = row[3]
    capstone_project = row[4]

    sql = f"INSERT INTO GraduationRequirements (major, required_credits, core_courses, electives, capstone_project) VALUES ('{major}', {required_credits}, '{core_courses}', '{electives}', '{capstone_project}')"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}")

# db_conn.commit()

for row in df_internships.values:
    opportunity_id = row[0]
    company = row[1]
    role = row[2]
    requirements = row[3]
    deadline = row[4]
    status = row[5]

    sql = f"INSERT INTO InternshipsOpportunities (opportunity_id, company, role, requirements, deadline, status) VALUES ('{opportunity_id}', '{company}', '{role}', '{requirements}', '{deadline}', '{status}')"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}")

# db_conn.commit()

for row in df_financial.values:
    student_id = row[0]
    tuition_fees = row[1]
    payments = row[2]
    scholarships = row[3]
    outstanding_balance = row[4]

    sql = f"INSERT INTO FinancialRecords (student_id, tuition_fees, payments, scholarships, outstanding_balance) VALUES ('{student_id}', {tuition_fees}, {payments}, {scholarships}, {outstanding_balance})"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}")

# db_conn.commit()

for row in df_extracurricular.values:
    student_id = row[0]
    activity_name = row[1]
    role = row[2]
    hours = row[3]

    sql = f"INSERT INTO ExtracurricularActivities (student_id, activity_name, role, hours) VALUES ('{student_id}', '{activity_name}', '{role}', {hours})"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}")

# db_conn.commit()

for row in df_attendance_behavior.values:
    student_id = row[0]
    course_code = row[1]
    attendance_percent = row[2]
    behavior_notes = row[3]

    sql = f"INSERT INTO AttendanceBehavior (student_id, course_code, attendance_percent, behavior_notes) VALUES ('{student_id}', '{course_code}', {attendance_percent}, '{behavior_notes}')"

    # try:
    #     cursor.execute(sql)
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     continue
    # print(f"Inserted: {sql}")

# db_conn.commit()


