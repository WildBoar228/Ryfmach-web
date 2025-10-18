import sys, os
cwd = os.getcwd()
sys.path.append(cwd)
#sys.path.append(cwd + '/mysite')
from main import app as application