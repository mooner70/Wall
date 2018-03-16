from flask import Flask, request, redirect, render_template, session, flash
import re
import md5
from mysqlconnection import MySQLConnector
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector(app,'wall')

@app.route('/')
def login():
    if 'user' in session:
        return redirect('/wall')
        print session['user']

    else:
        return render_template('index.html')


@app.route('/login', methods=['POST'])

def valLogin():
    error = 0
    form_data = {'email' : str(request.form['logemail']), 'pw' : str(request.form['logpw']) }
    ## Data Validation
    for key, value in form_data.items():
        if "" == value:
            flash('There are blank fields')
            error += 1
            break
    if len(form_data['pw']) < 8:
        flash('Password must be at least 8 characters long')
        error += 1
    if not EMAIL_REGEX.match(form_data['email']):
        flash('Email is not a valid email address')
        error += 1
   
    ### End Data Validation  
    if error > 0:
        return redirect('/')   
    else:
        query = "select * from users where email ='" + str(request.form['logemail']) +"' LIMIT 1"
        check = mysql.query_db(query)
        password = md5.new(request.form['logpw']).hexdigest()
        if len(check) < 1:
            flash('User not found')
        else:
            if check[0]['password'] == password:
                session['user'] = check[0]
                return redirect ('/wall')
            else:
                flash('Password incorrect')
        
        return redirect('/')


@app.route('/registration', methods=['POST'])

def valReg():
    error = 0
    form_data = {'email' : str(request.form['regemail']), 'first' : str(request.form['first_name']), 'last' : str(request.form['last_name']), 'pw' : str(request.form['pw']), 'pwconfirm' : str(request.form['pwconfirm'])}
    error = 0
    ## Data Validation
    for key, value in form_data.items():
        if "" == value:
            flash('There are blank fields')
            error += 1
            break
    if str.isalpha(form_data['first']) == False:
        flash('Can not have numbers in first name')
        error += 1
    if str.isalpha(form_data['last']) == False:
        flash('Can not have numbers in last name')
        error += 1
    if len(form_data['pw']) < 8:
        flash('Password must be at least 8 characters long')
        error += 1
    if not EMAIL_REGEX.match(form_data['email']):
        flash('Email is not a valid email address')
        error += 1
    if form_data['pw'] != form_data['pwconfirm']:
        flash('Password confirmation does not match password')
        error += 1
    ### End Data Validation     
    if error > 0:
        return redirect('/')
    else:
        password = md5.new(request.form['pw']).hexdigest()
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name,:last_name,:email,:password, NOW(), NOW())"
        data = {
             'first_name': request.form['first_name'],
             'last_name': request.form['last_name'],
             'email': request.form['regemail'],
             'password': password,
           }
        mysql.query_db(query, data)
        return redirect('/')

@app.route('/wall')

def wall():
    query = "select *,  date_format(messages.created_at, '%b %d %Y') AS date FROM users left JOIN messages ON users.id = messages.user_id left join comments on messages.id = comments.message_id ORDER BY messages.created_at DESC"
    container = mysql.query_db(query)
    return render_template('wall.html', container=container)

@app.route('/wall', methods=["POST"])
def post():
    id = session["user"]["id"]
    query = "INSERT INTO messages (message, created_at, updated_at, user_id) VALUES (:message, NOW(), NOW(), :id)"
    data = {
        "message": request.form["message"],
        "id": id
    }
    mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/comment', methods=["POST"])

def comment():
    id = session["user"]["id"]
    mID = request.form['hidden']
    query = "INSERT INTO comments (comment, created_at, updated_at, user_id, message_id) VALUES (:comment, NOW(), NOW(), :id, :mID)"
    data = {
        "comment": request.form["comment"],
        "id": id,
        "mID": mID
    }
    mysql.query_db(query, data)
    return redirect('/wall')










app.run(debug=True)