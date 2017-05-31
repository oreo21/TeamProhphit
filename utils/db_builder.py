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
    init_state()

def get_weight(code):
    #Physical education classes
    if is_pe_course(code):
        return 0
    #Lab classes
    if is_science_course(code) and code[-1] == "L":
        return 0
    return 1

def get_science_department(code):
    sym = code[1]
    if sym == "P":
        return "Physics"
    elif sym == "C":
        return "Chemistry"
    elif sym == "L" or sym == "B":
        return "Biology"
    else:
        return "Science"

def is_science_course(code):
    return code[0] == "S"

def is_pe_course(code):
    return code[0] == "P" and (code[-1] == "A" or code[-1] == "B")

def is_cs_course(code):
    return code[:2] == "MK"

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

        course["is_AP"] = 1 if course["code"][-1] == "X" else 0
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
