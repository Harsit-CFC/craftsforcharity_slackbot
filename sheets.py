import csv

import ezsheets
import json
config = json.load(open('config.json'))

def sheetinit():
    ss = ezsheets.Spreadsheet(config['spreadsheet'])  # grab the google spreadsheet id
    ss.downloadAsCSV()
    sheetfilecsv = open('CFC_Classes_Sign_Up_.csv')
    sheetdatacsv = csv.reader(sheetfilecsv)
    dataList = list(sheetdatacsv)
    dataList.pop(0)
    return dataList


def courseinit():
    ss = ezsheets.Spreadsheet(config['spreadsheet'])  # grab the google spreadsheet id
    sh = ss.sheets[4]
    courses = sh.getColumn(1)
    return courses
