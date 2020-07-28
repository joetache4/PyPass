import pytest

from .context import pypass


@pytest.mark.usefixtures("cleandir")
class TestDatabase:
	
	def test_init(self):
		db = pypass.database.Database("password")