from pymongo import MongoClient
import csv
import hashlib
import datetime

server = MongoClient()
#server = MongoClient("lisa.stuy.edu")
db = server['ttpp']

# args: none
# return: a list of the names of all the departments
def list_departments():
    ret = []
    depts = db.departments.find({})
    for dept in depts:
       # print dept
        ret.append( dept["name"].encode("ascii") )
    return ret

# args: fileObject f
#       f is a file object of a CSV ofstudents' transcripts
#       each row in the CSV file correlates to one class
#         e.g. one student took 7 classes in his Stuy career so far,
#              so the first 7 lines correspond to those classes
#         the CSV contains the following columns:
#             * StudentID
#             * FirstName
#             * LastName
#             * Grade (9, 10, 11, 12)
#             * Course (Course code)
#             * Mark (Grade in the course)
# return: none
def add_students(f):
    transcripts = csv.DictReader(f)

    for class_record in transcripts:
        course_code = class_record["Course"]
        course_info = db.courses.find_one( {"code": course_code } )
        course_dept = course_info["department"] if course_info != None else "Unknown"

        student = db.students.find_one( {"id" : class_record["StudentID"]} )
        #if student not in database, set up a dictionary for all student info
        new = student == None:
        if new:
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
                student['department_averages'][dept] = {"average": 0, "count": 0}
            student['classes_taken']["Unknown"] = [] #stores unrecognized codes
            student['classes_taking'] = []
            
            student['overall_average'] = 0
            student['selections'] = []
            student['exceptions'] = []
            student["amount"] = 0
    
        if "Mark" in class_record: #class has grade means class is in the past
            course_mark = class_record["Mark"]
            student["classes_taken"][course_dept].append( {"code" : course_code, "mark" : course_mark})
            if new:
                db.students.insert_one(student)
            else:
                db.students.update_one( {"id" : student["id"]},
                                        {"$set" :
                                         {"classes_taken" :
                                          student["classes_taken"]}})
        else: #class has no grade means class is current
            student["classes_taking"].append(course_code)
            if new:
                db.students.insert_one(student)
            else:
                db.students.update_one( {"id" : student["id"]},
                                        {"$set" :
                                         {"classes_taken" :
                                          student["classes_taken"]}})

# args: string student OSIS number
# return: student document as a dictionary
def get_student(student_id):
    return db.students.find_one( {"id" : student_id} )

# args: string student OSIS number, string department name
# return: departmental average of student as a float
def get_department_average(student_id, department):
    student = get_student(student_id)
    return student["department_averages"][department]

# args: string student OSIS number
# return: average of student as a float
def get_overall_average(student_id):
    student = get_student(student_id)
    return student["overall_average"]

# args: string student OSIS number, string department name
# return: none
# recalculates the departmental average
# used when new classes are added to the student's data
#   or if a grade was changed
def recalculate_department_average(student_id, department):
    student = get_student(student_id)
    if student == None:
        print "ERROR: no student with that ID"
        return
    courses = student["classes_taken"][department]
    print courses
    total = count = 0
    for course in courses:
        if course["weight"]: #not 0
            try:
                total += int(course["mark"])
                count += 1
            except:
                pass
            print total
            print count
    avg = total * 1.0 / count if count != 0 else 0
    print "avg: ", avg
    student["department_averages"][department]["average"] = avg
    student["department_averages"][department]["count"] = count
    db.students.update_one( {"id" : student_id},
                            {"$set" :
                                {"department_averages" : student["department_averages"] }
                            }
                          )

# args: string student OSIS number
# return: none
# recalculates the overall average
# used when new classes are added to the student's data
#   or if a grade was changed
def recalculate_overall_average(student_id):
    student = get_student(student_id)
    dept_avgs = student["department_averages"]
    print dept_avgs
    summ = 0
    count = 0
    for dept in dept_avgs:
        summ += dept_avgs[dept]["average"] * dept_avgs[dept]["count"]
        count += dept_avgs[dept]["count"]
    avg = summ * 1.0 / count
    db.students.update_one( {"id" : student_id},
                            {"$set" :
                             {"overall_average" : avg}
                            }
                          )
# args: string course code
# return: course document
def get_course(code):
    return db.courses.find_one({"code" : code})

# args: string student OSIS number, string field, string/list/number value
# return: none
# updates field with new value
# possible fields to be updated:
#     * first_name
#     * last_name
#     * cohort
#     * id
#     * selections
def edit_student(student_id, field, value):
    db.students.update_one( {"id" : student_id},
                            {"$set" : {field : value}}
                           )
# args: none
# return: list of course codes of all AP courses
def get_APs():
    docs = db.courses.find({"is_AP" : 1})
    ret = []
    for doc in docs:
        ret.append( doc["code"].encode("ascii") )
    return ret

def get_department_courses(department):
    dept = db.departments.find_one({"name" : department})
    return dept["courses"]

# args: string course code, string field, list/number value
# return: none
# updates field with new value
# possible fields to be updated:
#     * prereq_courses
#     * prereq_overall_average
#     * prereq_department_average
def edit_course(code, field, value):
    db.courses.update_one( {"code" : code},
                           {"$set" : {field : value}}
                           )



# PE courses: PE---A or PE---B
# Science courses:
#  physics SP---
#  chemistry SC---
#  biology SB--- or SL---
#    admin inputs for every other combo
#    lab courses: S---L
# Math courses:
#  compsci MK---
