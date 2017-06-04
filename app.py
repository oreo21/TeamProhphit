import os, sys, random, csv
from flask import Flask, render_template, url_for, request, redirect, session
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

@app.route('/login/', methods = ['POST', 'GET'])
def oauth_testing():
    flow = flow_from_clientsecrets('client_secrets.json',
                                   scope = 'https://www.googleapis.com/auth/userinfo.email',
                                   redirect_uri = url_for('oauth_testing', _external = True))

    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url() # This is the url for the nice google login page
        return redirect(auth_uri) # Redirects to that page
    else: # That login page will redirect to this page but with a code in the request arguments
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code) # This is step two authentication to get the code and store the credentials in a credentials object
        session['credentials'] = credentials.to_json() # Converts the credentials to json and stores it in the session variable
        return redirect(url_for('sample_info_route'))

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

        if c["hd"] == "stuy.edu":
            if c['email'] in adminlist:
                session['admin'] = c["email"]
            else:
                session['student'] = c["email"]
            return redirect("/")
        else:
            return redirect(url_for("/"), message="please login with your stuy.edu email")
        # for thing in c:
        #     print thing
        #     print c[thing]
        # print c['email']
        # return c['email'] # Return the email


@app.route('/')
# @app.route('/login/')
def home():
    if 'admin' in session:
        return redirect(url_for('admin_home'))
    elif 'student' in session:
        return redirect(url_for('student_home'))
    else:
        on = (db_manager.get_site_status() == 'on')
        return render_template('student_login.html', on=on)

@app.route('/admin-login/')
def adminLogin():
    if 'admin' in session:
        return redirect(url_for('admin_home'))
    elif 'student' in session:
        return redirect(url_for('student_home'))
    else:
        return render_template('admin_login.html')

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
        session['success'] = "Admin successfully added."
    return ret

def passCheck(password):

    if len(password) < 8:
        return False

    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = 'ABCDEFGHIJKLMNOPQRSTUVQXYZ'
    nums = '0123456789'

    ret = [0 if x in lower else 1 if x in upper else 2 if x in nums else 3 for x in password]
    return 0 in ret and 1 in ret and 2 in ret

@app.route('/logout/')
def logout():
    if 'admin' in session:
        session.pop('admin')
    if 'student' in session:
        session.pop('student')
    return redirect(url_for('home'))

@app.route('/student_home/')
def student_home():
    #NOTE: dummy variables for now
    if 'student' not in session:
        return redirect(url_for('oauth_testing'))
    numAps = 3
    aps = ['first','second','third','fourth','fifth']
    return render_template('student_home.html', numAps = numAps, aps=aps)

#NOTE: should allow students to sign up for class
@app.route('/signup/', methods=['POST'])
def signup():
    return redirect(url_for('home'))

@app.route('/admin_home/')
def admin_home():
    if 'admin' not in session:
        return redirect(url_for('oauth_testing'))
    courses = db_manager.get_APs()
    #print courses
    getdept = db_manager.list_departments_AP()
    cohorts = ['2017','2018','2019','2020']
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

@app.route('/categorize/')
def categorize():
    noProblems = False
    courses = db_manager.get_problematic_courses()
    if len(courses) <= 0:
        noProblems = True
    depts = db_manager.list_departments()
    return render_template('categorize.html',courses=courses, depts=depts, noProblems = noProblems, fxn=db_manager.get_course)

@app.route('/categorizeForm/', methods=['POST'])
def categorizeForm():
    print request.form
    for course in request.form:
        db_manager.edit_course(course, "department", request.form[course])
    session['success'] = "Courses successfully categorized!"
    return redirect(url_for('home'))

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
        print 'clear students'
        session['success'] = "Students Cleared"
    elif 'export' in request.form:
        print 'export'
        session['success'] = "Exported"

    return redirect(url_for('admin_home'))

@app.route("/search/")
def search():
    query = request.query_string[7:]
    results = db_manager.get_student(query)
    courses = db_manager.get_APs()
    getdept = db_manager.list_departments_AP()
    return render_template("search.html",student=results, osis=query, courses=courses, depts=getdept, myfxn=db_manager.get_course)

@app.route("/modify_student/", methods = ['POST'])
def modify_student():
    #cohort
    if 'cohort' in request.form:
        cohort = request.form['cohort']
    #selections; returns list
    if 'selections' in request.form:
        selections = request.form.getlist('selections')
    #exceptions; returns list
    if 'exceptions' in request.form:
        exceptions = request.form.getlist('exceptions')
    #number of aps
    if 'amount' in request.form:
        amount = request.form['amount']
    session['success'] = "Student successfully modified!"
    return redirect(url_for('home'))

@app.route("/delete_student/", methods = ['POST'])
def delete_student():
    return redirect(url_for('home'))

@app.route('/rm_courses/', methods=["POST"])
def rm_course():
    #returns list
    courses = request.form.getlist('course')
    #NOTE: function to remove course
    return redirect(url_for('home'))

@app.route('/rm_cohort/', methods=["POST"])
def rm_cohort():
    cohort = request.form['cohort']
    session['success'] = "Cohort %s successfully deleted!"%cohort
    return redirect(url_for('home'))

#options for editing course
@app.route('/mod/<course>/')
def mod(course):
    #NOTE: will eventually be list of courses in same dep't that can be prereqs
    courses = ['HGS44XE','HGS44XW','HPS21X']
    course_info = db_manager.get_course(course)
    #hardcoded for now
    cohorts = ['2017','2016','2015','2014']
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
#<!-- name, code, department, is_AP, weight, prereq_courses, prereq_overall_average, prereq_department_averages, grade_levels -->
#example of how to deal w/file
@app.route('/testForm/', methods=['POST'])
def testForm():
    #if there's a file uploaded
    if 'upload' in request.files:
        #get the file
        filedata  = request.files['upload']
        db_manager.add_courses(filedata)
        session['success'] = "Transcript uploaded succesfully!"
        #go to student home
        return redirect(url_for("admin_home"))
    #if the file is missing
    else:
        return redirect(url_for("add"))

@app.route('/adddeptadmin/')
def addadmin():
    email = request.form["email"]
    if email != request.form["checkEmail"]:
        return render_template("admin_home.html", message="the emails you've entered do not match.")
    else:
        p = hashlib.sha512(request.form["pass"])
        if p == hashlib.sha512(request.form["checkpass"]):
            #set admin fxn
            return render_template("admin_home.html", message="added new admin successfully.")
        return render_template("admin_home.html", message="the passwords you've entered do not match.")

@app.route('/validateCSV/', methods=['POST'])
def validateCSV():
    #get error message (debugging only)
    db_manager.add_departments(request.form['f'])
    db_manager.add_courses(request.form['f'])
    try:
        csv = csv.reader(request.form['f'])
        db_manager.add_departments(request.form['f'])
        db_manager.add_courses(request.form['f'])
        session['success'] = "Courses uploaded succesfully!"
        ret = ''
    except:
        return 'Error. CSV is in invalid form.'

if __name__ == '__main__':
    app.debug = True
    app.run()
