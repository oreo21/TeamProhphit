from pymongo import MongoClient
import csv

server = MongoClient("lisa.stuy.edu")
db = server['platekschengshi']

def initialize():
    init_courses()
    init_students()

def init_courses():
    f = open("courses.csv")
    course_list = csv.DictReader(f)
    for elem in course_list:
        course = {}
        course["code"] = elem["CourseCode"]
        course["name"] = elem["CourseName"]
        course["department"] = elem["Department"]
        
        db.courses.insert_one(course)

def init_students():
    f = open("students.csv")
    student_list = csv.DictReader(f)
    for elem in course_list:
        student = {}

        db.students.insert_one(student)
        
initialize()
