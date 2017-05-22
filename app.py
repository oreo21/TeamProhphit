import os, sys, random, csv
from flask import Flask, render_template, url_for, request, redirect, session
from utils import auth

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route('/')
@app.route('/login/')
def login():
    if 'user' in session:
        t = session['acct_type']
        if t == 'student':
            return redirect(url_for('student_home'))
        elif t == 'admin':
            return redirect(url_for('admin_home'))
    else:
        if t == 'student':
            return render_template('student_login.html')
        elif t == 'admin':
            return render_template('admin_login.html')

'''            
@app.route('/home/')
def home():
    if 'user' in session:
        return render_template('home.html', user = session['user'])
    else:
        return redirect(url_for('login'))
'''

@app.route('/authenticate/', methods = ['POST'])
def authenticate():
    u = request.form['username']
    p = request.form['password']
    t = request.form['acct_type']
    data = auth.login(u, p, t)
    if data[1]: # login successful
        session['user'] = u
        session['acct_type'] = t
        if t == 'student':
            return redirect(url_for('student_home'))
        elif t == 'admin':
            return redirect(url_for('admin_home'))
    else:
        if t == 'student':
            return render_template('student_login.html', messageLogin = data[0])
        elif t == 'admin':
            return render_template('admin_login.html', messageLogin = data[0])

@app.route('/logout/')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))

@app.route('/student_home/')
def student_home():
    #NOTE: dummy variables for now
    numAps = 3
    aps = ['HGS44XE','HGS44XW','HPS21X']
    return render_template('student_home.html', user = session['user'], numAps = numAps, aps=aps)

#NOTE: should allow students to sign up for class
@app.route('/signup/', methods=['POST'])
def signup():
    return redirect(url_for('home'))

@app.route('/admin_home/')
def admin_home():
    return render_template('admin_home.html', user = session['user'])

@app.route('/add/')
def add():
    return render_template('add.html')

@app.route('/remove/')
def remove():
    #NOTE: dummy courses
    courses = ['HGS44XE','HGS44XW','HPS21X']
    return render_template('remove.html')

@app.route('/rm/')
def rm():
    course = request.form['course']
    #NOTE: function to remove course
    return redirect(url_for('home'))

@app.route('/modifyChoose/')
def modifyChoose():
    #NOTE: will eventually be list of actual available courses
    courses = ['HGS44XE','HGS44XW','HPS21X']
    return render_template('modifyChoose.html',courses=courses)

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
        #read the file
        csvreader = csv.reader(filedata)
        #print the file
        for row in csvreader:
            print row
        #go to student home
        return redirect(url_for("adminHome"))
    #if the file is missing
    else:
        return redirect(url_for("add"))

if __name__ == '__main__':
    app.debug = True
    app.run()
