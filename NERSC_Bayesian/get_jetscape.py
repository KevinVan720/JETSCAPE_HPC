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

for n in range(10):
    os.system("cp -r JETSCAPE design_jetscape/final/"+str(n)+"/")
    os.system("cp -r jetscape_*.xml design_jetscape/final/"+str(n)+"/")
