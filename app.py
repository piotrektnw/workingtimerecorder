import os
import sqlite3
import datetime
import math
from datetime import datetime, timedelta
from tempfile import mkdtemp
from flask_session import Session
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message

from helpers import login_required, access, send_email, makeActiveUsers
app = Flask(__name__)

au = makeActiveUsers()

# Source: 
# adapted from: Source: CS50 PSET9: Finance, Author: CS50 authors (https://cs50.harvard.edu/x/2021/psets/9/finance/)
mail= Mail(app)
app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'piotrekcs50x@outlook.com'
app.config['MAIL_PASSWORD'] = access()
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
mail = Mail(app)

app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configure session to use filesystem (instead of signed cookies)
# Source: CS50 Finance created by CS50 staff
# From: https://cs50.harvard.edu/x/2021/psets/9/finance/
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# database connection for whole program
conn = sqlite3.connect("wtr.db", check_same_thread=False)
c = conn.cursor()
conn.commit()

@app.route("/index", methods=["GET", "POST"])
@login_required

def index():
    if request.method == "GET":
        au = makeActiveUsers()
        currentUser = session.get('b', None)
        userIsAdmin = session.get('userIsAdmin', None) 

        return render_template("index.html", au=au, userIsAdmin=userIsAdmin, currentUser=currentUser)
    
    else:
        au = makeActiveUsers()
        # list of alerts to trigger events in frontend 
        breakTaken = False
        displayCheck = False
        shortCheck = False
        workTimeAlert = False
        noRowAlert = False
               
        userIsAdmin = session.get('userIsAdmin', None)  
        currentUser = session.get('b', None)
        # collect user input
        display = request.form.get("display")
        show = request.form.get("show")
        user = request.form.get("user")
        short = request.form.get("short")
        clear = request.form.get("clear")

        if userIsAdmin:
            if display == "displayClicked":    
                displayCheck = True     
            if short == "shortClicked":
                shortCheck = True   
            if clear == "clearClicked":
                c.execute("DELETE FROM entrances")
            
            #extract needed data to display table
            c.execute("SELECT time(start), time(stop), duration, username, status FROM entrances") 
    
            time_val = c.fetchall()
            started = [z[0] for z in time_val]
            stopped = [z[1] for z in time_val]
            duration = [z[2] for z in time_val]
            username = [z[3] for z in time_val]
            status = [z[4] for z in time_val]
               
            # filter by username
            if show == "detailsClicked":
                displayCheck = True
                c.execute("SELECT username FROM entrances WHERE username=?", (user,))
                time_val2 = c.fetchall()
                username = [z[0] for z in time_val2]

            conn.commit() 

            # zip all data extracted from db
            timing = zip(started, stopped, duration, username, status) 
            return render_template("index.html", shortCheck=shortCheck, currentUser=currentUser, au=au, timing=timing, userIsAdmin=userIsAdmin, displayCheck=displayCheck)

        else: 
            
            # time limit prototype (default is 8 hours)
            limit = timedelta (
                seconds=5
            )
            durationDelta = limit

            # collect user input
            start = request.form.get("start")
            stop = request.form.get("stop")
            break15 = request.form.get("break15")     

            # default break value to be inserted to database
            x = 0

            # collect data from user input
            if start == "startClicked":
                c.execute("INSERT INTO entrances (start, userId, username, status, break) VALUES (julianday('now'), ?, ?, ?, ?)", (currentUser, currentUser, 1, x))

            # extract current row and current stop value
            c.execute("SELECT rowid, stop FROM entrances WHERE userId=? ORDER BY rowid DESC LIMIT 1", (currentUser,))  
              
            last_row = c.fetchone()
            if last_row == None:
                noRowAlert = True
                return render_template("error.html", noRowAlert=noRowAlert)
      
            current_no = last_row[0] 
            
            current_stop = last_row[1]

            # update db if break taken 
            # default break time: 30 min, for testing purposes: 5 seconds
            if break15 == "break15Clicked":
                x = 5
                c.execute("UPDATE entrances SET break=? WHERE rowid=?", (x, current_no))
                breakTaken = True   

            # use current_stop value to prevent double scan
            # support multiple users using system at once
            if (stop == "stopClicked" and current_stop == None):
                c.execute("UPDATE entrances SET stop=julianday('now') WHERE rowid=?", (current_no,))    

            # collect data for table display
            c.execute("SELECT datetime(start), datetime(stop), username, break FROM entrances WHERE username=?", (currentUser,))
            
            time_val = c.fetchall()
            started = [z[0] for z in time_val]
            stopped = [z[1] for z in time_val]
            username = [z[2] for z in time_val]
            breaks = [z[3] for z in time_val]
            userRecordQty = len(stopped)

            if stop == "stopClicked" and current_stop == None:
                
                # count work time duration
                # support overnight shifts
                FMT = '%Y-%m-%d %H:%M:%S'
                durationDelta = (datetime.strptime(stopped[userRecordQty-1], FMT) - datetime.strptime(started[userRecordQty-1], FMT)) - timedelta(seconds = breaks[userRecordQty-1]) 
                c.execute("UPDATE entrances SET duration=? WHERE rowid=?", (str(durationDelta), current_no))
                if durationDelta < timedelta(seconds = breaks[userRecordQty-1]): 
                    workTimeAlert = True
                    return render_template("error.html", workTimeAlert=workTimeAlert)

            # inform admin if work time < limit
            if durationDelta < limit:
                c.execute("UPDATE entrances SET status=? WHERE rowid=?", (2, current_no))
                send_email()
            
                                      
            # save changes to database
            conn.commit()   
            
            c.execute("SELECT duration FROM entrances WHERE userId=?", (currentUser,))  
            
            # extract duration time of current userId
            extractDuration = c.fetchall() 
            duration = [z[0] for z in extractDuration]
            
            # zip all data related to timing
            timing = zip(started, stopped, username, duration)
           
            return render_template("index.html", breakTaken=breakTaken, currentUser=currentUser, au=au, timing=timing, userIsAdmin=userIsAdmin, displayCheck=displayCheck)


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():

    """Change Password"""
    if request.method == "POST":
        
        userIsAdmin = session.get('userIsAdmin', None) 
        alertPassword = False
        alertRepPassword = False
        alertCompPassword = False
        success = False

        userpassword = request.form.get("new_password")
        reppassword = request.form.get("confirmation")

        # Ensure username and passwords were submitted
        if not userpassword:
            alertPassword = True
            return render_template("change.html", userIsAdmin=userIsAdmin, alertPassword=alertPassword)
        elif not reppassword:
            alertRepPassword = True
            return render_template("change.html", userIsAdmin=userIsAdmin, alertRepPassword=alertRepPassword)
        elif userpassword != reppassword:
            alertCompPassword = True
            return render_template("change.html", userIsAdmin=userIsAdmin, alertCompPassword=alertCompPassword)
        else:
            # hash password and update list of passwords
            hashedpass = generate_password_hash(userpassword)
            c.execute("UPDATE users SET hash=? WHERE userId=?", (hashedpass, session["user_id"]))
            success = True
            return render_template("change.html", success=success, userIsAdmin=userIsAdmin)

    else:
        userIsAdmin = session.get('userIsAdmin', None) 
        return render_template("change.html", userIsAdmin=userIsAdmin)

@app.route("/removeusers", methods=["GET", "POST"])
@login_required
def removeusers():
    
    """ Remove users module only for admin """
    if request.method == "GET":
        
        au = makeActiveUsers()
        userIsAdmin = session.get('userIsAdmin', None) 
        return render_template("remove.html", au=au, userIsAdmin=userIsAdmin)

    else:
        au = makeActiveUsers()
        removeActivate = False
        removeConfirmed = False
        noneAlert = False
        userIsAdmin = session.get('userIsAdmin', None)

        removeButton = request.form.get("removeButton")

        # ensure button was clicked
        if removeButton == "clicked":
            removeActivate = True 
            
            # removal process and verification of choice       
            userToRemove = request.form.get("user")
            if userToRemove == None:
                noneAlert = True
                return render_template("remove.html", userIsAdmin=userIsAdmin, noneAlert=noneAlert)
            
            c.execute("SELECT userId FROM users WHERE nick=?", (userToRemove,))
            a = c.fetchone()
            x = a[0]
            # clear databases
            c.execute("DELETE FROM entrances WHERE userId=?", (x,))
            c.execute("DELETE FROM users WHERE userId=?", (x,))
            conn.commit
            

            return render_template("remove.html", userIsAdmin=userIsAdmin, au=au, removeConfirmed=removeConfirmed, userToRemove=userToRemove, removeActivate=removeActivate)

@app.route("/register", methods=["GET", "POST"])
def register():
    
    """Register user"""
    if request.method == "POST":
        
        au = makeActiveUsers()
        alertUsername = False
        alertUsernameTaken = False
        alertPassword = False
        alertRepPassword = False
        alertCompPassword = False
        success = False
        nick = request.form.get("username")
        userpassword = request.form.get("password")
        reppassword = request.form.get("confirmation")
  
        # Ensure username and passwords were submitted
        if not nick:
            alert = True
            return render_template("register.html", alertUsername=alertUsername)
        # check if username already taken
        if nick in au:
            alertUsernameTaken = True
            return render_template("register.html", alertUsernameTaken=alertUsernameTaken)
        elif not userpassword:
            alertPassword = True
            return render_template("register.html", alertPassword=alertPassword)
        elif not reppassword:
            alertRepPassword = True
            return render_template("register.html", alertRepPassword=alertRepPassword)
        elif userpassword != reppassword:
            alertCompPassword = True
            return render_template("register.html", alertCompPassword=alertCompPassword)
            
        else:

            hashedpass = generate_password_hash(userpassword)
            # add new user to database
            c.execute("INSERT INTO users (nick, hash) VALUES (?,?)", (nick, hashedpass))
            conn.commit()
            success = True
            
            if success:
                return render_template("register.html", au=au, success=success)

    else:
        return render_template("register.html")



@app.route("/", methods=["GET", "POST"])
def login():
    """ Login panel """
    """ Source: CS50 Finance created by CS50 staff """ 
    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        userIsAdmin = False
        alertUsername = False
        alertPassword = False
        alert = False

        nick = request.form.get("username")
        userpassword = request.form.get("password")

        # Ensure username was submitted
        if not nick:
            alertUsername = True
            return render_template("login.html", alertUsername=alertUsername)

        # Ensure password was submitted
        elif not userpassword:
            alertPassword = True
            return render_template("login.html", alertPassword=alertPassword)

        # Query database for needed data
        c.execute("SELECT * FROM users WHERE nick = ?", (request.form.get("username"),))
        conn.commit()
        elem = c.fetchall()

        # Extract username if found
        user = [g[1] for g in elem]
  
        # Ensure username exists and password is correct
        if len(user) != 1 or not check_password_hash(elem[0][2], request.form.get("password")): 
            alert = True
            return render_template("login.html", alert=alert)    
            
        # Remember which user has logged in
        session["user_id"] = elem[0][0]
         # identify user
        
        current_user = session["user_id"]
        c.execute("SELECT nick FROM users WHERE userId=?", (current_user,))
        a = c.fetchone()
        session['b'] = currentUser = a[0]

        #extract current_userId
        if current_user == 1:
            session['userIsAdmin'] = userIsAdmin = True


        # Redirect user to home page
        return render_template("index.html", currentUser=currentUser, userIsAdmin=userIsAdmin)

    else: 
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/readme", methods=["GET"])
def readme():
    """Provide basic info about website"""
    if request.method == "GET": 
 

    # Redirect user to login form
        return render_template("readme.html")
