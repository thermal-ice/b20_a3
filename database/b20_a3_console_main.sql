CREATE TABLE Feedback(
    feedback_id INTEGER PRIMARY KEY,
    instructor_id INTEGER NOT NULL,
    feedback_text TEXT NOT NULL,
    FOREIGN KEY (instructor_id) references Instructor(instructor_id)
);

CREATE TABLE Instructor(
    instructor_id INTEGER PRIMARY KEY NOT NULL UNIQUE ,
    username TEXT NOT NULL ,
    password TEXT NOT NULL,
    lecture_section INTEGER NOT NULL

);

CREATE TABLE Student(
    student_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL ,
    password TEXT NOT NULL ,
    firstName TEXT NOT NULL ,
    lastName TEXT NOT NULL ,
    lectureSection INTEGER,
    A1_mark INTEGER,
    A2_mark INTEGER,
    A3_mark INTEGER,
    Lab1_mark INTEGER,
    Lab2_mark INTEGER,
    Lab3_mark INTEGER,
    midtermMark INTEGER ,
    finalExam INTEGER
);

CREATE TABLE Remarks(
    student_id INTEGER,
    assignmentType TEXT NOT NULL ,
    remarkMessage TEXT NOT NULL ,
    FOREIGN KEY (student_id) references Student(student_id)
);

INSERT INTO Feedback(instructor_id, feedback_text) VALUES (10000,'We need more class engagement');
INSERT INTO Feedback(instructor_id, feedback_text) VALUES (10001, 'We need more interesting TA');
INSERT INTO Feedback(instructor_id, feedback_text) VALUES (20000,'Instructor could set up breakout rooms');
INSERT INTO Feedback(instructor_id, feedback_text) VALUES (20001,'The assignment is too long');
INSERT INTO Feedback(instructor_id, feedback_text) VALUES (20000,'Time is not sufficient for our midterm');


INSERT INTO Instructor VALUES (10000, 'LyndaBarnes', 'GraduateOffice', 1);
INSERT INTO Instructor VALUES (10001, 'SteveEngels', 'sengels', 1);
INSERT INTO Instructor VALUES (10002, 'PaulGries', 'pgries', 2);
INSERT INTO Instructor VALUES (10003, 'DanHeap', 'heapify', 2);
INSERT INTO Instructor VALUES (10004, 'KarenReid', 'reid', 3);

INSERT INTO Student VALUES (00128, 'Zhang', 'Zhang00', 'Larry', 'Zhang',2, '86', '78', '59', '68', '80', '72', 86, 95);
INSERT INTO Student VALUES (00345, 'Shankar', 'Shankar00', 'Tom', 'Shankar',2, '75', '58', '93','84', '93', '89', 85, 75);
INSERT INTO Student VALUES (00991,'Brandt', 'Brandt00', 'Dan', 'Brandt', 1, '68', '80', '72', '90', '85', '93', 78, 85);
INSERT INTO Student VALUES (00121, 'Chavez', 'Chavez00', 'Tarek', 'Chavez',1, '90', '85', '93','89', '94', '78', 85, 96);
INSERT INTO Student VALUES (00553, 'Peltier', 'Peltier00', 'Ashton', 'Peltier',2, '92', '69', '78','96', '88', '87', 85, 79);
INSERT INTO Student VALUES (00678, 'Levy', 'Levy00', 'Ravin', 'Levy',3, '84', '93', '89','84', '80', '72', 87, 90);
INSERT INTO Student VALUES (00321, 'Williams', 'Williams00', 'Allan','Williams', 1, '98', '91', '88','68', '80', '72',79,93);
INSERT INTO Student VALUES (00739, 'Sanchez', 'Sanchez00', 'Michael', 'Sanchez',3, '87', '79', '95', '78', '87', '76',83,78);
INSERT INTO Student VALUES (00557, 'Snow', 'Snow00', 'White', 'Snow', 3, '83', '92', '86', '84', '93', '89', 89, 93);
INSERT INTO Student VALUES (00543, 'Brown', 'Brown00', 'Marsha', 'Brown', 2, '96', '88', '87','68', '80', '72',92, 79);

INSERT INTO Remarks VALUES (00128, 'A2', 'I want more marks');
INSERT INTO Remarks VALUES (00128, 'Midterm', 'I want even more marks');
INSERT INTO Remarks VALUES (00991, 'A2', 'My mark is not enough');
INSERT INTO Remarks VALUES (00128, 'A1', 'The total score is not calculated correctly');
INSERT INTO Remarks VALUES (00128, 'Midterm', 'I want more marks for question 5');

SELECT * from Feedback;

-- Mandatory users to add:

INSERT INTO Student VALUES (0600,'student1','student1','Bob','Jones',3,'96', '88', '87','68', '80', '72',75,80);
INSERT INTO Student VALUES (0601,'student2','student2','Bob','Jones',3,'76', '78', '77','58', '70', '62',65,70);

INSERT INTO Instructor VALUES (20000, 'instructor1', 'instructor1', 1);
INSERT INTO Instructor VALUES (20001, 'instructor2', 'instructor2', 2);







