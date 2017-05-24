from pymongo import MongoClient
import csv
import hashlib
import datetime

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
    seen = {} #will store dictionaries to hold student data
    
    transcript = csv.DictReader(f)
    for class_record in transcript:

        #if student not in database, set up ALL info
        if class_record["StudentID"] not in seen:
            student = {}
            student['id'] = class_record["StudentID"]
            student['first_name'] = class_record["FirstName"]
            student['last_name'] = class_record["LastName"]
            student['cohort'] = str(datetime.datetime.now().year - (int(class_record["Grade"]) - 9))
            
            student['classes_taken'] = {}
            student['department_averages'] = {}
            depts = list_departments()
            for dept in depts:
                student['classes_taken'][dept] = []
                student['department_averages'][dept] = 0
            student['classes_taken']["Unknown"] = [] #stores unrecognized codes
        
            student['overall_average'] = 0
            student['selections'] = []
            seen[class_record["StudentID"]] = student

        #otherwise, retrieve the student data we collected already
        else:
            student = seen[class_record["StudentID"]]

        course_code = class_record["Course"]
        course_info = db.courses.find_one( {"code": course_code } )
        course_dept = course_info["department"] if course_info != None else "Unknown"
        course_mark = class_record["Mark"]

        student["classes_taken"][course_dept].append( {"code" : course_code, "mark" : course_mark})

    #convert seen (dictionary) into a list to send to mongo db
    data = []
    for entry in seen:
        data.append( seen[entry] )
    print data
        
    db.students.insert_many(data)

def calculate_department_average(student, department):
    pass
    
def calculate_averages(student):
    pass
