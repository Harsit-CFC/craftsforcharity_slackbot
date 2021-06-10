# all imports
import copy  # copy to create deep copies of our pages so that the base files never change
import json  # json package used to load, modify, and dump our json
from datetime import date  # imports date formatting automatically
import os
from slack_bolt import App  # imports the app from slack that we use to connect

import sheets  # sheets.py, our file that formats our sheet data

import re  # the regex stuff

# json credentials
config = json.load(open('config.json'))


# datetime variables
def timereturn():
    t = date.today()
    timestamp = t.strftime("%B %d, %Y")
    return timestamp


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
        self.course = re.sub(r" ?\([^)]+\)", "",
                             course)  # dont change this please !!! or anything in the sheets in terms of names or
        # else something will break and i am NOT responsible for it!


# base json formats
MainPage = json.load(open('mainpage.json'))
StudentPage = json.load(open('studentpage.json'))
# spreadsheet variables
students = sheets.sheetinit()
courses = sheets.courseinit()


# construction functions
def coursecreate(chosenCourses):  # returns a course list => get courses from list and adds it to a classlist
    courselist = []  # list made to return all courses
    for i in chosenCourses:  # standard loop through list
        if i == "":  # if empty then pass
            pass
        else:  # if it has content then add it to courselist
            courselist.append(i)
    courselist.pop(0)
    return courselist


def coursejson(courselist):  # returns dumped json => insert courses in json format
    main_page_copy = copy.deepcopy(MainPage)
    timestamp = timereturn()
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


def coursefilters(courselist):  # returns nested list => creates a list for every value in courselist
    innerCourseStorage = [[] for _ in range(len(courselist))]
    for i in courselist:
        innerCourseStorage[courselist.index(i)].append(i)
    return innerCourseStorage


def coursematch(student,
                courselist):  # returns student.course as INTEGER => sets student course to the index of course value
    for c in courselist:
        if student.course == c:
            student.course = courselist.index(c)
    return student.course


def appendstorage(student, innerCourseStorage):  # no return => adds student to the course-specific list index
    innerCourseStorage[student.course].append(student)


def studentcreate(innerStudents):  # no return => creates the student object for all students
    courselist = coursecreate(courses)
    innerCourseStorage = coursefilters(courselist)
    for i in innerStudents:
        student = Applicant(i[2], i[3], i[4], i[6], i[7], i[9], i[8], i[14], i[11])
        student.course = coursematch(student, courselist)
        appendstorage(student, innerCourseStorage)
    return innerCourseStorage


# does all student functions, very important
def runstudents(innerCourses,
                innerStudents):  # runs all student-related functions to put them in the studentcopy json array
    courselist = coursecreate(innerCourses)
    # probably some double variable error here in the future!!!
    innerCourseStorage = coursefilters(courselist)
    innerCourseStorage = studentcreate(innerStudents)
    # courseStorage = studentBlocks(courseStorage)
    return innerCourseStorage


# Like in title, compiles the requested data into json using magic code
def compilerequesteddata(body, innerCourseStorage):  # returns json object from python dictionary
    timestamp = timereturn()
    classList = []
    student_page_copy = copy.deepcopy(StudentPage)
    student_page_copy["blocks"][1]["elements"][0]["text"] = timestamp + "  |  Crafts for Charity"
    options = body['view']['state']['values']['section678']['text1234']['selected_options']
    for text in options:
        classList.append(text['text']['text'])
    print(classList)
    for innerList in innerCourseStorage:
        if innerList[0] in classList:
            student_page_copy['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*" + innerList[0] + "*" + " :cfc:"
                }
            })
            student_page_copy['blocks'].append({
                "type": "divider"
            }, )
            print(innerList[1:])
            for student in innerList[1:]:
                student_page_copy['blocks'].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "" + student.student + " (" + student.numofstudents + ")" + " (" + student.hand + ")" + "| `" + student.time + " " + student.date + "` "
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Sign Up",
                        },
                        "value": "sign up",
                        "url": "https://docs.google.com/spreadsheets/d/1q4eK4VxqPZa0Bfg7rFuaKWnLQtAbAg_5wKzEE3xtQQY/edit?usp=sharing",
                        "action_id": "button-action"
                    }
                }, )
                print(student_page_copy)
                if student == innerList[len(innerList) - 1]:
                    student_page_copy['blocks'].append({
                        "type": "divider"
                    }, )
    print(student_page_copy)
    print(json.dumps(student_page_copy))
    return json.dumps(student_page_copy)


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
    innerCourses = sheets.courseinit()  # refreshes courses on every call
    viewId = res['view']['id']  # viewid is needed to update the modal
    data = coursejson(coursecreate(innerCourses))  # the data that we're sending to slack
    client.views_update(  # updates the default view with our new view
        view_id=viewId,  # uses viewid to find the location
        view=data  # the content that we're sending to the view
    )


@app.view("")
def handle_view_events(ack, body, client):
    ack()
    print(body)
    data = compilerequesteddata(body, courseStorage)
    response = client.views_open(
        trigger_id=body['trigger_id'],
        view=data
    )


# run server on port 3000
if __name__ == "__main__":
    courseStorage = runstudents(courses, students)
    print(courseStorage)
    app.start(port=int(os.environ.get("PORT", 3000)))
