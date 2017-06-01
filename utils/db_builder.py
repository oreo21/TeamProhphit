from pymongo import MongoClient
from db_manager import *
import csv
import hashlib


server = MongoClient()
#server = MongoClient("lisa.stuy.edu")
db = server['ttpp']

course_file = "data/courses.csv"

def initialize():
    init_courses(course_file)
    init_departments(course_file)
    init_admin()
    init_state()

def init_courses(filename):
    f = open(filename)
    course_list = csv.DictReader(f)
    for elem in course_list:
        course = {}
        course["code"] = elem["CourseCode"]
        course["name"] = elem["CourseName"]

        if is_science_course(course["code"]):
            course["department"] = get_science_department(course["code"])
        else:
            course["department"] = elem["Department"]

        course["is_AP"] = is_AP(course["code"])
        course["weight"] = get_weight(course["code"])
        course["prereq_courses"] = []
        course["prereq_overall_average"] = 0
        course["prereq_department_averages"] = []
        course["grade_levels"] = [9, 10, 11, 12]
#        if course["code"][0] == "S":
#            print course
        db.courses.insert_one(course)

def init_departments(filename):
    f = open(filename)
    course_list = csv.DictReader(f)
    for elem in course_list:
        code = elem["CourseCode"]
        if is_science_course(code):
            dep = get_science_department(code)
        elif is_cs_course(code):
            dep = "Computer Science"
        else:
            dep = elem["Department"]
        new = db.departments.find_one({"name" : dep}) == None
        if new:
            d = {}
            d['name'] = dep
            d["courses"] = [ code ]
            db.departments.insert_one(d)
        else:
            db.departments.update_one({"name" : dep},
                                      {"$push" :
                                       {"courses": code }
                                      }
            )
    db.departments.insert_one({"name" : "Unknown", "courses" : []})

def init_admin():
    admin = {}
    admin['username'] = "admin"
    admin['password'] = hashlib.sha512("password").hexdigest()
    db.admins.insert_one(admin)

def init_state():
    doc = {}
    doc["on"] = 0
    db.state.insert_one(doc)
    
initialize()
