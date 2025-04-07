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
        if os.path.exists('students.csv'):
            with open('students.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    
                    student = Student(
                        student_id = row['student_id'],
                        fullname = row['fullname'],
                        email = row['email'],
                        password = row['password']  
                    )

                    
                    if row['registered_courses']:
                        student.registered_courses = set(row['registered_courses'].split('|'))

               
                    self.students[student.student_id] = student
    
    
        if os.path.exists('courses.csv'):
            with open('courses.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                 
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
            print(f"{c.course_id} - {c.name} | {c.instructor} | {c.days} {c.time} | Enrolled: {len(c.enrolled_students)}/{c.max_students}")



    def view_registered_courses(self):
        if not self.current_user:
            print("Please log in to view your schedule.")
            return

        print(f"\n Registered Courses for {self.current_user.fullname}:")
        for cid in self.current_user.registered_courses:
            course = self.courses.get(cid)
            if course:
                print(f"{course.course_id} - {course.name} | {course.days} {course.time}")
          
                
    def parse_time_range(self,time_range: str):
       
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
                    print(f"Schedule conflict with {existing_course.course_id} ({existing_course.days} {existing_course.time})")
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

        
def main():
    system = EnrollmentSystem()
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
    
    system.register_student("S001", "Njabulo Moyo", "njabulo@uni.edu", "pass123")

    system.login_student("S001", "pass123")

    
    system.add_course("CS101", "Intro to CS", "Prof. X", "MWF", "10:00–11:20")

   
    system.enroll_current_user_in_course("CS101")

    
    system.view_registered_courses()

    
    system.save_data()
    

if __name__ == "__main__":    
    main()
        
        
        
        
        
        
        
