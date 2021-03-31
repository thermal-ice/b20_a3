import sqlite3
import os

from flask import Flask, render_template, request, g, redirect, url_for, session

app = Flask(__name__)

# Setting the path to the database file
DATABASE = os.path.join('.', 'database', 'a3_database.db')

def scoreStringParser(scoreString: str):
    return scoreString.split('/')

# Passing in the parser function for assignment/lab marks
app.jinja_env.globals.update(scoreStringParser = scoreStringParser)





def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    db.row_factory = make_dicts
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()




app.secret_key = b'jenny'


# @app.route('/index')
# @app.route('/login', methods=['GET','POST'])
# def login():
#
#     if request.method == 'POST':
#         session.['username'] = request.form.get('username')
#         return redirect(url_for('index'))
#
#     elif request.method == 'POST':
#
#
#
#             return f"username is: {username}, you have logged in with password {session[username]}"
#

@app.route('/login')
@app.route('/login/<loginresult>')
def loginpage(loginresult = 'good'):

    #sessions = {'username': 'student1'}

    if 'username' in session:
        return f"Hi {session['username']}, you have logged on"

    if loginresult == 'bad':
        return render_template('login.html',firstLoginAttempt = False)

    return render_template('login.html',firstLoginAttempt = True)


@app.route('/logout')
def logout():
    if 'username' in session:
        usernameVal = session['username']
        session.pop('username',None)
        session.pop('userid',None)
        return f"hey {usernameVal}, you have successfully logged off"
    else:
        return "You are not logged in"




@app.route('/loginresult', methods=['POST'])
def loginresult():
    potentialusername = request.form.get('username')
    potentialpassword = request.form.get('password')

    #First get the user submitted username and password

    db = get_db()
    cur1 = db.execute('SELECT * FROM Student WHERE username=? AND password=?',
               (potentialusername, potentialpassword))

    cur2 = db.execute('SELECT * FROM Instructor WHERE username=? AND password=?',
               (potentialusername, potentialpassword))

    cur1res = cur1.fetchone()
    cur2res = cur2.fetchone()
    success = cur1res or cur2res
    db.close()

    #Check if the username and password are correct

    if success:
        session['username'] = potentialusername

        if cur1res:
            session['userid'] = cur1res['student_id']
        else:
            session['userid'] = cur1res['instructor_id']
        return f"Hi {potentialusername}, you have logged on, with userid {session['userid']}"
    else:
        return redirect(url_for('loginpage',loginresult='bad'))


@app.route('/example')
def example():
    myvar = ['hello', 'guys','bye']
    return render_template('example.html', var1 = myvar)


@app.route('/')
def root():
    result = query_db("select * from Instructor")
    return result.__str__()


@app.route('/studentmarks')
def getStudentMarks():
    return query_db('SELECT * FROM Student').__str__()


@app.route('/feedback')
def getAllFeedback():
    return query_db('SELECT * FROM Feedback').__str__()

@app.route('/remarks')
def getAllRemarks():
    return query_db('SELECT * FROM Remarks').__str__()




coursework = ['Assignment1','Assignment2','Assignment3',
              'Lab1','Lab2','Lab3',
              'Midterm exam',
              'Final exam'
              ]

AssignmentOrLabs = ['Assignment1','Assignment2','Assignment3',
              'Lab1','Lab2','Lab3',]

@app.route('/remarkrequest', methods=['GET'])
def remarkrequest():
    return render_template('remarkRequest.html', courseworklist= coursework)

@app.route('/remarkresult', methods=['POST'])
def remarkresult():
    courseworkToRemark = request.form.get('thecoursework')
    explanationForRemark = request.form.get('remarkexplanation')



    query_db("INSERT INTO Remarks VALUES (?,?,?)",(session['userid'],courseworkToRemark,explanationForRemark))

    return f"The work to remark is: {courseworkToRemark}, the explantion is {explanationForRemark}"


if __name__ == "__main__":
    app.run(debug=True)
