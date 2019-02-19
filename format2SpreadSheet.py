#!/usr/bin/python

import sys
import os
from os.path import basename #For printing nicely argv[0]

gpltDir="files4Gnuplot/"
newListOfEnergD=[] #Just avoiding errors

#Chimera's telescope numbers
teles_num=[16, 16, 24, 24, 32, 32, 40, 40, 40, 40, 48, 48, 48, 48, 48,
           48, 48, 48, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
           32, 32, 32, 16, 8]

#Making a list of accepted options
accOpts=["-c", "-C", "-s", "--prefixShift","-h","--help","--range"]
ignoreOp4Header=["--prefixShift","-h","--help","--range"]

def getPreShiftFromCMDL(myOptDict,argv):
    """Multipuspose function returns False if vals not ok and the vals if
all is fine"""
    myEVal="--prefixShift"
    if len(myOptDict[myEVal]) != 2:
        print("error: "+myEVal+" needs exactly 2 arguments")
        return False
    preStr,shiftStr=[argv[myOptIdx] for myOptIdx in myOptDict[myEVal]]
    if not shiftStr.isdigit():
        print("error: shiftInt="+shiftStr+" should be an integer")
        return False
    shiftInt=int(shiftStr)
    if shiftInt < 0:
        print("error: shiftInt"+shiftStr+" should be a positive integer")
        return False
    return [preStr,shiftInt]

def getIdxList2Ignore(myOptDict):
    idxList2Ignore=[]

    for e in ignoreOp4Header:
        if e in myOptDict:
            idxList2Ignore+=myOptDict[e]

    return idxList2Ignore

def getRingIdxFromTNum(tNum):
    if tNum < 0 or tNum > 1192:
        return None
    cumulTNum=0
    for rIdx in range(len(teles_num)):
        if cumulTNum <= tNum < cumulTNum+teles_num[rIdx]:
            return rIdx
        cumulTNum+=teles_num[rIdx]

def getCleanStrL(fName, sColBool=True):
    # print("fName = %s" % fName)
    myFile = open(fName,'r')

    # retVal=myFile.read()
    myLines=myFile.readlines()
    retVal=[]
    for myLine in myLines:
        if myLine[0] == '#' or myLine[0] == '*' or myLine == '\n':
            continue
        tmpList=myLine.rstrip().split('\t')
        if len(tmpList) != 2 and sColBool:
            #Ignoring lines with one column
            continue
        retVal.append(tmpList)
    myFile.close()
    return retVal

def getRange(argv, myOptDict):
    eVar="--range"
    if len(myOptDict[eVar]) != 2:
        print("error: "+eVar+" should have exactly two integers.")
        return False

    minVal,maxVal=argv[myOptDict[eVar][0]],argv[myOptDict[eVar][1]]

    if not minVal.isdigit() or not maxVal.isdigit():
        print("error: range values need to be positive integers")
        return False
    
    minInt=int(minVal)
    maxInt=int(maxVal)

    if minInt < 0 or maxInt < 0:
        print("error: range integers have to be positive")
        return False

    if minInt > maxInt:
        print("error: need min < max.")
        return False

    return minInt,maxInt

def inTestRange(nHN):
    for val in nHN:
        if val not in range(1192):
            return False
    return True

#Did I mean prefix..?!
def getSuffixAndShift(valList):
    if valList[0][0].isdigit():
        return "",0
    suffix=valList[0][0][0]
    justHistNums=[int(val[0][1:]) for val in valList]
    delta=12000 #assuming shift is a multiple of 12000
    shift=0
    for i in range(20): #a "normal" range to search
        shift+=delta
        newHistNums=[hVal-shift for hVal in justHistNums]
        if inTestRange(newHistNums):
            return suffix,shift
    return suffix,"None"

def getModifDL1(myDL1,myOptDict,argv):
    if "--prefixShift" in myOptDict:
        suffix,shift=getPreShiftFromCMDL(myOptDict,argv)
    else:
        suffix,shift=getSuffixAndShift(myDL1)
    # modifDL1=[[int(val[0])-shift for val in myDatList[1]],myDa]

    if suffix == "":
        for myVal in myDL1:
            myVal[0]=int(myVal[0])
    else:
        for myVal in myDL1:
            myVal[0]=int(myVal[0][1:])-shift
            # print("myVal[0] = ",myVal[0])
    return myDL1

def getTelesIdxInList(myDataStuff,telesNum):
    place2Find=myDataStuff[1]
    for i in range(len(place2Find)):
        locLstVal=place2Find[i]
        if telesNum == locLstVal[0]:
            return i
    return None

def getList2Print(myDatList,idx):
    idxList=[getTelesIdxInList(myDatStuff,idx) for myDatStuff in myDatList]
    list2Print=[]
    # eightSpaces="        "
    for newIdx in range(len(idxList)):
        if idxList[newIdx] == None:
            list2Print.append("")
        else:
            list2Print.append(myDatList[newIdx][1][idxList[newIdx]][1])
    return list2Print

def getCleaner4EnerStrL(cleanedStrL):
    """Just a special case for handling the energy files, it just
reformats the given list in a nicer way"""
    cleaner4EnerStrL=[e[0] for e in cleanedStrL]
    return cleaner4EnerStrL

def createGpltDir():
    newpath = gpltDir
    if not os.path.exists(newpath):
        os.makedirs(newpath)

def isFloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def checkIfAtLeast2Chans(list2Check):
    minRequirement=2
    totFound=0
    for e in list2Check:
        if isFloat(e):
            totFound+=1
        if totFound >= minRequirement:
            return True
    return False

def getMyOptDict(myArgs):
    myOptDict={}

    tmpOpt=''
    for i in range(len(myArgs)):
        e=myArgs[i]
        if e[0] == '-':
            myOptDict[e]=[]
            tmpOpt=e
            continue #Just skipping the option

        if tmpOpt != '':
            myOptDict[tmpOpt].append(i)

    return myOptDict

def quickOptParse(argv,myOptDict):
    for myOptKey in myOptDict:
        if myOptKey not in accOpts:
            print("error: option="+myOptKey+" is not a valid option")
            return False

        if myOptKey == "-h" or myOptKey == "--help":
            printHelp(argv,True)
            return False

        if myOptDict[myOptKey] == []:
            print("error: "+str(myOptKey)+" should have at least one argument")
            return False
    return True

def getOrdKL(dict2Ord):
    list2Order=[]
    for myK in dict2Ord:
        list2Order.append([myK,dict2Ord[myK][0]])

    list2Order.sort(key=lambda x: x[1])
    list2Send=[e[0] for e in list2Order]
    return list2Send

def getFinalChFileIdx(myArgs,ordKL):
    if len(ordKL) == 0:
        return len(myArgs)-1
    firstOpt=ordKL[0]
    for myArg,idx in zip(myArgs[1:],range(1,len(myArgs[1:])+1)):
        if myArg == firstOpt:
            return idx-1

def getListOfKeys(myDatList):
    listOfKeys=[]
    for myV in myDatList:
        for myValPair in myV[1]:
            if myValPair[0] not in listOfKeys:
                listOfKeys.append(myValPair[0])

    return listOfKeys

# def lowerCHandling(myLowerCIdxList,argv):
#     for myIdx in myLowerCIdxList:

#     pass

def printHelp(argv,hBool=False):
    print("usage: %s chFiles... [options] #use -h for help"\
          % basename(argv[0]))
    if hBool:
        print("options:")
        print("\t-h | --help:\t displays this menu.")
        print("\t-c eFiles... :\t expects a set of files chimera format, 35 lines single col.")
        print("\t-C Efiles... :\t expects a set of 2 col tNum (or histo) energ files.")
        print("\t-s enerVa... :\t expects a set of values that will be the same for all rows.")
        print("\t--prefixShift:\t expects a prefix and a shift rule for converting histograms to teles.\t")
        print("\t--range min max:\t expects the range for printing the rows.")

def main(argv):
    myRange=False
    myMinIntV,myMaxIntV=660,669

    myOptDict=getMyOptDict(argv)
    if not quickOptParse(argv,myOptDict):
        return
    ordKL=getOrdKL(myOptDict)
    # print(ordKL)
    # return
    pltFBool=False
    if len(argv) == 1:
        printHelp(argv)
        return
    myData=[]
    listOfEnerg=[]

    newListOfEnergD=[]

    finalChFileIdx=getFinalChFileIdx(argv,ordKL)

    fChAL=range(1,finalChFileIdx+1)
    nChFiles=len(fChAL)
    restSum=0
    for myOpVar in myOptDict:
        if myOpVar in ignoreOp4Header :
            #Excluding this from the sum
            continue
        restSum+=len(myOptDict[myOpVar])

    if nChFiles == restSum:
        createGpltDir()
        pltFBool=True

    # for myArg,idx in zip(argv[1:],range(1,len(argv[1:])+1)):
    for myArg,idx in zip(argv[1:],range(1,finalChFileIdx)):
        myData.append([myArg,getCleanStrL(myArg)])

    # print(myData)
    myLOfK=getListOfKeys(myData)
    # print(myLOfK)
    #Now loop through the options
    for e in ordKL:
        #Now loop through the corresponding indices
        if ( e == '-c'):
            for myOptIdx in myOptDict[e]:
                myFileName=argv[myOptIdx]
                myEList=getCleanStrL(myFileName,False)
                cleanerEList=getCleaner4EnerStrL(myEList)
                if len(cleanerEList) != 35:
                    print("error: we need exactly 35 values in %s!!" %myFileName)
                    return
                listOfEnerg.append(cleanerEList)
        if ( e == '-C'):
            #First make the list of empty dictionaries<
            newListOfEnergD=[{} for myAwesomeVar in myOptDict[e]]
            for myOptIdx,myNewIdx in zip(myOptDict[e],range(len(myOptDict[e]))):
                # locEnergDict[argv[myIdx]]={}
                # print("myOptIdx = "+str(myOptIdx))
                myFileName=argv[myOptIdx]
                myNewEList=getCleanStrL(myFileName,True) #Need exactly 2 columns
                #Now need to assign to the corresponing dict list newListOfEnergD somehow
                for myLEle in myNewEList:
                    # myNewIdx is the idx position in the list of dictionares
                    # myLEle[0] is a string (avoids errors) I'm expecting a number
                    # myLEle[1] is the corresponding energy
                    newListOfEnergD[myNewIdx][myLEle[0]]=myLEle[1]

        if ( e == '-s'):
            termEList=[argv[myOptIdx] for myOptIdx in myOptDict[e]]

        if ( e == '--prefixShift' ):
            preSh=getPreShiftFromCMDL(myOptDict,argv)
            if preSh == False:
                return

        if ( e == "--range" ):
            print("Handling the range option")
            myRange=getRange(argv, myOptDict)
            if myRange == False:
                return

    for myDatList in myData:
        suffix,shift=getSuffixAndShift(myDatList[1])
        if shift=="None":
            print("error: unable to find the shift")
            return
        myDatList[1]=getModifDL1(myDatList[1],myOptDict,argv)#myData is being modified here

    headerStr="#telesN"

    idxList2Ignore=getIdxList2Ignore(myOptDict)
    for fileName,theIdx in zip(argv[1:],range(1,len(argv))):
        # if fileName == "-c" or fileName == "-C": #Change to in options or something
        if fileName in accOpts or theIdx in idxList2Ignore:
            continue
        headerStr+=", "+fileName

    # return
    print(headerStr)

    # print("Stopped deliverately")
    # return

    # for i in range(0,1192):

    if myRange != False:
        myMinIntV,myMaxIntV=myRange
    
    for i in range(myMinIntV,myMaxIntV):
        list2Print=getList2Print(myData,i) #These are the channels
        baseStr=str(i)+", "+", ".join(list2Print)
        myLocEList=[]
        for ordOpt in ordKL:
            if ordOpt == "-c":
                for enerList in listOfEnerg: #These are the E values in 35 line format
                    #Put a condition here in case returns None
                    baseStr+=", "+enerList[getRingIdxFromTNum(i)]
                    myLocEList.append(enerList[getRingIdxFromTNum(i)])
            if ordOpt == "-C":
                for newDictIter,myDictIdx in zip(newListOfEnergD,range(len(newListOfEnergD))):
                    if str(i) in newDictIter:
                        baseStr+=", "+newDictIter[str(i)]
                    else:
                        baseStr+=", "
            if ordOpt == "-s":
                baseStr+=", "
                baseStr+=", ".join(termEList)
        print(baseStr)

        if pltFBool:
            tVar=gpltDir+"t"+str(i)+".txt"
            if checkIfAtLeast2Chans(list2Print):
                with open(tVar, 'w') as gpltFile:
                    for chan,energy in zip(list2Print,myLocEList):
                        if chan != "":
                            gpltFile.write(str(chan)+"\t"+str(energy)+"\n")

    if pltFBool:
        print("#A directory  ("+gpltDir+") was filled with txt files for calibration purposes.")


if __name__ == "__main__":
   main(sys.argv)
