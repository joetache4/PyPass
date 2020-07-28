import os
import pytest

from .context import pypass


@pytest.mark.usefixtures("cleandir")
class TestParser:
	
	def test_master(self, helpers):
		try:
			p = pypass.Parser("password")
			with helpers.replace_stdin(["y", "newpassword"]):
				p.parse("master")
			p.db.key.bkey = None
			p.db.key.fkey = None
			p.db.key.login("newpassword")
		except Exception as e:
			print(e)
			assert 0
		
		with pytest.raises(ValueError):
			p.db.key.bkey = None
			p.db.key.fkey = None
			p.db.key.login("password") # should be wrong by now
	
	def test_add(self, helpers, monkeypatch):
		p = pypass.Parser("password")
		
		clip = helpers.ShellFunc()
		monkeypatch.setattr(pypass.Parser, "_clip_text", clip.call)
		p.parse("add a -g")
		assert clip.called
		assert os.path.isfile("a")
		assert any(f.startswith("a.") for f in os.listdir(".backup"))
		
		monkeypatch.setattr(pypass.Parser, "_clip_text", lambda: pytest.fail("Clipboard disabled"))
		
		with helpers.replace_stdin(["abc"]):
			p.parse("add aa --no-clip")
			assert os.path.isfile("aa")
			assert any(f.startswith("aa.") for f in os.listdir(".backup"))
		
		with helpers.replace_stdin(["abc", "def"]):
			p.parse("add aaa -m --no-clip")
			assert os.path.isfile("aaa")
			assert any(f.startswith("aaa.") for f in os.listdir(".backup"))
			
		with helpers.replace_stdin():
			p.parse("add b/b -g --no-clip")
			assert os.path.isfile("b/b")
			assert any(f.startswith("b.") for f in os.listdir(".backup/b"))
			
			p.parse("add b/bb -g --no-clip")
			assert os.path.isfile("b/bb")
			assert any(f.startswith("bb.") for f in os.listdir(".backup/b"))
			
			with pytest.raises(ValueError):
				p.parse("add b -g --no-clip")
				
			with pytest.raises(ValueError):
				p.parse("add b/b -g --no-clip")
				
			with pytest.raises(ValueError):
				p.parse("add b/b/b -g --no-clip")
				
			with pytest.raises(ValueError):
				p.parse("add .c -g --no-clip")
				
			with pytest.raises(ValueError):
				p.parse("add c. -g --no-clip")
			
			p.parse("add c.com -g --no-clip")
			assert os.path.isfile("c.com")
			assert any(f.startswith("c.com.") for f in os.listdir(".backup"))
			
			p.parse("add ' d d ' -g --no-clip")
			assert os.path.isfile(" d d ")
			assert any(f.startswith(" d d .") for f in os.listdir(".backup"))
	
	def test_mv(self, helpers, monkeypatch):
		p = pypass.Parser("password")
		
		monkeypatch.setattr(pypass.Parser, "_clip_text", lambda: pytest.fail("Clipboard disabled"))
		
		with helpers.replace_stdin():
			p.parse("add a -g --no-clip")
			p.parse("mv a b")
			assert not os.path.isfile("a")
			assert not any(f.startswith("a.") for f in os.listdir(".backup"))
			assert os.path.isfile("b")
			assert any(f.startswith("b.") for f in os.listdir(".backup"))
	
	def test_rm(self):
		pass
	
	def test_ls(self, capsys, helpers):
		p = pypass.Parser("password")
			
		p.parse("ls")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str(["", "Accounts:", ""])
		
		p.parse("add 'new account' -g --no-clip")
		p.parse("ls")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str(["", "Accounts:", "  new account", ""])
		
		p.parse("add aaa -g --no-clip")
		p.parse("ls")
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