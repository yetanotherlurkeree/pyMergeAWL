import os
import sys

sys.path.append("../pyMergeAWL")
from MergeAWL import MergeAWL
from MergeAWL import Logger
#from MergeAWL.MergeAWL.py import MergeAWL

import pytest

def test_read_one_file():
    logger =Logger("log")
    # create folder if it does not exist
    #
    if not os.path.exists(path=os.getcwd() + "/MergeAWL"):
        try:
            os.mkdir("MergeAWL")
        except:
            print("Could not create folder")

    #create a file
    try:
        file = open("MergeAWL/Test.AWL",'w')
        file.write("test")
        file.close()
    except Exception as e:
        print(e)
        print("Could not do it...")
    test = MergeAWL(os.getcwd(), logger)
    test.readFilesInFolder()

    assert(len(test.SourceFiles) ==1)
