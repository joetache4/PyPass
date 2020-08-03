import sys
import os
import shutil
import tempfile
from io import StringIO
from contextlib import contextmanager

import pytest


@pytest.fixture(scope = "function")
def cleandir():
	old_cwd = os.getcwd()
	newpath = tempfile.mkdtemp()
	os.chdir(newpath)
	yield
	os.chdir(old_cwd)
	shutil.rmtree(newpath)

@pytest.fixture(scope = "function")
def helpers():
	return Helpers


class Helpers:

	@staticmethod
	@contextmanager
	def replace_stdin(lines = []):
		lines = [(s if s.endswith("\n") else s + "\n") for s in lines]
		lines = StringIO("".join(lines))
		orig = sys.stdin
		sys.stdin = lines
		yield
		sys.stdin = orig

	@staticmethod
	def lines_str(lines):
		return "\n".join(lines) + "\n"
	
	class ShellFunc:
		def __init__(self):
			self.called = False
			self.args = None
		def call(self, *args):
			self.called = True
			self.args = args

'''
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