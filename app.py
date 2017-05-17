import os, sys, random
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

if __name__ == '__main__':
    app.debug = True
    app.run()
