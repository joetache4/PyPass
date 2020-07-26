import os
import shutil
import tempfile

import pytest

#from .context import pypass

@pytest.fixture(scope="function")
def cleandir():
	old_cwd = os.getcwd()
	newpath = tempfile.mkdtemp()
	os.chdir(newpath)
	yield
	os.chdir(old_cwd)
	shutil.rmtree(newpath)

#@pytest.fixture(scope="function")
#def newdb(cleandir):
#	pypass.crypto.MasterKey(".key", ".salt", " pass word ")
#	yield