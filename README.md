# WEB APPLICATION REGISTERING EMPLOYEES WORKING TIME - **'WTR' - WORKING TIME RECORDER** 		
#### 22.02.2021r. Krakow, Poland


#### Description:

###### What WTR is?
** WTR ** is a simple web application which helps to record employees activity during working time. 
** WTR ** key functionalities:
 - register user
 - change password
 - show content only for logged in users
 - application is divided into two parts: 
   - user:
     - record working time start and stop by clicking dedicated buttons
     - record break time (if taken) and update databases respectively
     - user is given 15 minutes* break 
     - break is taken by clicking proper option on the screen
     - view records history in his profile 
   - admin:
     - is able to see records of all employees
     - is able to filter tables and search for interested information 
     - is able to remove users 
     - WTR should be able to send an email to admin when the working time is shorter than 8 hours*


*for testing purposes working time has been shortened to 5 seconds as well as break time     

######Languages and technologies used during creation of **WTR**: 

 - Visual Studio Code 1.52.1.0 - IDE
 - DB Browser (SQLite) (testing SQL queries)
 - Python 3.8.7
 - SQLite 3
 - HTML
 - CSS
 - Flask framework
 - Bootstrap v.5.0

###### Files included: 
 - main:
   - app.py - core of the application. The file contains
     all needed paths, redirections, SQL commands and logic 
   - helpers.py - all created on demand functions used in app.py:
	- login_required 
	- makeActiveUsers() - prepare list of users
	- send_email()  - send email with alert for admin in certain conditions
	- access() - hides admin email password so it is not visible in app.py

   - requirements.txt 
 - static:
   - styles.css - styling
 - templates:
   - layout.html - layout of the website, created with **Bootstrap v.5.0**
     -all files below are extensions of 'layout.html':
   	- change.html - password change option
   	- error.html - error events controller - prevents from failures
   	- index.html - core of the application - most of the visible content is here
   	- login.html
   	- register.html 
   	- remove.html - removing users

###### Tasks organization:

 [x] Create logic in **application.py**:
	- [x] predefine routes:
	  - [x] /index - default screen for user (options: take a break*, view records history, start and stop working time)
	    - [x] psuedocode

	  - [x] /index -  default screen for admin (options: view records history, filter history, clear database, remove users)
	    - [x] psuedocode

	  - [x] /changepassword - for logged in
	    - [x] psuedocode 

	  - [x] /removeusers - only for admin
	    - [x] psuedocode

	  - [x] /register 
	    - [x] psuedocode

	  - [x] /login - if user does not exist display info that doesnt exist or removed by admin
	    - [x] psuedocode

 [x] Implement complete layout in layout.html:
		
	- [x] implement #bootstrap external free design for:
	  - [x] navbar
	  - [x] table
	  - [x] button
	  - [x] alerts

	- [x] fill styles.css
	  - [x] test

[x] Design helpers.py 
	- [x] write functions as needed by the program
	  - [x] write login_required function and import it in application.py (https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/)
	  - [x] create function createActiveUsers() - prepares list of current active users
	  - [x] create function sendemail() - sends email to admin in given conditions
	  - [x] create function access() - hides password of email client

[x] Design databases:
	- [x] design database for users profiles
	- [x] design database for users entrances (record of working time)
	  - [x] pseudocode

[x] Complete *.html files using Jinja:
	- [x] layout.html
	  - [x] complete logic - display content according to session (not logged, logged user, logged admin)
	- [x] login.html
	- [x] index.html
	  - [x] record user activity
	  - [x] support overnight (change date) shifts
	  - [x] display needed information
	- [x] changepassword.html
	- [x] removeusers.html
	- [x] register.html

*while taking a break display info that break length will be subtracted from total working time of the shift 

[x] Write code and test all modules:
 - [x] login
 - [x] register
 - [x] changepassword
 - [x] removeusers
 - [x] see history (user)
 - [x] see and manage history tables (admin)
 - [x] record user activity
 - [x] breaks
 - [x] send alert email
 - [x] logout


###### Sources: 
 - function login() - Source: CS50 PSET9: Finance, Author: CS50 authors (https://cs50.harvard.edu/x/2021/psets/9/finance/)
 - Session - Source: CS50 PSET9: Finance, Author: CS50 authors (https://cs50.harvard.edu/x/2021/psets/9/finance/)
 - function login_required () - Source: CS50 PSET9: Finance, Author: CS50 authors (https://cs50.harvard.edu/x/2021/psets/9/finance/)
 - sending emails - Source: adapted from: CS50 Week 9 - Flask, Author: CS50 authors (https://cs50.harvard.edu/x/2021/weeks/9/)
