import os, sys, random, csv
from flask import Flask, render_template, url_for, request, redirect, session
from utils import auth
from utils import db_manager

#oauth imports and stuff
from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials # OAuth library, import the function and class that this uses
from httplib2 import Http # The http library to issue REST calls to the oauth api

import json # Json library to handle replies

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config.update(dict( # Make sure the secret key is set for use of the session variable
    SECRET_KEY = 'secret'
    ))
adminlist = ["jxu9@stuy.edu", "vmavromatis@stuy.edu"]

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
        return render_template('student_login.html')

@app.route('/admin-login/')
def adminLogin():
    if 'admin' in session:
        return redirect(url_for('admin_home'))
    elif 'student' in session:
        return redirect(url_for('student_home'))
    else:
        return render_template('admin_login.html')

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

    return render_template('admin_home.html', courses= courses, login=True, depts=getdept, cohorts=cohorts, myfxn=db_manager.get_course, problems=problems, success=success)

@app.route('/categorize/')
def categorize():
    noProblems = False
    courses = db_manager.get_problematic_courses()
    if len(courses) <= 0:
        noProblems = True
    depts = db_manager.list_departments()
    print noProblems
    return render_template('categorize.html',courses=courses, depts=depts, noProblems = noProblems)

@app.route('/categorizeForm/', methods=['POST'])
def categorizeForm():
    for course in request.form:
        db_manager.edit_course(course, "department", request.form[i])
    session['success'] = "Courses successfully categorized!"
    return redirect(url_for('home'))

@app.route("/settings/", methods=['POST'])
def settings():
    if 'shut_down' in request.form:
        #shut down function
        print 'shut down'
    else:
        #export
        print 'export'
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
    return render_template('modify.html',course=str(course),courses=courses,course_info = course_info, special=True, cohorts=cohorts)

#does actual editing of course
@app.route('/modifyCourse/', methods = ['POST', 'GET'])
def modifyCourse():
    minGPA = request.form["minGPA"]
    mindept = request.form["minDept"]
    cohort = request.form["cohort"]
    prereqs = request.form["prereq"]
    course = request.form["course"]

    db_manager.edit_course(course, "prereq_overall_average", minGPA)
    db_manager.edit_course(course, "prereq_department_averages", minDept)
    db_manager.edit_course(course, "grade_levels", cohort)
    db_manager.edit_course(course, "prereq_courses", prereq)

    session['success'] = "Courses modified successfully!"
    return redirect(url_for('adHome'))
#<!-- name, code, department, is_AP, weight, prereq_courses, prereq_overall_average, prereq_department_averages, grade_levels -->
#example of how to deal w/file
@app.route('/testForm/', methods=['POST'])
def testForm():
    #if there's a file uploaded
    if 'upload' in request.files:
        #get the file
        filedata  = request.files['upload']
        db_manager.add_students(filedata)
        session['success'] = True
        #go to student home
        return redirect(url_for("admin_home"))
    #if the file is missing
    else:
        return redirect(url_for("add"))

if __name__ == '__main__':
    app.debug = True
    app.run()
