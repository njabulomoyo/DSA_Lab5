import csv
import os
from datetime import datetime


class Student:
    def __init__(self, student_id, fullname, email, password):
        self.student_id = student_id
        self.fullname = fullname
        self.email = email
        self.password = password
        self.registered_courses = set()


class Course:
    def __init__(self, course_id, name, instructor, days, time, max_students=30):
        self.course_id = course_id
        self.name = name
        self.instructor = instructor
        self.days = days
        self.time = time
        self.enrolled_students = set()
        self.max_students = max_students


class EnrollmentSystem:
    def __init__(self):
        self.students = {}
        self.courses = {}
        self.current_user = None

    def save_data(self):

        with open('students.csv', 'w', newline='') as f:
            fieldnames = ['student_id', 'fullname', 'email', 'password', 'registered_courses']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for student in self.students.values():
                writer.writerow({
                    'student_id': student.student_id,
                    'fullname': student.fullname,
                    'email': student.email,
                    'password': student.password,
                    'registered_courses': '|'.join(student.registered_courses)
                })

        with open('courses.csv', 'w', newline='') as f:
            fieldnames = ['course_id', 'name', 'instructor', 'days', 'time', 'max_students', 'enrolled_students']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for course in self.courses.values():
                writer.writerow({
                    'course_id': course.course_id,
                    'name': course.name,
                    'instructor': course.instructor,
                    'days': course.days,
                    'time': course.time,
                    'max_students': course.max_students,
                    'enrolled_students': '|'.join(course.enrolled_students)
                })

    def load_data(self):
        # === Load Students ===
        if os.path.exists('students.csv'):
            with open('students.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Step 1: Create the Student object
                    student = Student(
                        student_id=row['student_id'],
                        fullname=row['fullname'],
                        email=row['email'],
                        password=row['password']  # You need to update your Student class to accept this
                    )

                    # Step 2: Load registered courses (if any)
                    if row['registered_courses']:
                        student.registered_courses = set(row['registered_courses'].split('|'))

                    # Step 3: Add to self.students
                    self.students[student.student_id] = student

        if os.path.exists('courses.csv'):
            with open('courses.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Step 1: Create the Course object
                    course = Course(
                        course_id=row['course_id'],
                        name=row['name'],
                        instructor=row['instructor'],
                        days=row['days'],
                        time=row['time'],
                        max_students=int(row['max_students'])
                    )

                    if row['enrolled_students']:
                        course.enrolled_students = set(row['enrolled_students'].split('|'))

                    self.courses[course.course_id] = course

    def register_student(self, student_id, fullname, email, password):
        if student_id in self.students:
            print("Student ID already exists.")
            return False

        student = Student(student_id, fullname, email, password)
        self.students[student_id] = student
        print(f"{fullname} registered successfully!")
        return True

    def login_student(self, student_id, password):
        student = self.students.get(student_id)

        if not student:
            print("No account found with that student ID.")
            return False

        if student.password != password:
            print("Incorrect password.")
            return False

        self.current_user = student
        print(f"Welcome back, {student.fullname}!")
        return True

    def logout_student(self):
        self.current_user = None

    def add_course(self, course_id, name, instructor, days, time, max_students=30):
        if course_id in self.courses:
            print("Course already exists.")
            return False

        course = Course(course_id, name, instructor, days, time, max_students)
        self.courses[course_id] = course
        print(f"Course '{name}' added.")
        return True

    def drop_course(self, course_id):
        if not self.current_user:
            print("Please log in first.")
            return False

        student = self.current_user

        if course_id not in student.registered_courses:
            print("Not enrolled in this course.")
            return False

        student.registered_courses.remove(course_id)
        self.courses[course_id].enrolled_students.discard(student.student_id)
        print(f"Dropped {course_id}")
        return True

    def view_available_courses(self):
        print("\nAvailable Courses:")
        for c in self.courses.values():
            print(
                f"{c.course_id} - {c.name} | {c.instructor} | {c.days} {c.time} | Enrolled: {len(c.enrolled_students)}/{c.max_students}")

    def view_registered_courses(self):
        if not self.current_user:
            print("Please log in to view your schedule.")
            return

        print(f"\n Registered Courses for {self.current_user.fullname}:")
        for cid in self.current_user.registered_courses:
            course = self.courses.get(cid)
            if course:
                print(f"{course.course_id} - {course.name} | {course.days} {course.time}")

    def parse_time_range(self, time_range: str):

        start_str, end_str = time_range.split('–')
        start = datetime.strptime(start_str.strip(), '%H:%M').time()
        end = datetime.strptime(end_str.strip(), '%H:%M').time()
        return start, end

    def check_schedule_conflict(self, new_course: Course, student: Student) -> bool:
        new_days = set(new_course.days)
        new_start, new_end = self.parse_time_range(new_course.time)

        for course_id in student.registered_courses:
            existing_course = self.courses.get(course_id)
            if not existing_course:
                continue

            existing_days = set(existing_course.days)
            existing_start, existing_end = self.parse_time_range(existing_course.time)

            if new_days & existing_days:

                if (new_start < existing_end and new_end > existing_start):
                    print(
                        f"Schedule conflict with {existing_course.course_id} ({existing_course.days} {existing_course.time})")
                    return True

        return False

    def enroll_current_user_in_course(self, course_id):
        if not self.current_user:
            print("Please log in first.")
            return False

        if course_id not in self.courses:
            print("Course not found.")
            return False

        student = self.current_user
        course = self.courses[course_id]

        if course_id in student.registered_courses:
            print("Already enrolled.")
            return False

        if len(course.enrolled_students) >= course.max_students:
            print("Course is full.")
            return False

        if self.check_schedule_conflict(course, student):
            print("Cannot enroll due to a schedule conflict.")
            return False

        student.registered_courses.add(course_id)
        course.enrolled_students.add(student.student_id)
        print(f"Enrolled in {course.name}")
        return True


import PySimpleGUI as sg

# Initialize system and load data
system = EnrollmentSystem()
if not system.courses:
    system.add_course("BIO101", "General Biology", "Dr. Darwin", "MWF", "08:00–09:30")
    system.add_course("CHEM101", "Intro to Chemistry", "Dr. Curie", "TR", "08:00–09:30")
    system.add_course("MATH101", "College Algebra", "Dr. Euler", "MWF", "09:00–10:30")
    system.add_course("PHYS101", "Physics I", "Dr. Newton", "TR", "09:00–10:30")
    system.add_course("CS101", "Intro to Programming", "Prof. Turing", "MWF", "10:00–11:30")
    system.add_course("PSY101", "Psychology Basics", "Dr. Freud", "TR", "10:00–11:30")
    system.add_course("ENG101", "English Composition", "Prof. Orwell", "MWF", "11:00–12:30")
    system.add_course("SOC101", "Intro to Sociology", "Dr. Durkheim", "TR", "11:00–12:30")
    system.add_course("ART101", "Foundations of Art", "Prof. Picasso", "MWF", "12:00–13:30")
    system.add_course("MUS101", "Music Theory", "Prof. Bach", "TR", "12:00–13:30")
    system.add_course("HIST101", "World History", "Dr. Herodotus", "MWF", "13:00–14:30")
    system.add_course("ECON101", "Microeconomics", "Dr. Smith", "TR", "13:00–14:30")
    system.add_course("PHIL101", "Intro to Philosophy", "Dr. Kant", "MWF", "14:00–15:30")
    system.add_course("LANG101", "Spanish I", "Prof. Cervantes", "TR", "14:00–15:30")
    system.add_course("BUS101", "Principles of Business", "Dr. Bezos", "MWF", "08:00–09:30")
    system.add_course("LAW101", "Intro to Law", "Prof. Ginsburg", "TR", "09:00–10:30")
    system.add_course("ANTH101", "Cultural Anthropology", "Dr. Levi-Strauss", "MWF", "10:00–11:30")
    system.add_course("ASTRO101", "Astronomy Basics", "Dr. Hawking", "TR", "11:00–12:30")
    system.add_course("GEO101", "Physical Geography", "Dr. Wegener", "MWF", "12:00–13:30")
    system.add_course("MED101", "Intro to Medicine", "Dr. House", "TR", "14:00–15:30")
    system.save_data()

system.load_data()

# Track login state
current_user_id = None


# GUI layout functions
def login_layout():
    return [
        [sg.Text("Student ID"), sg.Input(key="-LOGIN_ID-")],
        [sg.Text("Password"), sg.Input(password_char="*", key="-LOGIN_PASS-")],
        [sg.Button("Login"), sg.Button("Register")]
    ]


def register_layout():
    return [
        [sg.Text("Student ID"), sg.Input(key="-REG_ID-")],
        [sg.Text("Full Name"), sg.Input(key="-REG_NAME-")],
        [sg.Text("Email"), sg.Input(key="-REG_EMAIL-")],
        [sg.Text("Password"), sg.Input(password_char="*", key="-REG_PASS-")],
        [sg.Button("Submit Registration"), sg.Button("Back")]
    ]


def dashboard_layout(student):
    return [
        [sg.Text(f"Logged in as: {student.fullname}")],
        [sg.Button("View Available Courses")],
        [sg.Listbox(values=[], key="-AVAILABLE_COURSES_LIST-", size=(50, 6))],
        [sg.Button("Enroll Selected", key="-ENROLL_SELECTED-")],
        [sg.Button("View My Courses")],
        [sg.Button("Enroll in Course"), sg.Input(key="-ENROLL_ID-", size=(10, 1))],
        [sg.Button("Drop Course"), sg.Input(key="-DROP_ID-", size=(10, 1))],
        [sg.Button("Logout")]
    ]


# Application Loop
layout = login_layout()
window = sg.Window("Course Enrollment System", layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    # Handle login
    if event == "Login":
        sid = values["-LOGIN_ID-"]
        pwd = values["-LOGIN_PASS-"]
        if system.login_student(sid, pwd):
            current_user_id = sid
            window.close()
            layout = dashboard_layout(system.current_user)
            window = sg.Window("Dashboard", layout)
        else:
            sg.popup_error("Invalid credentials.")

    # Switch to registration layout
    elif event == "Register":
        window.close()
        layout = register_layout()
        window = sg.Window("Register New Student", layout)

    # Handle registration
    elif event == "Submit Registration":
        sid = values["-REG_ID-"]
        name = values["-REG_NAME-"]
        email = values["-REG_EMAIL-"]
        pwd = values["-REG_PASS-"]
        if system.register_student(sid, name, email, pwd):
            sg.popup("Registration successful.")
        else:
            sg.popup_error("Student ID already exists.")
        window.close()
        layout = login_layout()
        window = sg.Window("Login", layout)

    elif event == "Back":
        window.close()
        layout = login_layout()
        window = sg.Window("Login", layout)

    # View available courses
    elif event == "View Available Courses":
        course_info = "\n".join([
            f"{c.course_id} - {c.name} | {c.instructor} | {c.days} {c.time} | {len(c.enrolled_students)}/{c.max_students}"
            for c in system.courses.values()
        ]) or "No courses available."
        sg.popup_scrolled(course_info, title="Available Courses", size=(60, 20))
        window["-AVAILABLE_COURSES_LIST-"].update(
            [
                f"{c.course_id} - {c.name} | {c.instructor} | {c.days} {c.time} | Enrolled: {len(c.enrolled_students)}/{c.max_students}"
                for c in system.courses.values()
            ]
        )


    # View my registered courses
    elif event == "View My Courses":
        student = system.current_user
        info = []
        for cid in student.registered_courses:
            course = system.courses.get(cid)
            if course:
                info.append(f"{course.course_id} - {course.name} | {course.days} {course.time}")
        message = "\n".join(info) if info else "No registered courses."
        sg.popup_scrolled(message, title="My Courses", size=(60, 20))

    # Enroll in course
    elif event == "Enroll in Course":
        cid = values["-ENROLL_ID-"].strip()
        if system.enroll_current_user_in_course(cid):
            sg.popup("Enrolled successfully.")
        else:
            sg.popup_error("Enrollment failed.")
    elif event == "-ENROLL_SELECTED-":
        selected = values["-AVAILABLE_COURSES_LIST-"]
        if selected:
            item_text = selected[0]
            course_id = item_text.split()[0]

            if system.enroll_current_user_in_course(course_id):
                sg.popup("Enrolled successfully.")
            else:
                sg.popup_error("Enrollment failed.")
    else:
        sg.popup_error("No course selected.")

    # Drop course
    elif event == "Drop Course":
    cid = values["-DROP_ID-"].strip()
    if system.drop_course(cid):
        sg.popup("Dropped successfully.")
    else:
        sg.popup_error("Drop failed.")

# Handle logout
elif event == "Logout":
system.logout_student()
current_user_id = None
window.close()
layout = login_layout()
window = sg.Window("Login", layout)

# Save before exiting
system.save_data()
window.close()

