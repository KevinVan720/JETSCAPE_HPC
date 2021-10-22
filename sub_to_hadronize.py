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

queueType = "secondary"
maxTime = 5  # in hours
repeatRange = range(0, 50)

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

##### End of directory checking/creation #####


def hadronizeWith(outputFolder, fileName,linesToRead=None):
    checkAndBuildDir(os.path.join(baseDir, "OutputFiles/"+outputFolder))
    for n in range(len(pThat_Min)):
        for m in repeatRange:

            FileStr = str(pThat_Min[n]).zfill(4)+"_"+str(pThat_Max[n]).zfill(4) + \
                "_ev_"+str(10*(m)).zfill(3)+"k_to_"+str(10*(m+1)).zfill(3)+"k"
            OutDir = "OutputFiles/"+outputFolder+"/"

            inputfileName = baseDir+"/InputFiles/jetscape_hadronize_"+outputFolder+"_Bin" + \
                str(pThat_Min[n])+"_"+str(pThat_Max[n])+"_"+str(m)+".xml"
            os.system("cp "+baseDir+"/"+fileName+" " + inputfileName)

            inEnergy = False
            for line in fileinput.input([inputfileName], inplace=True):
                if 'outputFilename' in line:
                    line = '<outputFilename>'+baseDir+"/"+OutDir+FileStr+'</outputFilename>\n'

                if "<ELoss>" in line:
                    inEnergy = True
                    Input_Par = "OutputFiles/"+extPartType1+"_"+FileStr+".dat"
                    line = '      <inputName>'+baseDir+"/"+Input_Par+'</inputName>\n'
                    chunk='''
                    <Eloss>
                     <deltaT>0.1</deltaT>
                     <formTime> -0.1</formTime>
                     <maxT>0.0</maxT>
                     <mutex>ON</mutex>

                     <CustomModulePartonReader>
                     <name> CustomModulePartonReader </name>'''\
                    +line\
                    +'''</CustomModulePartonReader>
                    </Eloss>

                    <!-- Jet Hadronization Module -->
                    <JetHadronization>
                    <name>colorless</name>
                    <take_recoil>1</take_recoil>
                    <eCMforHadronization>2510</eCMforHadronization>'''
                    if linesToRead!=None:
                        chunk+=   '''<LinesToRead>'''+\
                        linesToRead+\
                        '''</LinesToRead>'''
                    sys.stdout.write(chunk)

                if " </JetHadronization>" in line:
                    inEnergy = False

                if 'inputName' in line:
                    Input_Par = "OutputFiles/"+extPartType1+"_"+FileStr+".dat"
                    line = '      <inputName>'+baseDir+"/"+Input_Par+'</inputName>\n'

                if not inEnergy:
                    sys.stdout.write(line)

            buildDir = "builds/build_"+FileStr
            buildDir = os.path.join(baseDir, buildDir)
            # checkAndBuildDir(buildDir)

            subFileName = "SubScripts/sub_"+outputFolder+FileStr
            Input = "/InputFiles/jetscape_hadronize_"+outputFolder+"_Bin" + \
                str(pThat_Min[n])+"_"+str(pThat_Max[n])+"_"+str(m)+".xml"

            Input_Had = OutDir+FileStr+".dat"
            Output_Had = OutDir+extPartType2+"_"+FileStr+".dat"

            if (os.path.exists(Output_Had)):
                print("found output had")
                if(os.path.exists(buildDir)):
                    print("found a build directory...re-building")
                    os.system("rm -rf "+buildDir+"/*")
                    os.system("rm "+subFileName)
                else:
                    print("continue")
                    continue

            checkAndBuildDir(buildDir)

            subFile = open(subFileName, "w")

            #Write: Header
            subFile.writelines("#!/usr/bin/env bash\n")
            subFile.writelines("#SBATCH -q "+queueType+"\n")

            subFile.writelines("#SBATCH --constraint=intel\n")
            subFile.writelines("#SBATCH --mem=4GB\n")
            subFile.writelines("#SBATCH -N 1\n")
            subFile.writelines("#SBATCH -n 1\n")

            subFile.writelines("#SBATCH --job-name=MA_" +
                               str(pThat_Min[n]).zfill(4)+"_"+str(pThat_Max[n]).zfill(4)+"\n")
            subFile.writelines("#SBATCH -e "+OutDir+"MA_"+FileStr+".err\n")
            subFile.writelines("#SBATCH -o "+OutDir+"MA_"+FileStr+".log\n")
            subFile.writelines("#SBATCH --time "+str(maxTime)+":00:00\n")

            subFile.writelines("mkdir " +
                               buildDir + "/build" + "\n")
            subFile.writelines("cd " + baseDir + "\n")
            subFile.writelines("cp -rf JETSCAPE/* " +
                               buildDir + "\n")

            # Write: Go to directory
            subFile.writelines("module unload root\n")
            subFile.writelines("cd " + buildDir + "/build" "\n")
            subFile.writelines("cmake ..\n")
            subFile.writelines("make\n")

            #Write: Run

            subFile.writelines("time ./"+preCompiled_Raw+" ../../../"+Input +
                               " 1> ../../../"+OutDir+"Non-PBS_"+FileStr+".log 2> ../../../"+OutDir+"Non-PBS_"+FileStr+".err\n")

            subFile.writelines("time ./"+preCompiled_Had+" ../../../"+Input_Had+" ../../../"+Output_Had+" 1> ../../../" +
                               OutDir+"Non-PBS_Hadrons_"+FileStr+".log 2> ../../../"+OutDir+"Non-PBS_Hadrons_"+FileStr+".err\n")

            subFile.writelines(
                "rm -rf "+buildDir+"\n")
            subFile.writelines(
                "rm "+baseDir+"/"+Input_Had+"\n")

            # Write: change mode
            subFile.writelines("chmod -R g+r ../../../"+OutDir+"\n")

            # Write: create file 'completed' confirming that the job completed
            subFile.writelines("echo 'Completed!'>../../../" +
                               OutDir+"completed"+FileStr+"\n")

            # Close submission script file
            subFile.close()

            # Now, submit file
            os.system("cd " + baseDir + " && sbatch " +
                      subFileName + " > " + subFileName + ".out")

            print("submitted job "+subFileName)
            # ...and wait a few seconds, so as not to overwhelm the scheduler
            time.sleep(0.7)


hadronizeWith("light", "jetscape_init.xml")
