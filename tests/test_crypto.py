import os
import pytest

from .context import pypass


@pytest.mark.usefixtures("cleandir")
class TestCrypto:
	
	def test_init(self):
		assert os.listdir() == []
		key = pypass.crypto.MasterKey("pw")
		assert os.listdir() == [".key", ".salt"]
		assert key.bkey is not None
		assert key.fkey is not None
	
	def test_save(self):
		pass
	
	def test_login(self):
		pass
	
	def test_encrypt_decrypt(self):
		key = pypass.crypto.MasterKey("pw")
	
	def test_generate_password(self):
		pass