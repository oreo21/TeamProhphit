from pymongo import MongoClient
import csv
import hashlib

#server = MongoClient()
server = MongoClient("lisa.stuy.edu")
db = server['ttpp']

def list_departments():
    ret = []
    depts = db.departments.find({})
    for dept in depts:
       # print dept
        ret.append( dept["name"].encode("ascii") )
    return ret

def init_students(f):
    seen = []
    student_list = csv.DictReader(f)
    for elem in student_list:
        print elem
        if elem["StudentID"] not in seen:
            student = {}
            student['id'] = elem["StudentID"]
            seen.append(elem["StudentID"])
            student['first_name'] = elem["FirstName"]
            student['last_name'] = elem["LastName"]
            student['cohort'] = elem["Year"]
            student['classes_taken'] = {}
            student['department_averages'] = {}
            depts = list_departments()
            for dept in depts:
                student['classes_taken'][dept] = []
                student['department_averages'][dept] = 0
            student['overall_average'] = 0
            student['selections'] = []
            db.students.insert_one(student)
