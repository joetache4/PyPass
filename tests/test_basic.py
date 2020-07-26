# test with pytest

import sys
import os
from io import StringIO
from contextlib import contextmanager

import pytest

from .context import pypass


@contextmanager
def replace_stdin(target):
	target = [(s if s.endswith("\n") else s + "\n") for s in target]
	target = StringIO("".join(target))
	orig = sys.stdin
	sys.stdin = target
	yield
	sys.stdin = orig

def test_replace_stdin():
	with replace_stdin(["", "abc", "123", "", "", "xyz", ""]):
		assert input() == ""
		assert input() == "abc"
		assert input() == "123"
		assert input() == ""
		assert input() == ""
		assert input() == "xyz"
		assert input() == ""

'''
@pytest.fixture(scope="function")
def db(cleandir):
	yield pypass.database.Database(" pass word ")
'''

def newdb():
	return pypass.database.Database(" pass word ")

lines_str = lambda lines: "".join(x + "\n" for x in lines)


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
	
	def test_encrypt(self):
		pass
	
	def test_decrypt(self):
		pass
	
	def test_generate_password(self):
		pass

@pytest.mark.usefixtures("cleandir")
class TestDatabase:
	
	def test_init(self):
		db = newdb()

@pytest.mark.usefixtures("cleandir")
class TestParser:
	
	def test_master(self):
		try:
			db = newdb()
			with replace_stdin(["y", "newpassword"]):
				pypass.parse(db, "master")
			db.key.bkey = None
			db.key.fkey = None
			db.login("newpassword")
		except Exception as e:
			print(e)
			assert 0
		
		with pytest.raises(ValueError):
			db.key.bkey = None
			db.key.fkey = None
			db.login(" wrong password ")
	
	def test_add(self):
		pass
	
	def test_mv(self):
		pass
	
	def test_rm(self):
		pass
	
	def test_ls(self, capsys):
		db = newdb()
			
		pypass.parse(db, "ls")
		captured = capsys.readouterr()
		assert captured.out == lines_str(["", "Accounts:", ""])
		
		pypass.parse(db, "add 'new account' -g --no-clip")
		pypass.parse(db, "ls")
		captured = capsys.readouterr()
		assert captured.out == lines_str(["", "Accounts:", "  new account", ""])
		
		pypass.parse(db, "add aaa -g --no-clip")
		pypass.parse(db, "ls")
		captured = capsys.readouterr()
		assert captured.out == lines_str(["", "Accounts:", "  aaa", "  new account", ""])
	
	def test_print_account(self):
		pass
	
	def test_edit(self):
		pass
	
	def test_load(self):
		pass
	
	def test_copy(self):
		pass