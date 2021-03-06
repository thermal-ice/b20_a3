# required imports
# the sqlite3 library allows us to communicate with the sqlite database
import sqlite3
# we are adding the import 'g' which will be used for the database
from flask import Flask, render_template, request, g,session, redirect, url_for, escape

# the database file we are going to communicate with
DATABASE = './a3_database.db'

# connects to the database
def get_db():
    # if there is a database, use it
    db = getattr(g, '_database', None)
    if db is None:
        # otherwise, create a database to use
        db = g._database = sqlite3.connect(DATABASE)
    return db

# converts the tuples from get_db() into dictionaries
# (don't worry if you don't understand this code)
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# given a query, executes and returns the result
# (don't worry if you don't understand this code)
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# tells Flask that "this" is the current running app
app = Flask(__name__)
app.secret_key=b'jeffrey'

# this function gets called when the Flask app shuts down
# tears down the database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # close the database if we are connected to it
        db.close()

@app.route('/')
def index():
	if 'username' in session:
		return 'Logged in as %s <a href="/logout">Logout</a>' % escape(session['username'])
	return 'You are not logged in'

@app.route('/login',methods=['GET','POST'])
def login():
	if request.method=='POST':
		sql = """
			SELECT username, password FROM Student
			UNION
			SELECT password, password FROM Instructor
			"""
		results = query_db(sql, args=(), one=False)
		for result in results:
			if result[0]==request.form['username']:
				if result[1]==request.form['password']:
					session['username']=request.form['username']
					return redirect(url_for('index'))
		return "Incorrect UserName/Password"
	elif 'username' in session:
		return redirect(url_for('index'))
	else:
		return render_template('loginPage.html')
@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/inMarks')
def inMarks():
	var1=['1','user','password','first','last', '001', '90', '100', '99', '80', 
	'2','user2','password','first','last', '001', '90', '100', '99', '80',
	'3','user3','password','first','last', '001', '90', '100', '99', '80',
	'4','user4','password','first','last', '001', '90', '100', '99', '80',
	'5','user5','password','first','last', '001', '90', '100', '99', '80']
	counter=0
	return render_template("instructorMarks.html", myVar = var1, count = counter)

if __name__=="__main__":
	app.run(debug=True,host='0.0.0.0')