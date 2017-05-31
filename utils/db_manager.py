from pymongo import MongoClient
import csv
import hashlib
import datetime

db_name = "ttpp"

server = MongoClient()
#server = MongoClient("lisa.stuy.edu")
db = server[db_name]

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
        new = student == None
        if new:
            student = {}
            student['id'] = class_record["StudentID"]
            student['first_name'] = class_record["FirstName"]
            student['last_name'] = class_record["LastName"]
            student['cohort'] = grade_to_cohort(int(class_record["Grade"]))
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
    if field == "classes_taken":
        recalculate_department_averages(student_id)
        recalculate_overall_average(student_id)

def recalculate_department_averages(student_id):
    depts = list_departments()
    for dept in depts:
        recalculate_department_average(student_id, dept)

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

def grade_to_cohort(grade):
    this_year = datetime.datetime.now().year
    offset = grade - 9 + 1
    return this_year - offset
    
def cohort_to_grade(cohort):
    this_year = datetime.datetime.now().year
    offset = this_year - cohort - 1
    return 9 + offset

# args: string course code
# return: course document
def get_course(code):
    return db.courses.find_one({"code" : code})

def get_problematic_courses():
    docs = db.courses.find({"department" : "Unknown"})
    ret = [doc for doc in docs]
    print ret
    return ret

# args: none
# return: list of course codes first term of all AP courses
def get_APs():
    docs = db.courses.find({"is_AP" : 1})
    ret = []
    for doc in docs:
        if doc["department"] != "Functional Codes" and "2 of 2" not in doc["name"]:
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

#return -1 if class not taken    
def get_class_mark(student_id, course_code):
    student = db.students.find_one({"id" : student_id})
    
    course_info = db.courses.find_one({"code" : code})
    dept = course_info["department"]
    for course in student["classes_taken"][dept]:
        if course["code"] == course_code:
            return course["mark"]
    return -1
    
#generates list of aps this student can sign up for based on pre-reqs
def get_applicable_APs(student_id):
    student = db.students.find_one({"id": student_id})
    all_APs = get_APs()
    ret = []
    for course_code in all_APs:
        
        #admin override allows this AP
        #don't bother chechking other pre-reqs
        if course_code in student["exceptions"]:
            ret.append(course_code)
            continue
        
        course = db.courses.find_one({"code" : course_code})

        #is in the correct grade
        if cohort_to_grade(student["cohort"]) not in course["grade_levels"]:
            continue

        #meets overall avg requirement
        if student["overall_average"] < course["prereq_overall_average"]:
            continue

        #meets department avgs requirement
        meets_avg_reqs = True
        for and_req in course["prereq_department_averages"]:
            met = False
            for or_req in and_req:
                dept = req["name"]
                avg = req["average"]
                if student[department_averages][dept] >= avg:
                    met = True
                    break
            if not met:
                meets_avg_reqs = False
                break
        
        if not meets_avg_reqs:
            continue

        #meets prereq class requirements
        meets_class_reqs = True
        for and_req in course["prereq_courses"]:
            met = False
            for or_req in and_req:
                code = req["code"]
                mark = req["mark"]
                
                if code in student["classes_taking"] or \
                   get_class_mark(student_id, code) >= mark:
                    met = True
                    break
            if not met:
                meets_class_reqs = False
                break

        if not meets_class_reqs:
            continue

        #if passed all checks, then AP is applicable
        ret.append(course_code)
        
def remove_student(student_id):
    db.students.delete_many({"id" : student_id})

def remove_cohort(year):
    db.students.delete_many({"cohort" : year})

def get_site_status():
    res = db.state.find_one({})
    return res["on"]

def set_site_status(status):
    db.state.update_one({}, {"$set" : {"on" : status}})
    
def drop_db():
    server.drop_database(db_name)

def drop_students():
    db.students.drop()
    
# Math courses:
#  compsci MK---
