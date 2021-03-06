import sqlite3
import os

from flask import Flask, render_template, request, g, redirect, url_for, session

app = Flask(__name__)

# Setting the path to the database file
DATABASE = os.path.join('.', 'assignment3.db')


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

def userHasNotLoggedIn():
    return 'username' not in session



@app.route('/login')
@app.route('/login/<loginresult>')
def loginpage(loginresult='good'):
    # sessions = {'username': 'student1'}

    if not userHasNotLoggedIn():
        return redirect(url_for('index'))

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
        return render_template('index.html', userType=session['userType'])
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
    
    return render_template("seeFeedback.html", mydict = dict1, userType=session['userType'])

@app.route('/remarks')
def getAllRemarks():

    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    if session['userType'] != 'instructor':
        return render_template('error.html', errorMsg="You must be an instructor to see this page")

    remarks= query_db('SELECT * FROM Remarks')
    return render_template("remarks.html", myremarks = remarks)


coursework = ['A1', 'A2', 'A3',
              'Lab1', 'Lab2', 'Lab3',
              'Midterm exam',
              'Final exam'
              ]

courseworkToColumnName = {'A1':'A1_mark', 'A2':'A2_mark', 'A3':'A3_mark',
              'Lab1':'Lab1_mark', 'Lab2':'Lab2_mark', 'Lab3':'Lab3_mark',
              'Midterm exam':'midtermMark',
              'Final exam':'finalExam'}


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

def get_instructor_list():
    instuctor_list = query_db("select username from Instructor")
    result = []
    for instuctor_dict in instuctor_list:
        result.append(instuctor_dict["username"])

    return result

@app.route('/submitFeedback', methods=['GET'])
def feedback():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    if session['userType'] != 'student':
        return render_template('error.html', errorMsg="You must be a Student to see this page")

    instructorlist = get_instructor_list()
    return render_template('feedback.html', instructorlist=instructorlist, userType= session['userType'])


@app.route('/feedback_result', methods=['POST'])
def feedback_result():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    instructorToSend = request.form.get('theinstructor')
    instructor_row = query_db('select * from instructor where username=?', [instructorToSend], one=True)
    instructor_id = instructor_row['instructor_id']
    feedbackText = request.form.get('feedback_text')
   
    insertIntoDatabase('INSERT INTO Feedback(instructor_id, feedback_text) VALUES (?, ?)', (instructor_id, feedbackText))

    return render_template('success.html',successMsg=f"Your feedback has been submitted successfully! \nTo instructor: {instructorToSend}, " \
           f"with the following feedback: {feedbackText}", userType= session['userType'])

# The score for the individual student
@app.route('/scores', methods=['GET'])
def scores():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    if session['userType'] != 'student':
        return render_template('error.html', errorMsg="You must be a student to see this page")


    marks = getSingleRowFromDatabase("SELECT A1_mark, A2_mark, A3_mark, Lab1_mark, Lab2_mark, Lab3_mark, midtermMark,finalExam "
                                     "FROM Student WHERE student_id=?",(session['userid'],))


    return render_template('studentMarks.html',studentMarkDict= marks, userType = session['userType'])

    

@app.route('/editmarks', methods=['GET'])
@app.route('/editmarks/<result>', methods=['GET'])
def editMarks(result = 'good'):
    if result == 'bad':
        return render_template('editMarks.html', courseworklist=coursework, validStudentId=False)

    return render_template('editMarks.html', courseworklist = coursework, validStudentId= True)

@app.route('/editMarkResults', methods=['POST'])
def editMarkResults():
    potentialStudentId = int(request.form.get('studentid'))
    newPotentialMark = int(request.form.get('newMark'))

    studentIdExist = getSingleRowFromDatabase("SELECT 1 Student_id FROM Student where student_id=?;",(potentialStudentId,))

    if studentIdExist is not None:

        colToInsertInto = courseworkToColumnName[request.form.get('thecoursework')] #Probably should sanitize this input

        insertIntoDatabase(f"UPDATE Student SET {colToInsertInto}=? WHERE student_id=? ;",(newPotentialMark,potentialStudentId))

        return render_template('success.html',successMsg=f"You have successfully edited {potentialStudentId}'s Mark")


    return redirect(url_for('editMarks', result='bad'))


@app.route('/registerStudent',methods=['GET'])
@app.route('/registerStudent/<result>',methods=['GET'])
def registerStudent(result = 'good'):
    if result == 'bad':
        return render_template('registerStudent.html',userNameTaken=True)
    return render_template('registerStudent.html',userNameTaken = False)


@app.route('/registerStudentResult',methods=['POST'])
def registerStudentResult():

    potentialUsername = request.form.get('username')

    userNameAlreadyExists = getSingleRowFromDatabase("SELECT 1 username FROM Student where username=?;",(potentialUsername,))

    if userNameAlreadyExists is None:
        potentialPassword = request.form.get('password')
        potentialfirstName = request.form.get('firstname')
        potentialLastname = request.form.get('lastName')
        potentialLectureSection = int(request.form.get('lecSection'))

        insertIntoDatabase("INSERT INTO Student(username,password,firstName,lastName,lectureSection) VALUES (?,?,?,?,?);",
                           (potentialUsername,potentialPassword,potentialfirstName,potentialLastname,potentialLectureSection))

        return render_template('success.html',successMsg=f"You have successfully registered with {potentialUsername} as your username")

    return redirect(url_for('registerStudent',result='bad'))


@app.route('/registerInstructor', methods=['GET'])
@app.route('/registerInstructor/<result>',methods=['GET'])
def registerInstructor(result='good'):
    if result == 'bad':
        return render_template('registerInstructor.html', userNameTaken=True)
    return render_template('registerInstructor.html', userNameTaken=False)


@app.route('/registerInstructorResult',methods=['POST'])
def registerInstructorResult():
    potentialUsername = request.form.get('username')

    userNameAlreadyExists = getSingleRowFromDatabase(
        "SELECT 1 username FROM Instructor where username=?;",
        (potentialUsername,))

    if userNameAlreadyExists is None:
        potentialPassword = request.form.get('password')
        potentialLectureSection = int(request.form.get('lecSection'))

        insertIntoDatabase(
            "INSERT INTO Instructor(username,password,lecture_section) VALUES (?,?,?);",
            (potentialUsername, potentialPassword, potentialLectureSection))

        return render_template('success.html',successMsg=f"You have successfully registered with {potentialUsername} as your username")

    return redirect(url_for('registerInstructor', result='bad'))


# Stuff from the previous assignment:

# TODO: Integrate these pages with the new pages


@app.route('/index')
def index():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))
    return render_template('index.html',userType = session['userType'])


@app.route("/about")
def about():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    return render_template("about.html", userType=session['userType'])

# @app.route("/feedback")
# def feedback():
#     return render_template("feedback.html")

@app.route("/thankyou")
def thankyou():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    return render_template("thankyou.html", userType = session['userType'])

@app.route("/Assignments")
def Assignments():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    return render_template("Assignments.html",userType = session['userType'])

@app.route("/CourseTeam")
def CourseTeam():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    return render_template("CourseTeam.html",userType = session['userType'])

@app.route("/labs")
def labs():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    return render_template("labs.html",userType = session['userType'])

@app.route("/lecture")
def lecture():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    return render_template("lecture.html",userType = session['userType'])

@app.route("/tutorials")
def tutorials():
    if userHasNotLoggedIn():
        return redirect(url_for('loginpage',loginresult='notLoggedIn'))

    return render_template("tutorials.html",userType = session['userType'])


if __name__ == "__main__":
    app.run(debug=True)
