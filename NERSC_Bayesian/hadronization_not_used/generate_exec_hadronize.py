import os
import stat
import os.path
import re
import math
import shutil
import time
import getopt
import sys
import fileinput
import pathlib


def checkAndBuildDir(checkDir):
    if (not os.path.isdir(checkDir)):
        print("Creating directory \""+checkDir+"\" ...")
        os.mkdir(checkDir)


##### Input parameters #####
baseDir = str(pathlib.Path(__file__).parent.absolute())+"/"
extPartType1 = "Partons"
extPartType2 = "Hadrons"

preCompiled_Raw = "runJetscape"
preCompiled_Par = "FinalStatePartons"
preCompiled_Had = "FinalStateHadrons"

queueType = "regular"
maxTime = 2  # in hours
repeatRange = range(0, 10)

pThatPair = [1, 2, 3, 4, 5, 7, 9, 11, 13, 15, 17, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230,
             240, 250, 260, 270, 280, 290, 300, 350, 400, 450, 500, 550, 600, 700, 800, 900,  1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2200, 2400, 2510]
pThat_Min = pThatPair[:-1]
pThat_Max = pThatPair[1:]

##### End of input parameters #####

##### Checking that right directories exist and creating them as needed #####

checkAndBuildDir(os.path.join(baseDir, "builds"))
checkAndBuildDir(os.path.join(baseDir, "InputFiles"))
checkAndBuildDir(os.path.join(baseDir, "SubScripts"))
checkAndBuildDir(os.path.join(baseDir, "OutputFiles"))

def hadronizeWith(outputFolder, fileName):
    checkAndBuildDir(os.path.join(baseDir, "OutputFiles/"+outputFolder))
    for m in repeatRange:
        for n in range(len(pThat_Min)):
    
            FileStr = str(pThat_Min[n]).zfill(4)+"_"+str(pThat_Max[n]).zfill(4) + \
                "_ev_"+str(10*(m)).zfill(3)+"k_to_"+str(10*(m+1)).zfill(3)+"k"
            OutDir = "OutputFiles/"+outputFolder+"/"

            os.system("cp "+baseDir+"OutputFiles/Header* "+baseDir+OutDir)

            inputfileName = baseDir+"/InputFiles/jetscape_hadronize_"+outputFolder+"_Bin" + \
                str(pThat_Min[n])+"_"+str(pThat_Max[n])+"_"+str(m)+".xml"
            os.system("cp "+baseDir+"/"+fileName+" " + inputfileName)

            for line in fileinput.input([inputfileName], inplace=True):
                if 'outputFilename' in line:
                    line = '<outputFilename>'+baseDir+"/"+OutDir+FileStr+'</outputFilename>\n'

                if 'inputName' in line:
                    Input_Par = "OutputFiles/"+extPartType1+"_"+FileStr+".dat"
                    line = '      <inputName>'+baseDir+"/"+Input_Par+'</inputName>\n'

                sys.stdout.write(line)

            buildDir = "builds/build_"+outputFolder+FileStr
            buildDir = os.path.join(baseDir, buildDir)

            execFileName = "SubScripts/sub_"+outputFolder+FileStr
            Input = "/InputFiles/jetscape_hadronize_"+outputFolder+"_Bin" + \
                str(pThat_Min[n])+"_"+str(pThat_Max[n])+"_"+str(m)+".xml"

            Input_Had = OutDir+FileStr+".dat"
            Output_Had = OutDir+extPartType2+"_"+FileStr+".dat"

            if (os.path.exists(Output_Had)):
                continue

            execFile = open(execFileName, "w")

            #Write: Header
            execFile.writelines("#!/usr/bin/env bash\n")
            execFile.writelines("mkdir -p " +
                            buildDir + "/build" + "\n")
            execFile.writelines("cd " + baseDir + "\n")
            execFile.writelines("cp -rf JETSCAPE/* " +
                            buildDir + "\n")

            # Write: Go to directory
            execFile.writelines("cd " + buildDir + "/build" "\n")
            execFile.writelines("cmake "+ buildDir+"\n")
            execFile.writelines("make\n")

            #Write: Run

            execFile.writelines("time "+buildDir + "/build/"+preCompiled_Raw+" "+baseDir+Input +
                            " 1> "+baseDir+OutDir+"Non-PBS_"+FileStr+".log 2> "+baseDir+OutDir+"Non-PBS_"+FileStr+".err\n")

            execFile.writelines("time "+buildDir+"/build/"+preCompiled_Had+" "+baseDir+Input_Had+" "+baseDir+Output_Had+" 1> "+baseDir +
                            OutDir+"Non-PBS_Hadrons_"+FileStr+".log 2> "+baseDir+OutDir+"Non-PBS_Hadrons_"+FileStr+".err\n")

            execFile.writelines(
            "rm -rf "+buildDir+"\n")
            execFile.writelines(
            "rm "+baseDir+"/"+Out1+"\n")

            # Write: change mode
            #execFile.writelines("chmod -R g+r ../../../"+OutDir+"\n")

            # Write: create file 'completed' confirming that the job completed
            execFile.writelines("echo 'Completed!'>"+ baseDir+
                            OutDir+"completed"+FileStr+"\n")

            # Close submission script file
            execFile.close()
            os.chmod(execFileName, stat.S_IRWXG | stat.S_IRWXU)

hadronizeWith("light", "jetscape_hadronize_light.xml")
hadronizeWith("D", "jetscape_hadronize_D.xml")
#hadronizeWith("DB", "jetscape_hadronize_DB.xml")
