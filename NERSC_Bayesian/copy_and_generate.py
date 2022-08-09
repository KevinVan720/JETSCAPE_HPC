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

#repeatRange = range(5, 7)

for n in range(50):
    os.system("cp -r generate_exec*.py design_jetscape/main/"+str(n)+"/")


for n in range(50):
    os.chdir("/global/cscratch1/sd/wf39/Simulation/design_jetscape/main/"+str(n)+"/")
    os.system("python3 generate_exec.py")

