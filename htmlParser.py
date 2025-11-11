# Parse HTML page to extract data in table
#
# run with command such as:
# python ./htmlParser.py ./testDir

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
        print("no table body found")
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
    for lab in labels:
        labeledRowData[lab] = "NO_DATA"

    while inTableBody:
        #rowData = list()


        classCount  += 1

        labelStart = classStart + 7
        labelEnd   = data[labelStart:].find("\"") + labelStart + 1
        label = data[labelStart:labelEnd-1]

        # verified field does not follow standard of other table fields and must be hard coded
        if label == "verified":
            fieldStart  = data[labelStart - 150:labelStart].find("verified:") + labelStart - 140
            fieldEnd    = data[fieldStart:rowEnd].find("\n") + fieldStart
            field       = data[fieldStart:fieldEnd].strip()

        # all other fields follow same standard
        else:
            fieldStart  = data[labelEnd:rowEnd].find(">") + labelEnd + 1
            fieldEnd    = data[fieldStart:rowEnd].find("<") + fieldStart
            field       = data[fieldStart:fieldEnd].strip()

        # only populate data from the found labels
        if field:
            labeledRowData[label] = field
            #if rowCount == 1:
                #print(f"found label {label} and field {field}")
                #print(f"labeledRowData now: {labeledRowData} ")
                #print(f"headerStart: {labelStart}  headerEnd: {labelEnd}  Header: {label}  field: {field}")

        # find next class
        classStart += 6
        classStart += data[(classStart):rowEnd].find("class=")

        # check if the next class tag is before the end of row tag
        if classStart > rowEnd or data[(classStart):rowEnd].find("class=") == -1:
            #print("found end of row data")

            #if rowCount == 1 or rowCount == 2:
            # add the current rows found data to the total found data and clear working dictionary
            for lab in labels:
                #print(f"Working on label {lab} adding value {labeledRowData[lab]}")
                compiledData[lab] += [labeledRowData[lab]]
                labeledRowData[lab] = "NO_DATA"

            # checks if there are no more rows left
            if data[rowEnd+3:].find("<tr") + rowEnd > tbodyEnd or data[rowEnd+3:].find("<tr") == -1:
                print("found end of file's table")
                #print(f"compiledData: {compiledData}")
                print(f"Rows in file: {len(compiledData[labels[0]])}")
                inTableBody = False
                break

            # more rows round, reset rowStart and rowEnd to the next row
            else:
                rowStart = data[rowEnd+3:].find("<tr") + rowEnd
                rowEnd   = data[rowStart:].find("</tr>") + rowStart + 1
                classStart = rowStart
                classStart = data[classStart:rowEnd].find("class=") + classStart
                classCount = 0
                rowCount += 1

    #print(f"found labels: {foundLabels}")
    df = pd.DataFrame(compiledData)
    return df
    print(f"processed rows {rowCount}")
    return firstRow

def parseLabels(data):
    foundLabels = list()
    inTableBody = False
    tbodyStart  = 0
    tbodyEnd    = 0

    # checks that there is a table body in the file
    if data[:].find("<tbody"):
        inTableBody = True
        tbodyStart  = data.find("<tbody")
        tbodyEnd    = data.find("</tbody")
    else:
        print("no table body found")
        return

    #print(f"tbodyStart = {tbodyStart}")
    #print(f"tbodyEnd = {tbodyEnd}")

    # find where the table row starts and ends
    rowStart    = 0
    rowEnd      = 0
    rowStart    = data[tbodyStart:].find("<tr") + tbodyStart
    rowEnd      = data[rowStart:].find("</tr>") + rowStart + 1
    rowCount    = 1

    # find possible labels in class tags
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

            # if going to a new row reset row pointers
            else:
                rowStart = data[rowEnd+3:].find("<tr") + rowEnd
                rowEnd   = data[rowStart:].find("</tr>") + rowStart + 1
                classStart = rowStart
                classStart = data[classStart:rowEnd].find("class=") + classStart
                classCount = 0
                rowCount += 1

        # used for internal testing
        classCount  += 1

        # find the next potential label
        labelStart = classStart + 7
        labelEnd   = data[labelStart:].find("\"") + labelStart + 1
        label = data[labelStart:labelEnd-1]

        # verified field does not follow standard of other table fields and must be hard coded
        if label == "verified":
            fieldStart  = data[labelStart - 150:labelStart].find("verified:") + labelStart - 140
            fieldEnd    = data[fieldStart:rowEnd].find("\n") + fieldStart
            field       = data[fieldStart:fieldEnd].strip()

        # all other fields follow same standard
        else:
            # fill field value after found label
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

        # offset the class start pointer by it's match length and search for next match
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
            print(f"given filepath {filePath}")
            fileNames.append(filePath)
        else:
            print(f"given directory: {filePath}")

            #print(f"filepath in try {filePath}")
            allEntries = os.listdir(filePath)
            #print(f"file or directory contents {allEntries}")
            # Filter out directories, keeping only files
            for entry in allEntries:
                fullPath = os.path.join(filePath, entry)
                #print(f"full_path: {fullPath}")
                if os.path.isfile(fullPath):
                    fileNames.append(fullPath)

        #print(f"compiled file names: {fileNames}")
        print(f"Number of found files in directory: {len(fileNames)}")

        for file in fileNames:
            # read data from html file
            fileData = Path(fileNames[0]).read_text()

            # collect table data labels
            for labs in parseLabels(fileData):
                if labs not in labels:
                    labels.append(labs)

        #print(f"found labels: {labels}")
        print(f"Total number of labels found: {len(labels)}\n")

        # collect table values
        fileCounter = 1
        for file in fileNames:
            # read data from html file
            fileData = Path(fileNames[0]).read_text()

            if len(compiledData) < 5:
                compiledData = parseData(fileData, labels)
            else:
                compiledData = pd.concat([parseData(fileData, labels), compiledData], ignore_index = True)

            print(f"After {fileCounter} file processed {len(compiledData)} rows\n")
            fileCounter += 1
        #compiledData = pd.concat([parseData(fileData, labels), compiledData], ignore_index = True)
        #print(f"after 2 runs len(compiledData) {len(compiledData)}")

        # export csv
        compiledData.to_csv("./parsedData.csv")
    except Exception as e:
        print(f"Error openeing file: {e}")
