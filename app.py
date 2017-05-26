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
adminlist = ["mrgrumpy@stuy.edu", "jxu9@stuy.edu"]

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
        return render_template('home.html')

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
    #if 'student' not in session:
    #    return redirect(url_for('oauth_testing'))
    numAps = 3
    aps = ['first','second','third','fourth','fifth']
    return render_template('student_home.html', numAps = numAps, aps=aps)

#NOTE: should allow students to sign up for class
@app.route('/signup/', methods=['POST'])
def signup():
    return redirect(url_for('home'))

@app.route('/admin_home/')
def admin_home():
    getdept = db_manager.list_departments()
    print getdept
    if 'admin' not in session:
        return redirect(url_for('oauth_testing'))
    courses = ['HGS44XE','HGS44XW','HPS21X']
    return render_template('admin_home.html', courses= courses, login=True, depts=getdept)

@app.route("/search/")
def search():
    query = request.form["search"]
    #results = db_manager.get_student(query)
    return render_template("search.html" ''',student=results''')
    """
{u'cohort': u'2017',
u'first_name': u'Moe',
u'last_name': u'Szyslak',
u'selections': [],
u'department_averages': {
u'Visual Arts': {u'count': 0, u'average': 0},
u'Theater': {u'count': 0, u'average': 0},
u'Science': {u'count': 0, u'average': 0},
u'Guidance': {u'count': 0, u'average': 0},
u'Functional Codes': {u'count': 0, u'average': 0},
u'PE and Health': {u'count': 0, u'average': 0},
u'Human Services ': {u'count': 0, u'average': 0},
u'Music': {u'count': 0, u'average': 0},
u'English/ESL': {u'count': 0, u'average': 0},
u'Social Studies': {u'count': 0, u'average': 0},
u'Mathematics': {u'count': 0, u'average': 0},
u'Technology': {u'count': 0, u'average': 0},
u'LOTE': {u'count': 0, u'average': 0},
u'Career Development': {u'count': 0, u'average': 0}
},
u'classes_taken': {
u'Visual Arts': [],
u'Theater': [],
u'Science': [],
u'Guidance': [],
u'Functional Codes': [],
u'PE and Health': [],
u'Social Studies': [],
u'Music': [],
u'English/ESL': [],
u'Unknown': [
{
u'code': u'SLN11A',
u'weight': 1,
u'mark': u'98'
},
{
u'code': u'MEN11A',
u'weight': 1,
u'mark': u'100'
}
],
u'Human Services ': [],
u'Mathematics': [],
u'Technology': [],
u'LOTE': [],
u'Career Development': []
},
u'_id': ObjectId('592649559478151726b3c26d'),
u'overall_average': 0,
u'id': u'111111128'}

    """
@app.route('/rm/')
def rm():
    course = request.form['course']
    #NOTE: function to remove course
    return redirect(url_for('home'))

@app.route('/mod/<course>/')
def mod(course):
    #NOTE: will eventually be list of courses in same dep't that can be prereqs
    courses = ['HGS44XE','HGS44XW','HPS21X']
    return render_template('modify.html',course=str(course),courses=courses)

@app.route('/modifyCourse/')
def modifyCourse():
    #NOTE: deal w/adding prereqs later
    return redirect(url_for('adHome'))

#example of how to deal w/file
@app.route('/testForm/', methods=['POST'])
def testForm():
    #if there's a file uploaded
    if 'upload' in request.files:
        #get the file
        filedata  = request.files['upload']
        db_manager.add_students(filedata)
        #go to student home
        return redirect(url_for("admin_home"))
    #if the file is missing
    else:
        return redirect(url_for("add"))

if __name__ == '__main__':
    app.debug = True
    app.run()
