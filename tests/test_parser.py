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
				p.parse("add b\\b/b -g --no-clip")
				
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
			
			p.parse("mv b a/a")
			assert not os.path.isfile("b")
			assert not any(f.startswith("b.") for f in os.listdir(".backup"))
			assert os.path.isfile("a")
			assert any(f.startswith("a.") for f in os.listdir(".backup/a"))
			
			p.parse("mv a b\\b") # autocompletes a
			assert not os.path.isdir("a")
			assert not os.path.isdir(".backup/a")
			assert os.path.isfile("b/b")
			assert any(f.startswith("b.") for f in os.listdir(".backup/b"))
			
			p.parse("mv b/b a/a/a")
			assert not os.path.isdir("b")
			assert not os.path.isdir(".backup/b")
			assert os.path.isfile("a/a/a")
			assert any(f.startswith("a.") for f in os.listdir(".backup/a/a"))
	
	def test_rm(self):
		p = pypass.Parser("password")
		
		monkeypatch.setattr(pypass.Parser, "_clip_text", lambda: pytest.fail("Clipboard disabled"))
		
		with helpers.replace_stdin(["y"]):
			p.parse("add aa -g --no-clip")
			p.parse("rm a")
			assert not os.path.isfile("aa")
			assert any(f.startswith("aa.") for f in os.listdir(".backup"))
		
		with helpers.replace_stdin():
			p.parse("add aa/a -g --no-clip")
			p.parse("rm a")
			assert not os.path.isdir("aa")
			assert any(f.startswith("a.") for f in os.listdir("aa/.backup"))
	
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
	
	def test_print_account(self, helpers, capsys, monkeypatch):
		pass
	
	def test_edit(self):
		pass
	
	def test_load(self):
		sample = """
cc pin
083

gmail
password123
pinkroses

AOL
pw
user: dudeguy

amazon
pw
dudeguy

laptop
1234

netflix
cat33
dog33@gmail.com

geico
$2011$
pinkroses@aol.com

"""
	
	def test_copy(self, helpers, monkeypatch):
		p = pypass.Parser("master")
		
		with helpers.replace_stdin(["passwd123"]):
			p.parse("add abc --no-clip")
		clip = helpers.ShellFunc()
		monkeypatch.setattr(pypass.Parser, "_clip_text", clip.call)
		p.parse("ab")
		assert clip.called
		assert clip.args[0] == "passwd123"		
		
		with helpers.replace_stdin(["passwd_xyz", "someusername", "otherinfo"]):
			p.parse("add xyz -m --no-clip")
		clip = helpers.ShellFunc()
		monkeypatch.setattr(pypass.Parser, "_clip_text", clip.call)
		p.parse("copy x")
		assert clip.called
		assert clip.args[0] == "passwd_xyz"