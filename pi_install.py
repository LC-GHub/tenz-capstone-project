
from subprocess import STDOUT, check_call
import subprocess
import os


proc = subprocess.Popen('sudo apt-get install python3-pyqt5', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=STDOUT, executable="/bin/bash")
proc.wait()