import os
import pytest

from pypass.database import Database
from pypass.parser import Parser


@pytest.fixture(scope = "function")
def parser():
	db = Database(".", "password")
	return Parser(db)

@pytest.mark.usefixtures("cleandir")
class TestParser:
	
	def test_master(self, helpers, parser):
		try:			
			with helpers.replace_stdin(["y", "newpassword"]):
				parser.parse("master")
			parser.db.key.bkey = None
			parser.db.key.fkey = None
			parser.db.key.login("newpassword")
		except Exception as e:
			print(e)
			assert 0
		
		with pytest.raises(ValueError):
			parser.db.key.bkey = None
			parser.db.key.fkey = None
			parser.db.key.login("password") # should be wrong by now
	
	def test_add(self, helpers, monkeypatch, parser):		
		clip = helpers.ShellFunc()
		monkeypatch.setattr(Parser, "_clip_text", clip.call)
		parser.parse("add a -g")
		assert clip.called
		assert os.path.isfile("a")
		assert any(f.startswith("a.") for f in os.listdir(".backup"))
		
		monkeypatch.setattr(Parser, "_clip_text", lambda: pytest.fail("Clipboard disabled"))
		
		with helpers.replace_stdin(["abc"]):
			parser.parse("add aa --no-clip")
			assert os.path.isfile("aa")
			assert any(f.startswith("aa.") for f in os.listdir(".backup"))
		
		with helpers.replace_stdin(["abc", "def"]):
			parser.parse("add aaa -m --no-clip")
			assert os.path.isfile("aaa")
			assert any(f.startswith("aaa.") for f in os.listdir(".backup"))
			
		with helpers.replace_stdin():
			parser.parse("add b/b -g --no-clip")
			assert os.path.isfile("b/b")
			assert any(f.startswith("b.") for f in os.listdir(".backup/b"))
			
			parser.parse("add b/bb -g --no-clip")
			assert os.path.isfile("b/bb")
			assert any(f.startswith("bb.") for f in os.listdir(".backup/b"))
			
			with pytest.raises(ValueError):
				parser.parse("add b -g --no-clip")
				
			with pytest.raises(ValueError):
				parser.parse("add b/b -g --no-clip")
				
			with pytest.raises(ValueError):
				parser.parse("add b\\b/b -g --no-clip")
				
			with pytest.raises(ValueError):
				parser.parse("add .c -g --no-clip")
				
			with pytest.raises(ValueError):
				parser.parse("add c. -g --no-clip")
			
			parser.parse("add c.com -g --no-clip")
			assert os.path.isfile("c.com")
			assert any(f.startswith("c.com.") for f in os.listdir(".backup"))
			
			parser.parse("add ' d d ' -g --no-clip")
			assert os.path.isfile(" d d ")
			assert any(f.startswith(" d d .") for f in os.listdir(".backup"))
	
	def test_mv(self, helpers, monkeypatch, parser):		
		monkeypatch.setattr(Parser, "_clip_text", lambda: pytest.fail("Clipboard disabled"))
		
		with helpers.replace_stdin():
			parser.parse("add a -g --no-clip")
			parser.parse("mv a b")
			assert not os.path.isfile("a")
			assert not any(f.startswith("a.") for f in os.listdir(".backup"))
			assert os.path.isfile("b")
			assert any(f.startswith("b.") for f in os.listdir(".backup"))
			
			parser.parse("mv b a/a")
			assert not os.path.isfile("b")
			assert not any(f.startswith("b.") for f in os.listdir(".backup"))
			assert os.path.isfile("a/a")
			assert any(f.startswith("a.") for f in os.listdir(".backup/a"))
			
			parser.parse("mv a b\\b") # autocompletes a
			assert not os.path.isdir("a")
			assert not os.path.isdir(".backup/a")
			assert os.path.isfile("b/b")
			assert any(f.startswith("b.") for f in os.listdir(".backup/b"))
			
			parser.parse("mv b/b a/a/a")
			assert not os.path.isdir("b")
			assert not os.path.isdir(".backup/b")
			assert os.path.isfile("a/a/a")
			assert any(f.startswith("a.") for f in os.listdir(".backup/a/a"))
	
	def test_rm(self, helpers, monkeypatch, parser):		
		monkeypatch.setattr(Parser, "_clip_text", lambda: pytest.fail("Clipboard disabled"))
		
		with helpers.replace_stdin(["y"]):
			parser.parse("add aa -g --no-clip")
			parser.parse("rm a")
			assert not os.path.isfile("aa")
			assert any(f.startswith("aa.") for f in os.listdir(".backup"))
		
		with helpers.replace_stdin():
			parser.parse("add aa/a -g --no-clip")
			parser.parse("rm a -y")
			assert not os.path.isdir("aa")
			assert any(f.startswith("a.") for f in os.listdir(".backup/aa"))
	
	def test_ls(self, capsys, helpers, parser):			
		parser.parse("ls")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str(["", "Accounts:", ""])
		
		parser.parse("add 'new account' -g --no-clip")
		parser.parse("ls")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str(["", "Accounts:", "  new account", ""])
		
		parser.parse("add aaa -g --no-clip")
		parser.parse("ls")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str(["", "Accounts:", "  aaa", "  new account", ""])
	
	def test_print_account(self, helpers, capsys, monkeypatch, parser):		
		monkeypatch.setattr(Parser, "_clip_text", lambda: pytest.fail("Clipboard disabled"))
		
		with helpers.replace_stdin(["abc", "def"]):
			parser.parse("add aa -m --no-clip")
		
		with helpers.replace_stdin():
			capsys.readouterr()
			parser.parse("print")
			captured = capsys.readouterr()
			assert captured.out == helpers.lines_str([">>>>>>> aa", "abc", "def"])
			parser.parse("print a")
			captured = capsys.readouterr()
			assert captured.out == helpers.lines_str([">>>>>>> aa", "abc", "def"])
			parser.parse("print aa")
			captured = capsys.readouterr()
			assert captured.out == helpers.lines_str([">>>>>>> aa", "abc", "def"])
		
			with pytest.raises(ValueError):
				parser.parse("print aaa")
	
	def test_edit(self, helpers, capsys, monkeypatch, parser):		
		monkeypatch.setattr(Parser, "_clip_text", lambda: pytest.fail("Clipboard disabled"))
		
		with helpers.replace_stdin(["abc", "def"]):
			parser.parse("add aa -m --no-clip")
		
		with helpers.replace_stdin(["xyz", "123"]):
			parser.parse("edit aa --no-clip")
			capsys.readouterr()
			parser.parse("print aa")
			captured = capsys.readouterr()
			assert captured.out == helpers.lines_str([">>>>>>> aa", "xyz", "123"])
		
		with helpers.replace_stdin(["jkl"]):
			parser.parse("edit aa -m --no-clip")
			capsys.readouterr()
			parser.parse("print aa")
			captured = capsys.readouterr()
			assert captured.out == helpers.lines_str([">>>>>>> aa", "jkl"])
		
		with helpers.replace_stdin(["xyz", "123"]):
			parser.parse("edit aa --no-clip")
			capsys.readouterr()
			parser.parse("print aa")
			captured = capsys.readouterr()
			assert captured.out == helpers.lines_str([">>>>>>> aa", "xyz"])
	
	def test_load(self, helpers, capsys, monkeypatch, parser):		
		monkeypatch.setattr(Parser, "_clip_text", lambda: pytest.fail("Clipboard disabled"))
		
		sample = """
cc pin
083

gmail
password123
pinkroses

AOL
pw
user: dudeguy

shopping/amazon
pw

laptop
1234

netflix
cat33
dog33@gmail.com

geico
$2011$
pr@aol.com
more
even more

"""
		with open("a", "a") as f:
			f.write(sample)
		acc_all = sorted(("cc pin", "gmail", "AOL", f"shopping{os.sep}amazon", "laptop", "netflix", "geico"))
		acc_all = ["  " + a for a in acc_all]
		acc = sorted(("cc pin", "gmail", "AOL", f"shopping{os.sep}", "laptop", "netflix", "geico"))
		acc = ["  " + a for a in acc]
		
		parser.parse("load a")
		
		parser.parse("ls -a")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str(["", "Accounts:", *acc_all, ""])
		
		parser.parse("ls")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str(["", "Accounts:", *acc, ""])
		
		parser.parse("print ama")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str([f">>>>>>> shopping{os.sep}amazon", "pw"])
		
		parser.parse("print 'cc pin'")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str([">>>>>>> cc pin", "083"])
		
		parser.parse("print geico")
		captured = capsys.readouterr()
		assert captured.out == helpers.lines_str([">>>>>>> geico", "$2011$", "pr@aol.com", "more", "even more"])
	
	def test_copy(self, helpers, monkeypatch, parser):		
		with helpers.replace_stdin(["passwd123"]):
			parser.parse("add abc --no-clip")
		clip = helpers.ShellFunc()
		monkeypatch.setattr(Parser, "_clip_text", clip.call)
		parser.parse("ab")
		assert clip.called
		assert clip.args[0] == "passwd123"		
		
		with helpers.replace_stdin(["passwd_xyz", "someusername", "otherinfo"]):
			parser.parse("add xyz -m --no-clip")
		clip = helpers.ShellFunc()
		monkeypatch.setattr(Parser, "_clip_text", clip.call)
		parser.parse("copy x")
		assert clip.called
		assert clip.args[0] == "passwd_xyz"