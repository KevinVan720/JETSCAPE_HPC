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

'''
This script is for generating the job scripts that uses task farmer to run all the JETSCAPE simulations at all the design points.
All the JETSCAPE jobs will be listed in the tasks_*.txt files. 
And the task farmer (runcommands.sh) will run these .txt files.
'''


def checkAndBuildDir(checkDir):
    if (not os.path.isdir(checkDir)):
        print("Creating directory \""+checkDir+"\" ...")
        os.mkdir(checkDir)


##### Input parameters #####
baseDir = str(pathlib.Path(__file__).parent.absolute())

pThatPair = [1, 2, 3, 4, 5, 7, 9, 11, 13, 15, 17, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230,
             240, 250, 260, 270, 280, 290, 300, 350, 400, 450, 500, 550, 600, 700, 800, 900,  1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2200, 2400, 2510]
pThat_Min = pThatPair[:-1]
pThat_Max = pThatPair[1:]
queueType = "regular"
maxTime = 24  # in hours
repeatRange = range(1, 3)

taskRange=range(0,2)

##### End of input parameters #####

##### Checking that right directories exist and creating them as needed #####

confFileNames = [baseDir+"/tasks_"+str(i)+".txt" for i in taskRange]

confFiles = []

for i in taskRange:
    confFile = open(confFileNames[i], "w")
    confFile.writelines("#!/usr/bin/env bash\n\n")
    confFiles.append(confFile)

subFileNames = [baseDir+"/sub_to_run_"+str(i)+".sl" for i in taskRange]


totalTasks=(repeatRange.stop-repeatRange.start)*50.0*(len(pThatPair)-1)
jobPerTask=math.ceil(totalTasks/(taskRange.stop-taskRange.start))
nodePerTask=math.ceil(jobPerTask/16)+1

for i in taskRange:
    subFile = open(subFileNames[i], "w")
    subFile.writelines(
        '''#!/usr/bin/env bash

#SBATCH -q {queueType}
#SBATCH --constraint=haswell

#SBATCH -N {nodePerTask}
#SBATCH -c 64
#SBATCH --license cscratch1

#SBATCH --job-name=MA
#SBATCH --time {maxTime}:00:00

export THREADS=16

runcommands.sh tasks_{i}.txt'''.format(queueType=queueType, nodePerTask=nodePerTask, maxTime=maxTime, i=i))

##### End of directory checking/creation #####

count=0
for j in range(0,50):

    jobDir=baseDir+"/design_jetscape/main/"+str(j)+"/"
    for m in repeatRange:
        for n in range(len(pThat_Min)):
            
            FileStr = str(pThat_Min[n]).zfill(4)+"_"+str(pThat_Max[n]).zfill(4) + \
            "_ev_"+str(10*(m)).zfill(3)+"k_to_"+str(10*(m+1)).zfill(3)+"k"

            execFileName = jobDir+"SubScripts/sub_"+FileStr
            i=math.floor(count*(taskRange.stop-taskRange.start)/totalTasks)
            confFiles[i].writelines(execFileName+"\n")
            count+=1

