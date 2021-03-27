'''
Merges AWL from multiple to a single file  sorted on the compile numbers
Also splits merged awl files to multiple files
'''
import os
import datetime
from operator import itemgetter

# global variabel for the version
gintVersion = "0.01"

# Logs the events to a file
class Logger:
    def __init__(self,logfile):
        try:
            self.logfile = open(logfile+".log", "a")
        except:
            input("Press enter to quit....")
        self.loglevel=2
        self.OutputToShell=1

    def getType(self, aType):
        strLogType="Diagnostic"
        if (aType==1): strLogType="Error"
        if (aType==2): strLogType="Event"
        return strLogType

    def getTimeStamp(self):
        strTS = datetime.datetime.now().isoformat()
        return strTS
        
    def logEvent(self, aType, aEvent):
        strLogType= self.getType(aType)
        strTS = self.getTimeStamp()

        strLine = strTS + ": " + strLogType +": " + aEvent+ "\n"
        if (self.loglevel>=aType): self.logfile.write(strLine)
        if (self.OutputToShell>=aType): print(strLine)

    def setLogLevel(self,aLoglevel):
        self.loglevel=int(aLoglevel)

    def stopLogging(self):
        self.logfile.close()
        
# Contains the functions to create the merge AWL    
class MergeAWL:
    def __init__(self, aPath, aLogger):
        self.Path = str(aPath)
        self.SourceFiles=[]
        self.SortedSources=[]
        self.sLogger = aLogger
        self.strStandardFolder = "/MergeAWL/"
        self.strStandardFile = "Merge.AWL"
        
    # Read files in the folder 
    def readFilesInFolder(self):
        FilesDirectory = self.Path + self.strStandardFolder 
        compileNumber = 0
        CNFCombo =[0,"File"] #format
        # read files in  directory
        try:
            for file in os.listdir(FilesDirectory):
                if os.path.isfile(os.path.join(FilesDirectory,file)) and file.lower().endswith(".awl"):
                    self.SourceFiles.append(file)
                    compileNumber = self.readCompileNumber(os.path.join(FilesDirectory,file))
                    if (compileNumber>0):
                        self.SortedSources.append([compileNumber,file])
                    else:
                        self.sLogger.logEvent(2,"Skipped: "+file)
        except:
            self.sLogger.logEvent(1,"Can not read directory: "+FilesDirectory+";Does this directory exist?")
            

    # Read the compile numbers
    def readCompileNumber(self,file):
        CNFCombo =[0,"File"] #format
        SourceFile = open(file,"r")
        SourceFileLines = SourceFile.readlines()
        # check the number of lines 
        if len(SourceFileLines)>1:
            CNIndex = SourceFileLines[1].find("CN:")
        else:
            self.sLogger.logEvent(1,"Empty file")
            return -1
        CompileNumber = SourceFileLines[1][CNIndex+3:].strip()
        SourceFile.close()
        if not CompileNumber.isdigit():
            self.sLogger.logEvent(1,file+"-"+CompileNumber+" : invalid compile number")
            print("Invalid compile number", file)
            CompileNumber = -1
        else:
            CompileNumber = int(CompileNumber)
        return CompileNumber

    def sortSourcesOnCN(self):
        self.SortedSources.sort()

    def writeMergeFile(self):
        # check if file is empty
        if (len(self.SortedSources)>0):
            try:            
                MergeFile = open(self.strStandardFile, "w")
            except:
                self.sLogger.logEvent(1,"Can not open file:"+self.strStandardFile)
            FileCounter = 0

            for File in self.SortedSources:
                FileToBeWritten = open(self.Path + self.strStandardFolder  + self.SortedSources[FileCounter][1],"r")
                MergeFile.write(FileToBeWritten.read())
                FileToBeWritten.close()
                FileCounter = FileCounter +1
            MergeFile.close()
        else:
            self.sLogger.logEvent(1,"No sources available to generate MergeAWL")

class SplitAWL:
    def __init__(self, aPath, aLogger):
        self.sLogger = aLogger
        self.sPath = aPath
        self.strStandardFolder = "/SplitAWL/"
        self.strStandardFile = "/Split.awl"
        self.arrStandardBlocks = ["ORGANIZATION_BLOCK", "FUNCTION_BLOCK", "FUNCTION ", "TYPE","DATA_BLOCK"]
        self.FileLines = []

    def readSplitAWL(self):
        strFilePath = self.sPath+self.strStandardFile
        try:
            self.sFile = open(strFilePath,"r")
            self.FileLines = self.sFile.readlines()
        except:
            self.sLogger.logEvent(1,"Can not read file: "+strFilePath)

    def findBeginOfFile(self, astrLine):
        sFilename =""
        intStart = astrLine.find('"')+1       # find first "
        intEnd = astrLine.find('"', intStart) # find last "
        
        for Block in self.arrStandardBlocks:
            if (astrLine.find(Block)==0):
                sFilename = astrLine[intStart:intEnd]
        return sFilename

    def checkFolderExisting(self):
        strPath =self.sPath + self.strStandardFolder
        if not (os.path.isdir(strPath)):
            try:
                os.mkdir(strPath)
            except:
                self.sLogger.logEvent(1,"Can not create folder: "+strPath)

    def splitAWL(self):
        intLineCounter = 0
        self.sFileCounter = 0
        self.checkFolderExisting()
        for line in self.FileLines:
            strFileName = self.findBeginOfFile(self.FileLines[intLineCounter])   
            if (len(strFileName)>0):
                self.sLogger.logEvent(3,"File: " + strFileName)
                sPath = self.sPath+self.strStandardFolder +strFileName+".AWL"
                try:
                    sFile = open(sPath,"w")
                    self.sFileCounter = self.sFileCounter + 1
                except:
                    self.sLogger.logEvent(1,"Can not open file: "+sPath)
            if self.sFileCounter >0:
                if not sFile.closed:
                    sFile.write(self.FileLines[intLineCounter])
                if ( self.FileLines[intLineCounter][0:4] == "END_"):
                    sFile.close()
            self.sLogger.logEvent(4, "Processed line "+str(intLineCounter)+" "+str(len(self.FileLines)))
            intLineCounter=intLineCounter+1

class User:
    def __init__(self):
        print("Welcome to MergeAWL. Version " + gintVersion)

    def showOptions(self):
        print("This script can merge and unmerge source files from TIA")
        print("Please pick one of the following options:")
        print("(1) Merge files (Folder MergeAWL should exist in working directory)")
        print("(2) Split files")
        print("(3) Quit")

    def getFunctionFromUser(self):
        intInput = 0
        iInput=str(input("Choose function to execute:")).strip()
        #check if it is a digit
        if iInput.isdigit():
            intInput = int(iInput)
            if intInput>3 : print("Incorrect value!")
        else:
            print("Incorrect value!")
        return intInput

def main():
    cLog = Logger("mergeAWL")
    cMerge = MergeAWL(os.getcwd(),cLog)
    cSplitter = SplitAWL(os.getcwd(),cLog)
    cUI = User()
    intFunction = 0

    cLog.logEvent(2,"---------------------- ")
    cLog.logEvent(2,"Start PyMerge version: "+gintVersion)
    cUI.showOptions()
    intFunction = cUI.getFunctionFromUser()
    if intFunction == 1:
        cLog.logEvent(2,"====Start of merge====")
        cLog.logEvent(2,"Working directory: "+cMerge.Path)
        cLog.logEvent(2,"Reading files in folder: "+ cMerge.Path+cMerge.strStandardFolder)
        cMerge.readFilesInFolder()
        cLog.logEvent(2,"Found files: "+ str(len(cMerge.SourceFiles)))
        cLog.logEvent(2,"Found compile numbers: "+str(len(cMerge.SortedSources)))
        cLog.logEvent(2,"Sort sources on compile numbers")
        cMerge.sortSourcesOnCN()
        cLog.logEvent(2,"Write files: "+cMerge.Path+cMerge.strStandardFile)
        cMerge.writeMergeFile()
    elif intFunction == 2:
        cLog.logEvent(2,"====Start of split====")
        cLog.logEvent(2,"Working directory: "+cSplitter.sPath)
        cLog.logEvent(2,"Read merged AWL file: "+cSplitter.sPath+cSplitter.strStandardFile)
        cSplitter.readSplitAWL()
        cLog.logEvent(2, "Number of lines: "+str(len(cSplitter.FileLines)))
        cLog.logEvent(2,"Split files to: "+cSplitter.sPath+cSplitter.strStandardFolder)
        cSplitter.splitAWL()
        cLog.logEvent(2,"Number of files split: "+str(cSplitter.sFileCounter))
    elif intFunction>3:
        cLog.logEvent(2,"Invalid value - no function executed")
    cLog.logEvent(2,"Done! Until next time!")
    cLog.stopLogging()
    
if __name__ =="__main__":
    main()

    

