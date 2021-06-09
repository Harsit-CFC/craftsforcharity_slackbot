# all imports
import copy  # copy to create deep copies of our pages so that the base files never change
import json  # json package used to load, modify, and dump our json
from datetime import date  # imports date formatting automatically

from slack_bolt import App  # imports the app from slack that we use to connect

import sheets  # sheets.py, our file that formats our sheet data

import re  # the retgex stuff

# json credentials
config = json.load(open('config.json'))
# datetime variables

t = date.today()
timestamp = t.strftime("%B %d, %Y")


# class declaration
class Applicant:
    def __init__(self, e, d, a, chosenDate, time, student, numofstudents, hand, course):
        self.e = e
        if self.e:
            self.e = "E"  # 2nd index
        self.d = d
        if self.d:
            self.d = "D"  # 3rd index
        self.a = a
        if self.a:
            self.a = "A"  # 4th index
        self.date = chosenDate  # 6th index
        if chosenDate == "":
            self.date = "None"
        self.time = time  # 7th index
        if time == "":
            self.time = "No Time"
        self.student = student  # 9th index
        self.numofstudents = numofstudents  # 8th index
        self.hand = hand  # 14th index
        self.course = re.sub(r" ?\([^)]+\)", "", course)


# base json formats
MainPage = json.load(open('mainpage.json'))
StudentPage = json.load(open('studentpage.json'))
# spreadsheet variables
students = sheets.sheetinit()
courses = sheets.courseinit()


# construction functions
def coursecreate(courses):  # returns a course list => get courses from list and adds it to a classlist
    courselist = []  # list made to return all courses
    for i in courses:  # standard loop through list
        if i == "":  # if empty then pass
            pass
        else:  # if it has content then add it to courselist
            courselist.append(i)
    courselist.pop(0)
    return courselist


def courseJSON(courselist):  # returns dumped json => insert courses in json format
    main_page_copy = copy.deepcopy(MainPage)
    main_page_copy["blocks"][1]["elements"][0]["text"] = timestamp + "  |  Crafts for Charity"
    for i in courselist:  # standard loop through list
        value = courselist.index(
            i)  # slack needs a list value to add to the json, this just grabs the index and substitutes it instead
        main_page_copy["blocks"][3]["accessory"]["options"].append({
            "text": {
                "type": "plain_text",
                "text": i
            },
            "value": "value-" + str(value)
        }, )  # appends the data we need for the classes as a dictionary or list or something whatever format json uses
    return json.dumps(main_page_copy)


def courseFilters(courselist):  # returns nested list => creates a list for every value in courselist
    courseStorage = [[] for _ in range(len(courselist))]
    for i in courselist:
        courseStorage[courselist.index(i)].append([i])
    return courseStorage


def courseMatch(student, courselist):  # returns student.course as INTEGER => sets student course to the index of the course value
    for c in courselist:
        if student.course == c:
            student.course = courselist.index(c)
    return student.course


def appendStorage(student, courseStorage):  # no return => adds student to the course-specific list index
    courseStorage[student.course].append(student)


def studentCreate(students, courseStorage):  # no return => creates the student object for all students
    courselist = coursecreate(courses)
    courseStorage = courseFilters(courselist)
    for i in students:
        student = Applicant(i[2], i[3], i[4], i[6], i[7], i[9], i[8], i[14], i[11])
        student.course = courseMatch(student, courselist)
        appendStorage(student, courseStorage)
    return courseStorage


def studentBlocks(courseStorage):  # no return => adds student blocks to coursestorage at the right course
    student_page_copy = copy.deepcopy(StudentPage)
    for course in courseStorage:
        for student in course[1:]:
            courseStorage[student.course].append(student)
    return courseStorage


def runStudents(courses, students):  # no return=> runs all student-related functions to put them in the studentcopy json array
    courselist = coursecreate(courses)
    courseStorage = courseFilters(courselist)
    courseStorage = studentCreate(students, courseStorage)
    courseStorage = studentBlocks(courseStorage)
    return courseStorage


# Slack App
app = App(
    token=config["token"],  # bot token from slack oath/permissions page
    signing_secret=config["ss"]  # signing secret from slack info page
)


# Slack API functions
@app.shortcut("menu")  # reacts on call for shortcut with the id of "menu"
def create_modal(ack, shortcut, client):
    ack()  # acknowledge request and return http 200, code lasts for 3 seconds so we need to put something placeholder
    res = client.views_open(  # default view on open
        trigger_id=shortcut["trigger_id"],  # id's needed to respond at the right location
        view={
            "title": {
                "type": "plain_text",
                "text": "CFC Scheduler"
            },
            "type": "modal",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Loading :yarn:"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Please wait for the modal to load!"
                    }
                }
            ]
        })
    courses = sheets.courseinit()  # refreshes courses on every call
    viewId = res['view']['id']  # viewid is needed to update the modal
    data = courseJSON(coursecreate(courses))  # the data that we're sending to slack
    client.views_update(  # updates the default view with our new view
        view_id=viewId,  # uses viewid to find the location
        view=data  # the content that we're sending to the view
    )


# run server on port 3000
if __name__ == "__main__":
    courseStorage = runStudents(courses, students)
    print(courseStorage)
    # app.start(port=int(os.environ.get("PORT",3000)))
