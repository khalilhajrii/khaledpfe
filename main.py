import functools
import re
import time
import warnings
from flask import Flask, render_template, request, session, redirect, url_for, Markup
import secrets
import string
#libraries for database
import mysql.connector
import MySQLdb
import MySQLdb.cursors
from flask_mysqldb import MySQL
from flask_login import LoginManager


# Change this to your secret key (can be anything, it's for extra protection)
app = Flask(__name__)
app.secret_key = 'your secret key'
warnings.filterwarnings("ignore")

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'add'
app.config['MYSQL_PORT'] = 3306

# Intialize MySQL
login = LoginManager()
login.init_app(app)
mysql = MySQL(app)

# Login endpoint security
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

# Securing login page endpoint
@login.user_loader
@app.route('/')
def index():
    if "username" in session:
        return redirect(url_for("test"))
    return render_template("login.html")

#Login 
@ app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM user WHERE username = %s AND password = %s', (username, password,))
        # return one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['name'] = account['name']
            session['last_name'] = account['last_name']
            session['email'] = account['email']
            session['gender'] = account['gender']
            session['address'] = account['address']
            session['phone'] = account['phone']
            session['status'] = account['status']
            # Redirect to home page
            return redirect(url_for('profile'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = Markup(
                """<div class="alert alert-danger" role="alert"> User's password/username is wrong !</div> """)
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

# Listing users
@app.route('/users', methods=['GET', 'POST'])
@ login_required
def users():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * from user")
    mysql.connection.commit()
    user = cursor.fetchall()
    return render_template('userslist.html', user=user)

#generating random password
def passwords():
    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation
    alphabet = letters + digits + special_chars
    pwd_length = 12
    pwd = ''
    for i in range(pwd_length):
        pwd += ''.join(secrets.choice(alphabet))
    return pwd

# Add user
@ app.route('/adduser', methods=['GET', 'POST'])
@ login_required
def adduser():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        last_name = request.form['last_name']
        email = request.form['email']
        gender = int(request.form['gender'])
        address= request.form['address']
        phone=request.form['phone']
        status = int(request.form['status'])
        password=passwords()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM user WHERE username = %s or email = %s or phone=%s', (username, email, phone))
        user = cursor.fetchone()
        if user:
            msg = Markup(
                """<div class="alert alert-danger" role="alert"> User already exist</div> """)
        else:
            cursor.execute(
                'INSERT INTO user (username, name, last_name, email, password, gender, address, phone, status) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s)', (username, name, last_name, email, password, gender, address, phone,status))
            mysql.connection.commit()
            return redirect(url_for('users'))
    return render_template("add_user.html", msg=msg)


# Update user
@ app.route('/update/<int:id>', methods=['GET', 'POST'])
@ login_required
def updateuser(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user where id =% s", (id,))
    user = cursor.fetchone()
    return render_template('updateuser.html', user=user)


# Confirm update user
@ app.route('/update', methods=['GET', 'POST'])
def confirmupdate():
    msg = ""
    if request.method == 'POST':
        id=request.form["id"]
        username = request.form['username']
        name = request.form['name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']
        address=request.form['address']
        phone = request.form['phone']
        status = request.form['status']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE user SET username = %s, name = %s, last_name = %s, email = %s, password = %s, gender = %s, address= %s, phone = %s, status = %s WHERE id = %s',
               (username, name, last_name, email, password, gender, address, phone, status, (id,),))
        mysql.connection.commit()
        msg = Markup(
                """<div class="alert alert-success" role="alert">User updated successfully</div>""")
    return redirect(url_for('users'))

@app.route('/delete/<id>')
@ login_required
def delete_user(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM user WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('users'))

#return profile page
@ app.route('/profile',methods=['GET', 'POST'])
@login_required
def profile():
    id=session['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user where id =% s", (id,))
    user_data = cursor.fetchone()
    return render_template("profile.html",user_data=user_data)

# Update profile
@ app.route('/updateprofile/<int:id>', methods=['GET', 'POST'])
@ login_required
def updateprofile(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user where id =% s", (id,))
    user = cursor.fetchone()
    return render_template('updateProfile.html', user=user)


# Confirm update profile
@ app.route('/updateprofile', methods=['GET', 'POST'])
def confirmupdateprofile():
    if request.method == 'POST':
        status=0
        id=session['id']
        username = request.form['username']
        name = request.form['name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']
        address=request.form['address']
        phone = request.form['phone']
        if session['status']==1:
            status = request.form['status']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE user SET username = %s, name = %s, last_name = %s, email = %s, password = %s, gender = %s, address= %s, phone = %s, status = %s WHERE id = %s',
               (username, name, last_name, email, password, gender, address, phone, status, (id,),))
        mysql.connection.commit()
        if session['loggedin']:
            session['loggedin'] = True
            session['username'] = username
            session['name'] = name
            session['last_name'] = last_name
            session['email'] = email
            session['gender'] = gender
            session['address'] = address
            session['phone'] = phone
            session['status'] = status
    return redirect(url_for('profile'))

#Delete profile
@app.route('/deleteprofile/<id>')
@ login_required
def delete_profile(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM user WHERE id=%s", (id,))
    mysql.connection.commit()
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Update user
@ app.route('/useraction', methods=['GET', 'POST'])
@ login_required
def user_action():
    return render_template('abb.html')

#return Action list page
@ app.route('/action',methods=['GET', 'POST'])
@login_required
def action_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM action")
    action_list = cursor.fetchone()
    return render_template("action_list.html",action_list=action_list)



# Logout
@ app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()