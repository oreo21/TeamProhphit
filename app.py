from flask import Flask, render_template, session, request, redirect, url_for, flash


app = Flask(__name__)

@app.route("/", methods = ['GET', 'POST'])
def home():
  if "username" in session:
    usertype = #function for getting user type
    if usertype == 0: #change 0 to whatever boolean we set to differentiate
      #blah
    elif usertype == 1:
      #not the other usertype

    return render_template("home.html", user_type = usertype)
  else:
return render_template("home.html")
