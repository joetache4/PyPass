import pytest

from .context import pypass


@pytest.mark.usefixtures("cleandir")
class TestParser:
	
	def test_master(self, helpers):
		try:
			db = pypass.Database("password")
			with helpers.replace_stdin(["y", "newpassword"]):
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
	
	def test_ls(self, capsys, helpers):
		db = pypass.Database("password")
			
		pypass.parse(db, "ls")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str(["", "Accounts:", ""])
		
		pypass.parse(db, "add 'new account' -g --no-clip")
		pypass.parse(db, "ls")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str(["", "Accounts:", "  new account", ""])
		
		pypass.parse(db, "add aaa -g --no-clip")
		pypass.parse(db, "ls")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str(["", "Accounts:", "  aaa", "  new account", ""])
	
	def test_print_account(self):
		pass
	
	def test_edit(self):
		pass
	
	def test_load(self):
		pass
	
	def test_copy(self):
		pass