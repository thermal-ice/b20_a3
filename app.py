import sqlite3
import os

from flask import Flask, render_template, request, g, redirect, url_for, session

app = Flask(__name__)

# Setting the path to the database file
DATABASE = os.path.join('.', 'assignment3.db')



def scoreStringParser(scoreString: str):
    return scoreString.split('/')

def joinScoreList(scoreList: list):
    return '/'.join(scoreList)


# Passing in the parser function for assignment/lab marks
app.jinja_env.globals.update(scoreStringParser=scoreStringParser)



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


def insertIntoDatabase(sqlQuery: str, values: tuple):
    db = get_db()
    cur = db.cursor()
    cur.execute(sqlQuery, values)
    db.commit()
    cur.close()

def getSingleRowFromDatabase(sqlQuery: str, values: tuple):
    db =get_db()
    cur = db.cursor()
    result = cur.execute(sqlQuery,values).fetchone()
    db.commit()
    cur.close()
    return result

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

def userHasNotLoggedIn():
    return 'username' not in session



@app.route('/login')
@app.route('/login/<loginresult>')
def loginpage(loginresult='good'):
    # sessions = {'username': 'student1'}

    if not userHasNotLoggedIn():
        return f"Hi {session['username']}, you have logged on"

    if loginresult == 'bad':
        return render_template('loginPage.html', loginStatus=1)
    if loginresult == 'notLoggedIn':
        return render_template('loginPage.html',loginStatus=2)
    if loginresult == 'loggedOut':
        return render_template('loginPage.html', loginStatus=3)

    return render_template('loginPage.html', loginStatus=0)


@app.route('/logout')
def logout():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))


    session.pop('username', None)
    session.pop('userid', None)
    session.pop('userType', None)
    return redirect(url_for('loginpage',loginresult='loggedOut'))



@app.route('/loginresult', methods=['POST'])
def loginresult():
    potentialusername = request.form.get('username')
    potentialpassword = request.form.get('password')

    # First get the user submitted username and password

    cur1res = getSingleRowFromDatabase('SELECT * FROM Student WHERE username=? AND password=?',
                       (potentialusername, potentialpassword))

    cur2res = getSingleRowFromDatabase('SELECT * FROM Instructor WHERE username=? AND password=?',
        (potentialusername, potentialpassword))

    success = cur1res or cur2res

    # Check if the username and password are correct

    if success:
        session['username'] = potentialusername
        if cur1res:
            session['userid'] = cur1res['student_id']
            session['userType'] = 'student'
        else:
            session['userid'] = cur2res['instructor_id']
            session['userType'] = 'instructor'
        return render_template('index.html')
    else:
        return redirect(url_for('loginpage', loginresult='bad'))


@app.route('/example')
def example():
    myvar = ['hello', 'guys', 'bye']
    return render_template('example.html', var1=myvar)


@app.route('/')
def root():
    return redirect(url_for('loginpage'))


@app.route('/studentmarks')
def getStudentMarks():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))


    if session['userType'] != 'instructor':
        return render_template('error.html', errorMsg="You must be an instructor to see this page")


    mark1 = query_db('SELECT student_id,firstName,lastName,A1_mark,A2_mark,A3_mark,Lab1_mark,Lab2_mark,Lab3_mark, midtermMark, finalExam FROM Student')
    return render_template('instructorMarks.html', marks = mark1, numCols = 5)


@app.route('/feedback')
def getAllFeedback():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    if session['userType'] != 'instructor':
        return render_template('error.html', errorMsg="You must be an instructor to see this page")

    dict1 = query_db('SELECT feedback_text FROM Feedback WHERE instructor_id=?',(session['userid'],))
    # return render_template('seeFeedback.html', mydict=dict1)
    return dict1.__str__()

@app.route('/remarks')
def getAllRemarks():

    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    if session['userType'] != 'instructor':
        return render_template('error.html', errorMsg="You must be an instructor to see this page")


    return query_db('SELECT * FROM Remarks').__str__()


coursework = ['A1', 'A2', 'A3',
              'Lab1', 'Lab2', 'Lab3',
              'Midterm exam',
              'Final exam'
              ]

AssignmentOrLabs = ['A1', 'A2', 'A3',
                    'Lab1', 'Lab2', 'Lab3', ]

instructorlist = ['LyndaBarnes', 'SteveEngels', 'PaulGries', 'DanHeap', 'KarenReid']

@app.route('/remarkrequest', methods=['GET'])
def remarkrequest():

    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    return render_template('remarkRequest.html', courseworklist=coursework)


@app.route('/remarkresult', methods=['POST'])
def remarkresult():

    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    courseworkToRemark = request.form.get('thecoursework')
    explanationForRemark = request.form.get('remarkexplanation')

    insertIntoDatabase('INSERT INTO Remarks VALUES (?,?,?)', (
    session['userid'], courseworkToRemark, explanationForRemark))

    return f"The work to remark is: {courseworkToRemark}, the explantion is {explanationForRemark}"

@app.route('/submitFeedback', methods=['GET'])
def feedback():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    if session['userType'] != 'student':
        return "You must be an student to see this page"
    return render_template('feedback.html', instructorlist=instructorlist) #Why the hardcode?


@app.route('/feedback_result', methods=['POST'])
def feedback_result():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    instructorToSend = request.form.get('theinstructor')
    instructor_row = query_db('select * from instructor where username=?', [instructorToSend], one=True)
    instructor_id = instructor_row['instructor_id']
    feedbackText = request.form.get('feedback_text')
    # print(feedbackText)
    insertIntoDatabase('INSERT INTO Feedback(instructor_id, feedback_text) VALUES (?, ?)', (instructor_id, feedbackText))

    return f"Your feedback has been submitted successfully! \nTo instructor: {instructorToSend}, " \
           f"with the following feedback: {feedbackText}"

# The score for the individual student
@app.route('/scores', methods=['GET'])
def scores():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    if session['userType'] != 'student':
        return "You must be a student to see this page"

    marks = getSingleRowFromDatabase("SELECT A1_mark, A2_mark, A3_mark, Lab1_mark, Lab2_mark, Lab3_mark, midtermMark,finalExam "
                                     "FROM Student WHERE student_id=?",(session['userid'],))


    return render_template('studentMarks.html',studentMarkDict= marks)

    # return marks.__str__()


# Stuff from the previous assignment:

# TODO: Integrate these pages with the new pages


@app.route('/index')
def index():
    return render_template('index.html')


@app.route("/about")
def about():
    return render_template("about.html")

# @app.route("/feedback")
# def feedback():
#     return render_template("feedback.html")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/Assignments")
def Assignments():
    return render_template("Assignments.html")

@app.route("/CourseTeam")
def CourseTeam():
    return render_template("CourseTeam.html")

@app.route("/labs")
def labs():
    return render_template("labs.html")

@app.route("/lecture")
def lecture():
    return render_template("lecture.html")

@app.route("/tutorials")
def tutorials():
    return render_template("tutorials.html")


if __name__ == "__main__":
    app.run(debug=True)
