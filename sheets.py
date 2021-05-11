import csv
import ezsheets
import os

def sheetinit():
    ss = ezsheets.Spreadsheet('1iA6Wh31JKgqBVflHOb-gidD91Ru6D43ntzGqHpdLGOI')
    ss.downloadAsCSV()
    sheetfilecsv = open('Coding_CFC_Classes_Sign_Up_.csv')
    sheetdatacsv = csv.reader(sheetfilecsv)
    dataList = list(sheetdatacsv)
    dataList.pop(0)
    return dataList

def courseinit():
    ss = ezsheets.Spreadsheet('1iA6Wh31JKgqBVflHOb-gidD91Ru6D43ntzGqHpdLGOI')
    sh = ss.sheets[4]
    courses = sh.getColumn(1)
    return courses