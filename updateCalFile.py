#!/usr/bin/python

import sys
import os.path
import re

unwantedWords=["*", "#", "inf", "nan"]

def getArrDict(lineArray):
    """For reading the line array and converting the relevant part into a dictionary"""
    arrDict={}
    for row in lineArray:
        if any(uWord in row for uWord in unwantedWords):
            # print("Found unwanted word skipping line")
            # print("row = "+str(row))
            continue
        splRow=row.split()
        # print(splRow)
        intList=re.findall(r'\d+',splRow[0])
        if len(intList) == 0:
            # print("Don't want these cases either")
            continue
        # print(intList)
        tNum=intList[0]
        splRow[0]=tNum
        # print(splRow)
        arrDict[splRow[0]]=splRow[1:]
    # print(arrDict)
    return arrDict
        
def getNicerList(oldLines):
    nicerList=[]
    for i in range(len(oldLines)):
        row=oldLines[i]
        if any(uWord in row for uWord in unwantedWords):
            #Leaving the row as is
            nicerList.append(row) #element is a string
            continue
        nicerList.append(row.split()) #element is a list of strings

    return nicerList

def getStringyfyedList(myNiceList):
    stringyL=[]
    for myNiceE in myNiceList:
        #Horrible way of doing it but at least is python version independent
        if type(myNiceE) == type([]): #var is a list
            newE='\t'.join(myNiceE)
            stringyL.append(newE)
        else:
            stringyL.append(myNiceE)
    return stringyL

def specialMergeList(myArrDict,nicerList,myShift):
    for myElement in nicerList:
        #Horrible way of doing it but at least is python version independent
        if type(myElement) == type([]): #var is a list
            # print("variable a is a list")
            myTNum=myElement[0] #It's actually a string of an integer but, who cares?
            if myTNum in myArrDict:
                a=myArrDict[myTNum][0]
                b=myArrDict[myTNum][3]
                #Might be handy here to add conditionals with respect to the errors
                myElement[myShift]=a
                myElement[myShift+1]=b


def main(argv):
    if len(argv[1:]) != 4:
        print("usage:\n\t"+str(argv[0])+" --LG values4Update oldCalFile newUpdatedFile")
        print("\t"+str(argv[0])+" --HG values4Update oldCalFile newUpdatedFile\n")
        return

    gainVar=argv[1]

    if gainVar not in ["--LG","--HG"]:
        print("error: "+gainVar+" is neither --LG or --HG.")
        return

    #For selecting the right columns for the parameters
    if gainVar == "--HG":
        myShift=3
    else:
        myShift=5

    val4Updt=argv[2]
    oldCFName=argv[3]
    nUFile=argv[4]

    if not os.path.isfile(val4Updt):
        print("error: values4Update = \""+val4Updt+"\" must exist and be a regular file.")
        return

    with open(val4Updt, 'r') as val4UData:
        val4UData= val4UData.readlines()
        # print (oldData)
        myArrDict=getArrDict(val4UData)

    if not os.path.isfile(oldCFName):
        print("error: oldCalFile = \""+oldCFName+"\" must exist and be a regular file.")
        return

    with open(oldCFName, 'r') as oldDF:
        oldDataL = oldDF.readlines()
        # print (oldDataL)
        nicerList=getNicerList(oldDataL)
        # print(nicerList)

    # print(myArrDict['1121'])
    # print(nicerList[1155])
    specialMergeList(myArrDict,nicerList,myShift)
    # print(nicerList[1155])
    # print("Now stringifying!!")
    myStrL=getStringyfyedList(nicerList)
    # print(myStrL)
    #May add extra \n cause of undisturbed str
    myStr2Save='\n'.join(myStrL)
    #converting all \n\n into \n
    myStr2Save=myStr2Save.replace('\n\n','\n')
    myStr2Save+='\n' #One extra at the very end
    # print(myStr2Save)
    
    #This is for later, put some warning about updating or an option to forse it if file exists.
    # if os.path.isfile(nUFile):
    #     print("error: values4Update = \""+val4Updt+"\" must exist and be a regular file.")
    #     return

    with open(nUFile,'w') as place2Write:
        print("Saving data in "+nUFile)
        place2Write.write(myStr2Save)

if __name__ == "__main__":
   main(sys.argv)
