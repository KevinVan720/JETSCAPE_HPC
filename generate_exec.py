import os
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
baseDir = str(pathlib.Path(__file__).parent.absolute())
extPartType1 = "Partons"
extPartType2 = "Hadrons"

preCompiled_Raw = "runJetscape"
preCompiled_Par = "FinalStatePartons"
preCompiled_Had = "FinalStateHadrons"

queueType = "regular"
maxTime = 12  # in hours
repeatRange = range(1, 2)

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

confFileName = "run.conf"
confFile = open(confFileName, "w")


##### End of directory checking/creation #####

for n in range(len(pThat_Min)):
    for m in repeatRange:

        FileStr = str(pThat_Min[n]).zfill(4)+"_"+str(pThat_Max[n]).zfill(4) + \
            "_ev_"+str(10*(m)).zfill(3)+"k_to_"+str(10*(m+1)).zfill(3)+"k"
        OutDir = "OutputFiles/"

        inputfileName = baseDir+"/InputFiles/jetscape_initBin" + \
            str(pThat_Min[n])+"_"+str(pThat_Max[n])+"_"+str(m)+".xml"
        os.system("cp "+baseDir+"/jetscape_init.xml " + inputfileName)
        for line in fileinput.input([inputfileName], inplace=True):
            if 'pTHatMin' in line:
                line = '      <pTHatMin>'+str(pThat_Min[n])+'</pTHatMin>\n'

            if 'pTHatMax' in line:
                line = '      <pTHatMax>'+str(pThat_Max[n])+'</pTHatMax>\n'

            if 'outputFilename' in line:
                line = '<outputFilename>'+baseDir+"/"+OutDir+FileStr+'</outputFilename>\n'
            sys.stdout.write(line)

        Out1 = OutDir+FileStr+".dat"

        buildDir = "builds/build_"+FileStr
        buildDir = os.path.join(baseDir, buildDir)
        checkAndBuildDir(buildDir)

        execFileName = "SubScripts/sub_"+FileStr
        Input = "InputFiles/jetscape_initBin" + \
            str(pThat_Min[n])+"_"+str(pThat_Max[n])+"_"+str(m)+".xml"

        Input_Par = Out1
        Output_Par = OutDir+extPartType1+"_"+FileStr+".dat"

        Input_Had = Out1
        Output_Had = OutDir+extPartType2+"_"+FileStr+".dat"

        if (os.path.exists(Output_Had)):
            continue

        confFile.writelines(str(m*len(pThat_Min)+n)+" "+baseDir+"/"+execFileName+"\n")

        execFile = open(execFileName, "w")

        #Write: Header
        execFile.writelines("#!/usr/bin/env bash\n")
#        execFile.writelines("#SBATCH -q "+queueType+"\n")

#        execFile.writelines("#SBATCH --constraint=knl\n")
#        execFile.writelines("#SBATCH --mem=4GB\n")
#        execFile.writelines("#SBATCH -N 1\n")
#        execFile.writelines("#SBATCH -c 1\n")
#        execFile.writelines("#SBATCH -n 1\n")

#        execFile.writelines("#SBATCH --cpus-per-task 1")
#        execFile.writelines("#SBATCH --license cscratch1")

#        execFile.writelines("#SBATCH --job-name=MA_" +
#                           str(pThat_Min[n]).zfill(4)+"_"+str(pThat_Max[n]).zfill(4)+"\n")
#        execFile.writelines("#SBATCH -e "+OutDir+"MA_"+FileStr+".err\n")
#        execFile.writelines("#SBATCH -o "+OutDir+"MA_"+FileStr+".log\n")
#        execFile.writelines("#SBATCH --time "+str(maxTime)+":00:00\n")

        execFile.writelines("mkdir " +
                            buildDir + "/build" + "\n")
        execFile.writelines("cd " + baseDir + "\n")
        execFile.writelines("cp -rf JETSCAPE/* " +
                            buildDir + "\n")

        # Write: Go to directory
        #execFile.writelines("module unload root\n")
        execFile.writelines("cd " + buildDir + "/build" "\n")
        execFile.writelines("cmake ..\n")
        execFile.writelines("make\n")

        #Write: Run

        execFile.writelines("time ./"+preCompiled_Raw+" ../../../"+Input +
                            " 1> ../../../"+OutDir+"Non-PBS_"+FileStr+".log 2> ../../../"+OutDir+"Non-PBS_"+FileStr+".err\n")

        execFile.writelines("time ./"+preCompiled_Par+" ../../../"+Input_Par+" ../../../"+Output_Par+" 1> ../../../" +
                            OutDir+"Non-PBS_Partons_"+FileStr+".log 2> ../../../"+OutDir+"Non-PBS_Partons_"+FileStr+".err\n")

        execFile.writelines("time ./"+preCompiled_Had+" ../../../"+Input_Had+" ../../../"+Output_Had+" 1> ../../../" +
                            OutDir+"Non-PBS_Hadrons_"+FileStr+".log 2> ../../../"+OutDir+"Non-PBS_Hadrons_"+FileStr+".err\n")

        execFile.writelines(
            "rm -rf "+buildDir+"\n")
        execFile.writelines(
            "rm "+baseDir+"/"+Out1+"\n")

        # Write: change mode
        execFile.writelines("chmod -R g+r ../../../"+OutDir+"\n")

        # Write: create file 'completed' confirming that the job completed
        execFile.writelines("echo 'Completed!'>../../../" +
                            OutDir+"completed"+FileStr+"\n")

        # Close submission script file
        execFile.close()
