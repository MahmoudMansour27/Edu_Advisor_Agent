import mysql.connector

db_conn = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'edu_adv_db'
)

cursor = db_conn.cursor()

sql = '''
-- 1. Student Profile Table
CREATE TABLE StudentProfile (
    student_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    birthdate DATE,
    nationality VARCHAR(50),
    contact VARCHAR(50),
    enrollment_date DATE,
    major VARCHAR(100),
    advisor VARCHAR(100),
    status VARCHAR(20)
);

-- 2. Academic Records Table (Transcript)
CREATE TABLE AcademicRecords (
    record_id SERIAL PRIMARY KEY,
    student_id VARCHAR(10),
    course_code VARCHAR(10),
    course_name VARCHAR(100),
    semester VARCHAR(20),
    grade VARCHAR(2),
    credits INT,
    GPA DECIMAL(3, 2),
    FOREIGN KEY (student_id) REFERENCES StudentProfile(student_id)
);

-- 3. Course Catalog Table
CREATE TABLE CourseCatalog (
    course_code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    credits INT,
    prerequisites TEXT,
    department VARCHAR(100),
    instructor VARCHAR(100)
);

-- 4. Enrollment Table
CREATE TABLE Enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    student_id VARCHAR(10),
    course_code VARCHAR(10),
    semester VARCHAR(20),
    enrollment_status VARCHAR(20),
    attendance_percent INT,
    FOREIGN KEY (student_id) REFERENCES StudentProfile(student_id),
    FOREIGN KEY (course_code) REFERENCES CourseCatalog(course_code)
);

-- 5. Advising Notes Table
CREATE TABLE AdvisingNotes (
    note_id SERIAL PRIMARY KEY,
    student_id VARCHAR(10),
    advisor_id VARCHAR(10),
    date DATE,
    meeting_summary TEXT,
    recommendations TEXT,
    follow_up_date DATE,
    FOREIGN KEY (student_id) REFERENCES StudentProfile(student_id)
);

-- 6. Academic Calendar Table
CREATE TABLE AcademicCalendar (
    semester VARCHAR(20) PRIMARY KEY,
    start_date DATE,
    end_date DATE,
    registration_deadline DATE,
    exam_period VARCHAR(50)
);

-- 7. Department and Faculty Table
CREATE TABLE DepartmentFaculty (
    department_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    contact_info VARCHAR(100),
    faculty_members TEXT,
    office_hours VARCHAR(50)
);

-- 8. Graduation Requirements Table
CREATE TABLE GraduationRequirements (
    major VARCHAR(100) PRIMARY KEY,
    required_credits INT,
    core_courses TEXT,
    electives TEXT,
    capstone_project VARCHAR(100)
);

-- 9. Internships and Opportunities Table
CREATE TABLE Internships (
    opportunity_id VARCHAR(10) PRIMARY KEY,
    company VARCHAR(100),
    role VARCHAR(100),
    requirements TEXT,
    deadline DATE,
    status VARCHAR(10)
);

-- 10. Financial Records Table
CREATE TABLE FinancialRecords (
    financial_id SERIAL PRIMARY KEY,
    student_id VARCHAR(10),
    tuition_fees DECIMAL(10, 2),
    payments DECIMAL(10, 2),
    scholarships DECIMAL(10, 2),
    outstanding_balance DECIMAL(10, 2),
    FOREIGN KEY (student_id) REFERENCES StudentProfile(student_id)
);

-- 11. Extracurricular Activities Table
CREATE TABLE ExtracurricularActivities (
    activity_id SERIAL PRIMARY KEY,
    student_id VARCHAR(10),
    activity_name VARCHAR(100),
    role VARCHAR(50),
    hours INT,
    achievements TEXT,
    FOREIGN KEY (student_id) REFERENCES StudentProfile(student_id)
);

-- 12. Attendance & Behavior Table
CREATE TABLE AttendanceBehavior (
    behavior_id SERIAL PRIMARY KEY,
    student_id VARCHAR(10),
    course_code VARCHAR(10),
    attendance_percent INT,
    behavior_notes TEXT,
    FOREIGN KEY (student_id) REFERENCES StudentProfile(student_id),
    FOREIGN KEY (course_code) REFERENCES CourseCatalog(course_code)
);

'''

try:
    cursor.execute(sql, multi=True)
    db_conn.commit()
    print("Tables created successfully")
except mysql.connector.Error as err:
    print(f"Error: {err}")