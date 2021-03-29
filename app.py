import sqlite3
import os

from flask import Flask, render_template, request, g

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



if __name__ == "__main__":
    app.run(debug=True)
