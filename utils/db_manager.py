from pymongo import MongoClient
from db_builder import initialize
import csv, hashlib, datetime

db_name = "ttpp"

server = MongoClient()
#server = MongoClient("lisa.stuy.edu")
db = server[db_name]

# args: course code
# return: weight of course (1 or 0)
#         0 if course is a PE or Lab course
def get_weight(code):
    #Physical education classes
    if is_pe_course(code):
        return 0
    #Lab classes
    if is_science_course(code) and code[-1] == "L":
        return 0
    return 1

# args: course code of a science course
# return: the specific science dept (Physics, Chem, or Bio), or Science if unknown
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

# args: course code
# return: true if course is a science course, false if not
def is_science_course(code):
    return code[0] == "S"

# args: course code
# return: boolean if course is or is not AP

# args: course code
# return: true if course is a physical education course, false if not
def is_pe_course(code):
    return code[0] == "P" and (code[-1] == "A" or code[-1] == "B")

# args: course code
# return: true if course is a computer science course, false if not
def is_cs_course(code):
    return code[:2] == "MK"

# args: course code
# return: true if course is an AP, false if not
def is_AP(code):
    if(code[-1] == "X"):
        return 1
    return 0

# args: file obj of csv containing course info
# returns: none
# initializes courses collection
def add_courses(f):
    for elem in f:
        try:
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
            db.courses.insert_one(course)
            #things go wrong sometimes (empty entries)
        except:
            pass

# args: file obj of csv containing course info
# returns: none
# initializes departments collection to hold lists of courses per dept
def add_departments(f):
    db.departments.insert_one({"name" : "Unknown", "courses" : []})
    for elem in f:
        try:
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
            #things go wrong sometimes (empty entries)
        except:
            print elem



# args: none
# return: a list of the names of all the departments
def list_departments():
    ret = []
    depts = db.departments.find({})
    for dept in depts:
       # print dept
        ret.append( dept["name"].encode("ascii") )
    return ret

# args: none
# return: a list of the names of departments that have AP classes
def list_departments_AP():
    ret = []
    APs = get_APs()
    for AP in APs:
        dept = get_course(AP)["department"]
        if dept not in ret:
            ret.append(dept)
    return ret

def remove_stuyedu(s):
    if s.find("@stuy.edu") != -1:
        s = s[:s.find("@stuy.edu")]
    return s

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
    ret = False
    for class_record in f:
        try:
            course_code = class_record["Course"]
            print "course code"
            course_info = db.courses.find_one( {"code": course_code } )
            course_dept = course_info["department"] if course_info != None else "Unknown"
            if course_dept == "Unknown":
                add_unknown_course(course_code, class_record["Course Title"])
            print "course title"

            student = db.students.find_one( {"id" : class_record["StudentID"]} )
            #if student not in database, set up a dictionary for all student info

            "fkrgiofjoeg".strip("12345")
            new = student == None
            if new:
                student = {}
                student['id'] = class_record["StudentID"]
                student['first_name'] = class_record["FirstName"]
                student['last_name'] = class_record["LastName"]
                student['username'] = remove_stuyedu(class_record["Email"])
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
        except:
            ret = True
    return ret

def get_id(email):
    user = remove_stuyedu(email)
    result = db.students.find_one({"username" : user})
    if result == None:
        return -1
    return result["id"]

# args: string student OSIS number
# return: student document as a dictionary
def get_student(student_id):
    return db.students.find_one( {"id" : student_id} )

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

# args: current grade (9, 10, 11, 12)
# returns: cohort (year of freshman year)
def grade_to_cohort(grade):
    this_year = datetime.datetime.now().year
    offset = grade - 9 + 1
    return this_year - offset

# args: cohort (year of freshman year)
# returns: current grade (9, 10, 11, 12)
def cohort_to_grade(cohort):
    this_year = datetime.datetime.now().year
    offset = this_year - cohort - 1
    return 9 + offset

# args: string course code
# return: course document
def get_course(code):
    return db.courses.find_one({"code" : code})

def add_unknown_course(code, name):
    course = {}
    course["code"] = code
    course["name"] = name
    course["department"] = "Unknown"
    course["is_AP"] = is_AP(course["code"])
    course["weight"] = get_weight(course["code"])
    course["prereq_courses"] = []
    course["prereq_overall_average"] = 0
    course["prereq_department_averages"] = []
    course["grade_levels"] = [9, 10, 11, 12]
    db.courses.insert_one(course)

def get_problematic_courses():
    courses = db.courses.find({"department" : "Unknown"})
    ret = []
    for c in courses:
        ret.append(c["code"])
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

# args: department name
# returns: list of courses in the dept
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
        if "exceptions" in course_code:
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

def set_admin_list(lis):
    db.admins.update_one( {"name" : "other"},
                          {"$set" : {"emails" : lis} } )

def get_admin_list():
    return db.admins.find_one({"name" : "other"})["emails"]

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

def reset_db():
    drop_db()
    initialize()

#returns string that is in csv format
def export():
    most_APs = 4
    ret = ""
    student = db.students.find()
    for s in student:
        fname = s["first_name"]
        lname = s["last_name"]
        osis = s["id"]
        cohort = s["cohort"]
        try:
            selections = s["selection"]
            if len(selections) > most_APs:
                most_APs = len(selections)
            row = ",".join( [str(fname), str(lname), str(osis), str(cohort), str(",".join(selections))] )
        except:
            row = ",".join( [str(fname), str(lname), str(osis), str(cohort), " "] )
        ret += row + "\n"
    heading = "first_name,last_name,id,cohort,"
    heading += ",".join( ["selection" + str(x + 1) for x in range(most_APs)] )
    ret = heading + "\n" + ret
    return ret
