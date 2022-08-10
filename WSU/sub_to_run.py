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

##### generate and submit jobs for running JETSCAPE (not containerized) on a HPC that uses slurm job scheduler.
##### the folder structure should be
##### JETSCAPE jetscape_init.xml sub_to_run.py
##### submitting the jobs by running python3 sub_to_run.py

def checkAndBuildDir(checkDir):
    if (not os.path.isdir(checkDir)):
        print("Creating directory \""+checkDir+"\" ...")
        os.mkdir(checkDir)


##### Input parameters #####
baseDir = str(pathlib.Path(__file__).parent.absolute()) #the current directory
#both final partons and hadrons are stored
extPartType1 = "Partons" 
extPartType2 = "Hadrons"

preCompiled_Raw = "runJetscape"
preCompiled_Par = "FinalStatePartons"
preCompiled_Had = "FinalStateHadrons"

queueType = "regular"
maxTime=12 #in hours
repeatRange = range(0,1)


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

for n in range(len(pThat_Min)):
    for m in repeatRange:

        FileStr = str(pThat_Min[n]).zfill(4)+"_"+str(pThat_Max[n]).zfill(4) + \
            "_ev_"+str(10*(m)).zfill(3)+"k_to_"+str(10*(m+1)).zfill(3)+"k"
        OutDir = "OutputFiles/"

        ## create a new user xml file with the appropriate pThat bins and input/output file names
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

        subFileName = "SubScripts/sub_"+FileStr
        Input = "InputFiles/jetscape_initBin" + \
            str(pThat_Min[n])+"_"+str(pThat_Max[n])+"_"+str(m)+".xml"

        Input_Par = Out1
        Output_Par = OutDir+extPartType1+"_"+FileStr+".dat"

        Input_Had = Out1
        Output_Had = OutDir+extPartType2+"_"+FileStr+".dat"
 
        checkAndBuildDir(buildDir)

        ##### start writing the actual submission script
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
        
        subFile.writelines("time ./"+preCompiled_Par+" ../../../"+Input_Par+" ../../../"+Output_Par+" 1> ../../../" +
                           OutDir+"Non-PBS_Partons_"+FileStr+".log 2> ../../../"+OutDir+"Non-PBS_Partons_"+FileStr+".err\n")
        
        #now we dont save the hadrons at this step
        subFile.writelines("time ./"+preCompiled_Had+" ../../../"+Input_Had+" ../../../"+Output_Had+" 1> ../../../" +
                           OutDir+"Non-PBS_Hadrons_"+FileStr+".log 2> ../../../"+OutDir+"Non-PBS_Hadrons_"+FileStr+".err\n")

        #we store the event information in a separate file for future analysis
        subFile.writelines("cat "+baseDir+"/OutputFiles/"+extPartType2+"_"+FileStr+".dat | grep \"#\" > "+
            baseDir+"/OutputFiles/"+"Headers"+"_"+FileStr+".dat"+"\n")
        
        subFile.writelines(
            "rm -rf "+buildDir+"\n")

        # you may remove the final hadron to save space
        # The hadrons may be recreated as long as we store the final partons
        #subFile.writelines(
        #    "rm "+baseDir+"/"+Out1+"\n")

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

