import os, sys, random, csv
from flask import Flask, render_template, url_for, request, redirect, session, make_response
from utils import auth
from utils import db_manager
import hashlib
#oauth imports and stuff
from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials # OAuth library, import the function and class that this uses
from httplib2 import Http # The http library to issue REST calls to the oauth api

import json # Json library to handle replies

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config.update(dict( # Make sure the secret key is set for use of the session variable
    SECRET_KEY = 'secret'
    ))

adminlist = ["vmavromatis@stuy.edu"]

#oauth login
@app.route('/login/', methods = ['POST', 'GET'])
def oauth_testing():
    flow = flow_from_clientsecrets('client_secrets.json',
                                   scope = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email'],
                                   redirect_uri = url_for('oauth_testing', _external = True))

    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url() # This is the url for the nice google login page
        return redirect(auth_uri) # Redirects to that page
    else: # That login page will redirect to this page but with a code in the request arguments
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code) # This is step two authentication to get the code and store the credentials in a credentials object
        session['credentials'] = credentials.to_json() # Converts the credentials to json and stores it in the session variable
        return redirect(url_for('sample_info_route'))

#oauth stuff
@app.route('/auth/', methods = ['POST', 'GET'])
def sample_info_route():
    if 'credentials' not in session: # If the credentials are not here, user must login
        return redirect(url_for('oauth_testing'))

    credentials = OAuth2Credentials.from_json(session['credentials']) # Loads the credentials from the session

    if credentials.access_token_expired: # If the credentials have expired, login
        return redirect(url_for('oauth_testing'))
    else:
        http_auth = credentials.authorize(Http()) # This will authorize this http_auth object to make authenticated calls to an oauth api

        response, content = http_auth.request('https://www.googleapis.com/oauth2/v1/userinfo?alt=json') # Issues a request to the google oauth api to get user information

        c = json.loads(content) # Load the response
        # for thing in c:
        #     print "this is the key below"
        #     print thing
            # print
            # print "this is the value below"
            # print c[thing]
        # return c['email'] # Return the email

        if c["hd"] == "stuy.edu":
            if c['email'] in adminlist:
                session['admin'] = c["email"]
            else:
                session['student'] = c["email"]
            return redirect("/")
        else:
            return redirect(url_for("/"), message="please login with your stuy.edu email")


#home; redirects where you should be
@app.route('/')
def home():
    if 'admin' in session:
        return redirect(url_for('admin_home'))
    elif 'student' in session:
        return redirect(url_for('student_home'))
    else:
        on = (db_manager.get_site_status() == 'on')
        return render_template('student_login.html', on=on)

#admin login
@app.route('/admin-login/')
def adminLogin():
    if 'admin' in session:
        return redirect(url_for('admin_home'))
    elif 'student' in session:
        return redirect(url_for('student_home'))
    else:
        return render_template('admin_login.html')

#checks if all your information checks out
@app.route('/checkMatch/', methods=['POST'])
def checkMatch():
    if len(request.form['email1']) == 0:
        ret = "Please fill in e-mail."
    elif not request.form['email1'].endswith("@stuy.edu"):
        ret = "Please use your stuy.edu e-mail."
    elif request.form['email1'] != request.form['email2']:
        ret = "E-mails don't match."
    elif len(request.form['pass1']) == 0:
        ret = "Please enter password."
    elif request.form['pass1'] != request.form['pass2']:
        ret = "Passwords don't match."
    elif not passCheck(request.form['pass1']):
        ret = "Please enter a stronger passwords. Passwords must include at least one uppercase letter, one lowercase letter, and one number, and must be 8 character long."
    else:
        ret = ''
        email = request.form["email1"]
        p = hashlib.sha512(request.form["pass1"])
        db_manager.set_admin_list(db_manager.get_admin_list().append(email)) #UNICORN (idk if this work)
        session['success'] = "Admin successfully added."
    return ret

#checks if your password is good
def passCheck(password):
    #length
    if len(password) < 8:
        return False
    #diff categories
    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = 'ABCDEFGHIJKLMNOPQRSTUVQXYZ'
    nums = '0123456789'
    #check
    ret = [0 if x in lower else 1 if x in upper else 2 if x in nums else 3 for x in password]
    return 0 in ret and 1 in ret and 2 in ret

#will only be run *after* Check Match, which accounts for checking info
@app.route('/adddeptadmin/', methods=["POST"])
def addadmin():
    email = request.form["email1"]
    p = hashlib.sha512(request.form["pass1"]) #UNICORN (we're not adding the admin lmao)
    session['success'] = "%s successfully added as admin."%str(email)
    return redirect(url_for('home'))

@app.route('/logout/')
def logout():
    if 'admin' in session:
        session.pop('admin')
    if 'student' in session:
        session.pop('student')
    return redirect(url_for('home'))

#student home
@app.route('/student_home/')
def student_home():
    if 'student' not in session:
        return redirect(url_for('home'))

    print session["student"]
    osis = db_manager.get_id(session["student"])

    student = db_manager.get_student(osis)
    num = db_manager.get_num_APs(osis)
    #print student
    #overallavg = student["overall_average"]
    #aps = ['one','two','three','four','five']
    selectedCourses = student["selections"]
    #student = db_manager.get_student(db_manager.get_id(session["student"]))
    #get_applicable_APs(student_id)
    #student["id"] for osis
    aps = db_manager.get_applicable_APs(osis)
    return render_template('student_home.html', numAps = num, aps=aps, selectedCourses=selectedCourses)

#NOTE: should allow students to sign up for class
@app.route('/signup/', methods=["POST"])
def signup():
    #print request.form["ap0"]
    session['signedUp'] = True
    signedup = []
    osis = db_manager.get_id(session["student"])
    for i in request.form:
        signedup.append(request.form[i])
    # for item in request.form:
    #     print "this is an item" + str(item)
    #code for getting the options
    # for i in range(10):
    #     index = "ap" + str(i)
    #     if request.form[index]:
    #         print "hi"
    #         signedup.append(request.form[index])

    db_manager.edit_student(osis, "selections", signedup)
    return redirect(url_for('home'))

#admin home
@app.route('/admin_home/')
def admin_home():
    if 'admin' not in session:
        return redirect(url_for('oauth_testing'))
    courses = db_manager.get_APs()
    #print courses
    getdept = db_manager.list_departments_AP()
    cohorts = [db_manager.grade_to_cohort(9),db_manager.grade_to_cohort(10),db_manager.grade_to_cohort(11),db_manager.grade_to_cohort(12)] #UNICORN

    problems = db_manager.get_problematic_courses()
    if len(problems) > 0:
        problems = True
    else:
        problems = False

    success = False

    if 'success' in session:
        success = session['success']
        session.pop('success')

    on = (db_manager.get_site_status()=='on')

    return render_template('admin_home.html', courses= courses, login=True, depts=getdept, cohorts=cohorts, myfxn=db_manager.get_course, problems=problems, success=success, on=on)

#generate categorize form
@app.route('/categorize/')
def categorize():
    noProblems = False
    courses = db_manager.get_problematic_courses()
    if len(courses) <= 0:
        noProblems = True
    depts = db_manager.list_departments()
    return render_template('categorize.html',courses=courses, depts=depts, noProblems = noProblems, fxn=db_manager.get_course)

#categorize problematic courses
@app.route('/categorizeForm/', methods=['POST'])
def categorizeForm():
    #print request.form
    for course in request.form:
        db_manager.edit_course(course, "department", request.form[course])
    session['success'] = "Courses successfully categorized!"
    return redirect(url_for('home'))

#all settings functions
@app.route("/settings/", methods=['POST'])
def settings():
    if 'shut_down' in request.form:
        db_manager.set_site_status('off')
        session['success'] = 'Site shut down successfully'
    elif 'turn_on' in request.form:
        db_manager.set_site_status('on')
        session['success'] = 'Site turned on successfully'
    elif 'clear_db' in request.form:
        db_manager.reset_db()
        session['success'] = 'DB Cleared'
    elif 'clear_students' in request.form:
        print 'clear students' #UNICORN
        session['success'] = "Students Cleared"
    elif 'export' in request.form:
        response = make_response(db_manager.export())
        cd = 'attachment; filename=studentSelections.csv'
        response.mimetype='text/csv'
        response.headers['Content-Disposition'] = cd
        return response

    return redirect(url_for('admin_home'))

#search
@app.route("/search/")
def search():
    query = request.query_string[7:]
    results = db_manager.get_student(query)
    courses = db_manager.get_APs()
    getdept = db_manager.list_departments_AP()
    return render_template("search.html",student=results, osis=query, courses=courses, depts=getdept, myfxn=db_manager.get_course)

#modify student
@app.route("/modify_student/", methods = ['POST'])
def modify_student():
    #cohort
    if 'cohort' in request.form:
        cohort = request.form['cohort'] #UNICORN
    #selections; returns list
    if 'selections' in request.form:
        selections = request.form.getlist('selections') #UNICORN
    #exceptions; returns list
    if 'exceptions' in request.form:
        exceptions = request.form.getlist('exceptions') #UNICORN
    #number of aps
    if 'amount' in request.form:
        amount = request.form['amount'] #UNICORN
    session['success'] = "Student successfully modified!"
    return redirect(url_for('home'))

#delete students
@app.route("/delete_student/", methods = ['POST'])
def delete_student(): #UNICORN
    return redirect(url_for('home'))

#remove courses
@app.route('/rm_courses/', methods=["POST"])
def rm_course():
    #returns list
    courses = request.form.getlist('course')
    #NOTE: function to remove course
    session['succes'] = "Course removed." #UNICORN
    return redirect(url_for('home'))

#remove cohort
@app.route('/rm_cohort/', methods=["POST"])
def rm_cohort():
    cohort = request.form['cohort'] #UNICORN
    session['success'] = "Cohort %s successfully deleted!"%cohort
    return redirect(url_for('home'))

#options for editing course
@app.route('/mod/<course>/')
def mod(course):
    #NOTE: will eventually be list of courses in same dep't that can be prereqs
    courses = ['HGS44XE','HGS44XW','HPS21X'] #UNICORN
    course_info = db_manager.get_course(course)
    #hardcoded for now
    cohorts = ['2017','2016','2015','2014'] #UNICORN
    depts = db_manager.list_departments()
    return render_template('modify.html',course=str(course),courses=courses,course_info = course_info, special=True, cohorts=cohorts, depts=depts)

#does actual editing of course
@app.route('/modifyCourse/', methods = ['POST'])
def modifyCourse():
    dept = db_manager.list_departments()

    course = request.form['course']

    if 'minGPA' in request.form:
        minGPA = request.form["minGPA"]
        db_manager.edit_course(course, "prereq_overall_average", minGPA)
    if 'minDept' in request.form:
        minDept = request.form["minDept"]
        db_manager.edit_course(course, "prereq_department_averages", minDept)
    if 'cohort' in request.form:
        cohort = request.form["cohort"]
        db_manager.edit_course(course, "grade_levels", cohort)
    if 'prereq' in request.form:
        prereqs = request.form["prereq"]
        db_manager.edit_course(course, "prereq_courses", prereq)

    for i in request.form:
        if i in dept and request.form[i]:
            #i is the department, request.form[i] is the grade
            print i + " : " + request.form[i]
            #db_manager.edit_course(course, "prereq_department_averages", minDept)

    session['success'] = "Courses modified successfully!"
    return redirect(url_for('home'))

#function to add courses
@app.route('/validateCSV/', methods=['POST'])
def validateCSV():
    try:
        #read file
        fil = request.files['f'].read()
        #return file
        ret = []
        #split file by lines
        data = fil.split('\n')
        #get headers
        headers = []
        for i in data[0].split(','):
            headers.append(i.strip())
        for line in data[1:]:
            l = line.split(',')
            info = {}
            i = 0
            for category in headers:
                info[category] = l[i].strip()
                i += 1
                if i >= len(l):
                    break
            ret.append(info)
        dept = db_manager.add_departments(ret)
        course = db_manager.add_courses(ret)
        deptMsg = courseMsg = ""
        if dept:
            deptMsg = " Some departments failed to add."
        if course:
            courseMsg = " Some courses faield to add."
        msg = "Courses uploaded succesfully!%s%s"%(deptMsg,courseMsg)
        session['success'] = msg
        print "success??"
        return ''
    #bad file
    except:
        return 'Error. CSV is in invalid form.'

#functions to add students
@app.route('/validateTranscript/', methods=['POST'])
def validateTranscript():
    try:
        #read file
        fil = request.files['f'].read()
        #return file
        ret = []
        #split file by lines
        data = fil.split('\r\n')
        #get headers
        headers = []
        for i in data[0].split(','):
            headers.append(i.strip())
        for line in data[1:]:
            l = line.split(',')
            info = {}
            i = 0
            for category in headers:
                info[category] = l[i].strip()
                i += 1
                if i >= len(l):
                    break
            ret.append(info)
        fail = db_manager.add_students(ret)
        failMsg = ""
        if fail > 0:
            failMsg = "Some transcripts failed to add!"
        session['success'] = "Transcripts uploaded succesfully! %s"%failMsg
        return ''
    #bad file
    except:
        return 'Error. CSV is in invalid form.'

if __name__ == '__main__':
    app.debug = True
    app.run()
