import pytest

#from .context import pypass
from pypass.database import Database


@pytest.mark.usefixtures("cleandir")
class TestDatabase:
	
	def test_init(self):
		db = Database(".", "password")