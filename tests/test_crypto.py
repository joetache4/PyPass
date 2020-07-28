import os
import random
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
		with pytest.raises(ValueError):
			pypass.crypto.generate_password(7, False)
		for i in range(10):
			length = random.randint(8, 32)
			symbol = random.choice([True, False])
			passwd = pypass.crypto.generate_password(length, symbol)
			assert len(passwd) == length
			assert any(c in passwd for c in "abcdefghijkmnpqrstuvwxyz")
			assert any(c in passwd for c in "ABCDEFGHJKLMNPQRSTUVWXYZ")
			assert any(c in passwd for c in "23456789")
			if symbol:
				assert any(c in passwd for c in "!@#$%^&*()-+=.,?<>_:{}|*/")