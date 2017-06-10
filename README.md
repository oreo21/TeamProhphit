# Course Selection
### Team Team Platek Prophit
Mr. Brown // Software Development Period 8 // Spring 2017
* Reo Kimura 
* Vanna Mavromatis
* Haley Zeng
* Amy Xu

### About
As requested by the Programming Office, the Course Selection site allows for students to select AP courses. Administrators have control over pre-requisites for each AP class, including overall average, departmental averages, grade level, and classes previously taken. A students' options are filtered to only include APs that they qualify for. Administrators have the ability to close and open the course selection site, so they can decide what window the students have to make their choices. Once the course selection period is over, the students' selections can be exported to a CSV so the Programming Office can go through the list and approve students.

This site is an improvement on the Programming Office's current method of AP course selection (Google Forms) as it prevents students from signing up for classes they cannot take. 

### Dependencies:
* Flask
* oauth2client
* httplib2

To download these dependencies, 
```$ pip install <dependency>```

### Running locally:
* Clone the repo
* On the top level of the repo, run the database initializer
```$ python utils/db_builder.py```
* Run the Flask app
```$ python app.py```
* In a web broswer, go to localhost:5000

### ADMINS: Setting up the site 
1. Upload the Courses file which is the master list of all courses. See courses.csv for the expected format.
2. Upload the Student Transcripts file, which contains all the students and their class grades. See student_transcripts.csv for the expected format.
3. If a warning regarding uncategorized courses appears, click on the warning to fix these issues.
4. Turn on the site to allow students to select courses.

NOTE: The clients secret file should be placed in the root of the directory.
### Admin functionality:
* Modify course information, including pre-requisite courses/grades
* Modify student information
* Overriding pre-reqs to allow a student to sign up for a course
* Open/close the student site
* Export student choices

### Student functionality:
* Select AP courses
