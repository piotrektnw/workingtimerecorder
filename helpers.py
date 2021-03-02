import os

import urllib.parse
import sqlite3
from flask import Flask, redirect, render_template, request, session
from functools import wraps
from flask_mail import Mail, Message
app = Flask(__name__)

mail= Mail(app)
app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'piotrekcs50x@outlook.com'
app.config['MAIL_PASSWORD'] = 'cs50xcs50x'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
mail = Mail(app)

def login_required(f):
    """
    Decorate routes to require login.
    Sources: CS50 PSET9: Finance, Author: CS50 authors 
    https://cs50.harvard.edu/x/2021/psets/9/finance/

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

conn = sqlite3.connect("wtr.db", check_same_thread=False)
c = conn.cursor()
conn.commit()

#prepare list of users
def makeActiveUsers():
    c.execute("SELECT nick FROM users")
    conn.commit()
    users = c.fetchall()
    activeUsers = [d[0] for d in users]
    return activeUsers

def send_email():

    with mail.connect() as mailcon:                     
        message = Message("Working time check", recipients=['piotrekcs50x@outlook.com'])
        message.body = "This is working time alert message. Check your database."
        mailcon.send(message)

def access():
    password = 'cs50xcs50x'
    os.getenv(password)

