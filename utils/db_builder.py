from pymongo import MongoClient
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

def init_courses(filename):
    f = open(filename)
    course_list = csv.DictReader(f)
    for elem in course_list:
        course = {}
        course["code"] = elem["CourseCode"]
        course["name"] = elem["CourseName"]
        course["department"] = elem["Department"]
        course["is_AP"] = 1 if course["code"][-1] == "X" else 0
        course["prereq_courses"] = []
        course["prereq_overall_average"] = 0
        course["prereq_department_average"] = 0
        db.courses.insert_one(course)

def init_departments(filename):
    depts = {}
    f = open(filename)
    course_list = csv.DictReader(f)
    for elem in course_list:
        if elem["Department"] not in depts:
            d = {}
            d['name'] = elem["Department"]
            d["courses"] = [ elem["CourseCode"] ]
            depts[elem["Department"]] = d
        else:
            d = depts[elem["Department"]]
            d["courses"].append( elem["CourseCode"] )
    data = []
    for dept in depts:
        data.append(depts[dept])
    db.departments.insert_many(data)
        
def init_admin():
    admin = {}
    admin['username'] = "admin"
    admin['password'] = hashlib.sha512("password").hexdigest()
    db.admins.insert_one(admin)
    
initialize()
