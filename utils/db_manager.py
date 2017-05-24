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
    seen = {}
    transcript = csv.DictReader(f)
    for class_record in transcript:
        
        course_code = class_record["Course"]
        course_dept = db.courses.find_one( {"code": course_code } )["department"]

        if class_record["StudentID"] not in seen:
            student = {}
            student['id'] = class_record["StudentID"]
            seen.append(class_record["StudentID"])
            student['first_name'] = class_record["FirstName"]
            student['last_name'] = class_record["LastName"]
            student['cohort'] = class_record["Year"]
            
            student['classes_taken'] = {}
            student['department_averages'] = {}
            depts = list_departments()
            for dept in depts:
                student['classes_taken'][dept] = []
                student['department_averages'][dept] = 0

            student['overall_average'] = 0
            student['selections'] = []
            seen[class_record["StudentID"]] = student

        else:
            student = seen[class_record["StudentID"]]
        student["classes_taken"][course_dept].append(course_code)

        data = []
        for entry in seen:
            data.append( seen[entry] )
        print data
        
        db.students.insert_many(data)
