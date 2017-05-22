from pymongo import MongoClient
import csv

server = MongoClient("lisa.stuy.edu")
db = server['ttpp']

course_file = "data/courses.csv"
student_file = "data/students.csv"

def list_departments(filename):
    depts = []
    f = open(filename)
    course_list = csv.DictReader(f)
    for elem in course_list:
        if elem["Department"] not in depts:
            depts.append(elem["Department"])
    return depts
    
def initialize():
    init_courses(course_file)
    init_students(student_file)

def init_courses(filename):
    f = open(filename)
    course_list = csv.DictReader(f)
    for elem in course_list:
        course = {}
        course["code"] = elem["CourseCode"]
        course["name"] = elem["CourseName"]
        course["department"] = elem["Department"]
        course["prereq_courses"] = []
        course["prereq_overall_average"] = 0
        course["prereq_department_average"] = 0
        db.courses.insert_one(course)

#need a list of all the students
def init_students(filename):
    f = open(filename)
    seen = []
    student_list = csv.DictReader(f)
    for elem in student_list:
        if elem["StudentID"] in seen:
            continue
        student = {}
        student['id'] = elem["StudentID"]
        seen.append(elem["StudentID"])
        student['first_name'] = elem["FirstName"]
        student['last_name'] = elem["LastName"]
        student['cohort'] = elem["Year"]

        student['classes_taken'] = {}
        student['department_averages'] = {}
        depts = list_departments(course_file)
        for dept in depts:
            student['classes_taken'][dept] = []
            student['department_averages'][dept] = 0

        student['overall_average'] = 0
        student['selections'] = []
        print student
        db.students.insert_one(student)
        
        
initialize()
