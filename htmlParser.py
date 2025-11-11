# parse HTML page to extract data in table
# script needs to be run where the directory containing the html files is located
# can be run against a single file in current working directory or all files in a given directory in current working directory
# run with command such as (obviously an example command below):
# python .\htmlParser.py .\testDir

import sys
import os
import pandas as pd
from datetime import date
from pathlib import Path

def parseData(data, labels):
    compiledData = {}
    for label in labels:
        compiledData[label] = []

    inTableBody = False
    tbodyStart  = 0
    tbodyEnd    = 0

    # checks that there is a table body in the file
    if data[:].find("<tbody"):
        inTableBody = True
        tbodyStart  = data.find("<tbody")
        tbodyEnd    = data.find("</tbody")
    else:
        print("No table body found!")
        return

    #print(f"tbodyStart = {tbodyStart}")
    #print(f"tbodyEnd = {tbodyEnd}")

    # find where the table row starts and ends
    rowStart    = 0
    rowEnd      = 0
    rowStart    = data[tbodyStart:].find("<tr") + tbodyStart
    rowEnd      = data[rowStart:].find("</tr>") + rowStart + 1
    rowCount    = 1

    firstRow = data[rowStart:rowEnd+4]
    #print(f"rowStart = {rowStart}")
    #print(f"rowEnd = {rowEnd}")

    # find possible labels in class tags
    classStart = rowStart
    classStart = data[classStart:rowEnd].find("class=") + classStart
    classCount = 0
    #print(f"first class found at {classStart}")

    labeledRowData = {}
    for label in labels:
        labeledRowData[label] = "Null"

    while inTableBody:
        #rowData = list()

        classCount  += 1

        labelStart = classStart + 7
        labelEnd   = data[labelStart:].find("\"") + labelStart + 1
        labelCheck = data[labelStart:labelEnd-1]

        # verified field does not follow standard of other table fields and must be hard coded because of vendor stupidity
        if labelCheck == "verified":
            fieldStart  = data[labelStart - 150:labelStart].find("verified:") + labelStart - 140
            fieldEnd    = data[fieldStart:rowEnd].find("\n") + fieldStart
            field       = data[fieldStart:fieldEnd].strip()

        # all other fields follow same standard
        else:
            fieldStart  = data[labelEnd:rowEnd].find(">") + labelEnd + 1
            fieldEnd    = data[fieldStart:rowEnd].find("<") + fieldStart
            field       = data[fieldStart:fieldEnd].strip()

        # only populate data from the found labels; overwrite null value
        if field:
            labeledRowData[labelCheck] = field
            #if rowCount == 1:
                #print(f"found label {labelCheck} and field {field}")
                #print(f"labeledRowData now: {labeledRowData} ")
                #print(f"headerStart: {labelStart}  headerEnd: {labelEnd}  Header: {labelCheck}  field: {field}")

        # find next class
        classStart += 6
        classStart += data[(classStart):rowEnd].find("class=")

        # check if the next class tag is before the end of row tag
        if classStart > rowEnd or data[(classStart):rowEnd].find("class=") == -1:
            #print("found end of row data")

            #if rowCount == 1 or rowCount == 2:
            # add the current rows found data to the total found data and clear working dictionary
            for label in labels:
                #print(f"Working on label {label} adding value {labeledRowData[label]}")
                compiledData[label] += [labeledRowData[label]]
                labeledRowData[label] = "Null"

            # checks if there are no more rows left
            if data[rowEnd+3:].find("<tr") + rowEnd > tbodyEnd or data[rowEnd+3:].find("<tr") == -1:
                print("Found end of file's table")
                #print(f"compiledData: {compiledData}")
                print(f"Rows in file: {len(compiledData[labels[0]])}")
                inTableBody = False
                break

            # more rows found, reset rowStart and rowEnd to the next row
            else:
                rowStart = data[rowEnd+3:].find("<tr") + rowEnd
                rowEnd   = data[rowStart:].find("</tr>") + rowStart + 1
                classStart = rowStart
                classStart = data[classStart:rowEnd].find("class=") + classStart
                classCount = 0
                rowCount += 1

    #print(f"found labels: {foundLabels}")
    # finally convert compiled data to pandas dataframe for easy csv export
    df = pd.DataFrame(compiledData)
    return df

def parseLabels(data):
    foundLabels = list()
    inTableBody = False
    tbodyStart  = 0
    tbodyEnd    = 0

    # checks that there is a table body in the file
    if data[:].find("<tbody"):
        inTableBody = True
        # will give starting index of first occurrence of tbody tag
        tbodyStart  = data.find("<tbody")
        # will give starting index of first occurrence of tbody end tag
        tbodyEnd    = data.find("</tbody")

    else:
        # this may turn into a headache later if formatting is inconsistent between files, basic basic error handling for now
        print("No table body found!")
        return

    #print(f"tbodyStart = {tbodyStart}")
    #print(f"tbodyEnd = {tbodyEnd}")

    # find where the table row starts and ends
    rowStart    = 0
    rowEnd      = 0
    # adding the offset of tbodyStart to get the correct index in rowStart
    rowStart    = data[tbodyStart:].find("<tr") + tbodyStart
    # adding the offset of rowStart to get the correct index in rowEnd
    rowEnd      = data[rowStart:].find("</tr>") + rowStart + 1
    rowCount    = 1

    # find possible labels in class tags, we don't like buttons
    classStart = rowStart
    classStart = data[classStart:rowEnd].find("class=") + classStart
    classCount = 0

    # parse data in table
    while inTableBody:
        field = ""
        # check if the next class tag is before the end of row tag
        if classStart > rowEnd or data[(classStart):rowEnd].find("class=") == -1:

            # checks if there are no more rows left
            if data[rowEnd+3:].find("<tr") + rowEnd > tbodyEnd or data[rowEnd+3:].find("<tr") == -1:
                inTableBody = False
                break

            # if going to a new row reset row index (keri doesn't know c++ to use pointers); else logic can turn into a headache later if formatting is inconsistent
            else:
                rowStart = data[rowEnd+3:].find("<tr") + rowEnd
                rowEnd   = data[rowStart:].find("</tr>") + rowStart + 1
                classStart = rowStart
                classStart = data[classStart:rowEnd].find("class=") + classStart
                classCount = 0
                rowCount += 1

        # used for internal testing
        classCount  += 1

        # find the next potential label, hopefully 7 characters from start of class to data value
        labelStart = classStart + 7
        labelEnd   = data[labelStart:].find("\"") + labelStart + 1
        label = data[labelStart:labelEnd-1]

        # verified field does not follow standard of other table fields and must be hard coded because of vendor stupidity
        if label == "verified":
            fieldStart  = data[labelStart - 150:labelStart].find("verified:") + labelStart - 140
            fieldEnd    = data[fieldStart:rowEnd].find("\n") + fieldStart
            field       = data[fieldStart:fieldEnd].strip()

        # all other fields follow same standard
        else:
            # fill field value after found label, delimited by html tags
            fieldStart  = data[labelEnd:rowEnd].find(">") + labelEnd + 1
            fieldEnd    = data[fieldStart:rowEnd].find("<") + fieldStart
            field       = data[fieldStart:fieldEnd].strip()

        # only keep the label and data if there is data associated with a possible label
        if field:
            #if rowCount == 1:
                #print(f"found label {label} and field {field}")
                #print(f"labeledRowData now: {labeledRowData} ")
                #print(f"headerStart: {labelStart}  headerEnd: {labelEnd}  Header: {label}  field: {field}")
            if label not in foundLabels:
                foundLabels.append(label)

        # offset the class start index by it's match length and search for next match
        classStart += 6
        classStart += data[(classStart):rowEnd].find("class=")

    return foundLabels

if __name__ == '__main__':

    filePath = ""
    fileData = ""
    labels = list()
    compiledData = ""

    for arg in sys.argv[1:]:
        # check if the given argument references a file or directory in the current path
        if arg[0:2] == ".\\":
            filePath = arg

        else:
            #default file path
            filePath = "./20251027_save as sept data.html"

    # make sure the given file can be opened
    try:
        fileNames = []
        # determines if the given argument is a file or directory
        if filePath[2:].find('.') > 0:
            # print file path and add to fileNames array 
            print(f"Given filepath: {filePath}")
            fileNames.append(filePath)
        else:
            # assuming if no . in argument then it is a directory
            print(f"Given directory: {filePath}")
            allEntries = os.listdir(filePath)

            #print(f"file or directory contents {allEntries}")
            # filter out directories, keeping only files
            for entry in allEntries:
                # prefix directory path to file name to get full relative path (not to be mistaken with absolute path duh)
                fullPath = os.path.join(filePath, entry)
                #print(f"full_path: {fullPath}")
                # we're checking things in a directory to only add files to the fileNames array
                if os.path.isfile(fullPath):
                    fileNames.append(fullPath)

        # now we have a list of files to process in fileNames array only printing number unless I want more detail
        #print(f"compiled file names: {fileNames}")
        print(f"Number of found files in directory: {len(fileNames)}")

        for file in fileNames:
            # read data from html file, we aren't worried about efficiency since it's not a lot of data
            fileData = Path(fileNames[0]).read_text()

            # collect table data labels
            for label in parseLabels(fileData):
                if label not in labels:
                    labels.append(label)

        # now we have a list of all column headers in labels, only printing number unless I want more detail
        #print(f"found labels: {labels}")
        print(f"Total number of labels found: {len(labels)}\n")

        # TODO confirm total number of labels expected with real data 

        # collect table data values
        fileCounter = 1
        for file in fileNames:
            # read data from html file, we aren't worried about efficiency since it's not a lot of data
            fileData = Path(fileNames[0]).read_text()

            if len(compiledData) < 5:
                compiledData = parseData(fileData, labels)
            else:
                compiledData = pd.concat([parseData(fileData, labels), compiledData], ignore_index = True)

            # print cumulative number of rows processed after each file - good to remove from for loop after complete testing
            print(f"After {fileCounter} file processed {len(compiledData)} rows\n")
            fileCounter += 1

        # export csv
        # this is a hardcoded output file name
        compiledData.to_csv("./parsedData.csv")

        # TODO pull current date and append to csv file name to avoid overwriting previous data files

    # try block failure error handling
    except Exception as e:
        print(f"Error opening file: {e}")
