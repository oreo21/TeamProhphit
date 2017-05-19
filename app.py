import os, sys, random, csv
from flask import Flask, render_template, url_for, request, redirect, session
from utils import auth

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route('/')
@app.route('/login/')
def login():
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/home/')
def home():
    if 'user' in session:
        return render_template('home.html', user = session['user'])
    else:
        return redirect(url_for('login'))

@app.route('/authenticate/', methods = ['POST'])
def authenticate():
    u = request.form['username']
    p = request.form['password']
    a = request.form['action']
    data = auth.authenticate([u, p, a])
    if data[1]:
        session['user'] = u
        return redirect(url_for('home'))
    else:
        return render_template('login.html', messageLogin = data[0])

@app.route('/logout/')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))

@app.route('/studentHome')
def studentHome():
    return render_template('stuHome.html')

#NOTE: should allow students to sign up for class
@app.route('/signup/')
def signup():
    return redirect(url_for('home'))

@app.route('/adHome')
def adHome():
    return render_template('adHome')

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
