import sys
import os
import time
import shlex
import argparse
import textwrap
import pyperclip
import logging
from contextlib import contextmanager

from .database import Database


@contextmanager
def _chdir(dir):
	old_dir = os.getcwd()
	os.chdir(dir)
	yield
	os.chdir(old_dir)

class ErrorCatchingArgumentParser(argparse.ArgumentParser):
    def exit(self, status = 0, message = None):
        raise EOFError()

class Parser:
	
	def __init__(self, master = None, dir = "."):
		self.logger = logging.getLogger()
		self.dir = dir
		with _chdir(self.dir):
			self.db = Database(master)
		
		self.parser = ErrorCatchingArgumentParser(
			prog = "pypass",
			#formatter_class = argparse.RawDescriptionHelpFormatter,
			description = "Create, store, and retrieve passwords for multiple accounts.")
		self.parser.add_argument("-y", "--yes", dest = "yes", action = "store_true",
			help = "answer yes to any [y/n] prompts")
		self.parser.add_argument("--no-clip", dest = "clip", action = "store_false",
			help = "do not copy passwords to the clipboard")
		self.parser.add_argument("-t", "--time", dest = "seconds", nargs = 1, default = 20, type = int,
			help = "time, in seconds, to keep the password copied to the clipboard")
		subparsers = self.parser.add_subparsers(dest = "command", title = "subcommands",
			description = "type COMMAND -h to see how to use these subcommands")

		parser_master = subparsers.add_parser("master", help = "change master password")

		parser_ls = subparsers.add_parser("ls", help = "list accounts")
		parser_ls.add_argument("arg", metavar = "filter", nargs = "?", default = "",
			help = "optionally filter account names containing this string")

		parser_load = subparsers.add_parser("load", help = "load accounts from a file")
		parser_load.add_argument("infile", metavar = "file", type = argparse.FileType(),
			help = "file to load (or '-' to read from the console); The file/input should be formatted as such: [ACCOUNT\nPASSWORD\n[MISC\n]*\n]+")

		parser_add = subparsers.add_parser("add", help = "add a new account")
		parser_add.add_argument("arg", metavar = "account_name", # nargs = 1 # saved as a list, causes problems
			help = "name of the new account to add")
		parser_add.add_argument("-g", "--generate", dest = "length", nargs = "?", action = "store",
			default = -1, const = 16, type = int,
			help = "generate password (default: False/16 characters)")
		parser_add.add_argument("-n", "--no-symbols", dest = "symbols", action = "store_false",
			help = "exclude symbols from generated passwords (default: False)")
		parser_add.add_argument("-m", "--multiline", dest = "multiline", action = "store_true",
			help = "ask user for multiple lines of input")
		parser_add.add_argument("--no-clip", dest = "clip", action = "store_false",
			help = "do not copy passwords to the clipboard")
		parser_add.add_argument("-t", "--time", dest = "seconds", nargs = 1, default = 20, type = int,
			help = "time, in seconds, to keep the password copied to the clipboard")

		parser_edit = subparsers.add_parser("edit", help = "edit an existing account")
		parser_edit.add_argument("arg", metavar = "account_name", nargs = "?", default = "",
			help = "name of the account to edit")					
		parser_edit.add_argument("-g", "--generate", dest = "length", nargs = "?", action = "store",
			default = -1, const = 16, type = int,
			help = "generate password (default: False/16 characters)")
		parser_edit.add_argument("-n", "--no-symbols", dest = "symbols", action = "store_false",
			help = "exclude symbols from generated passwords (default: False)")
		parser_edit.add_argument("-m", "--multiline", dest = "multiline", action = "store_true",
			help = "ask user for multiple lines of input")
		parser_edit.add_argument("--no-clip", dest = "clip", action = "store_false",
			help = "do not copy passwords to the clipboard")
		parser_edit.add_argument("-t", "--time", dest = "seconds", nargs = 1, default = 20, type = int,
			help = "time, in seconds, to keep the password copied to the clipboard")

		parser_copy = subparsers.add_parser("copy", help = "copy an account password to the clipboard")
		parser_copy.add_argument("arg", metavar = "account_name", nargs = "?", default = "",
			help = "name of the account to copy")
		parser_copy.add_argument("--no-clip", dest = "clip", action = "store_false",
			help = "do not copy passwords to the clipboard")
		parser_copy.add_argument("-t", "--time", dest = "seconds", nargs = 1, default = 20, type = int,
			help = "time, in seconds, to keep the password copied to the clipboard")

		parser_print = subparsers.add_parser("print", help = "print all account details")
		parser_print.add_argument("arg", metavar = "account_name", nargs = "?", default = "",
			help = "name of the account to print")

		parser_mv = subparsers.add_parser("mv", help = "rename an account")
		parser_mv.add_argument("arg", metavar = "account_name",
			help = "name of the account to rename")
		parser_mv.add_argument("arg2", metavar = "new_account_name",
			help = "new name for the account")

		parser_rm = subparsers.add_parser("rm", help = "delete an account")
		parser_rm.add_argument("arg", metavar = "account_name", nargs = "?", default = "",
			help = "name of the account to delete")
		parser_rm.add_argument("-y", "--yes", dest = "yes", action = "store_true",
			help = "answer yes to any [y/n] prompts")

		parser_help = subparsers.add_parser("help", help = "show this help message and exit")

		parser_master.set_defaults(func = self.master)
		parser_ls.set_defaults(func = self.ls)
		parser_load.set_defaults(func = self.load)
		parser_add.set_defaults(func = self.add)
		parser_edit.set_defaults(func = self.edit)
		parser_copy.set_defaults(func = self.copy)
		parser_print.set_defaults(func = self.print_account)
		parser_mv.set_defaults(func = self.mv)
		parser_rm.set_defaults(func = self.rm)
		parser_help.set_defaults(func = lambda *x: self.parser.print_help())

	def parse(self, args):
		"""
		Parse the command line args and run the appropriate command.
		"""	
		self.logger.debug(f"Parsing args: {args}")
		
		if isinstance(args, str):
			args = args.replace("\\", "\\\\")
			args = shlex.split(args)
		
		args = [a.replace("/", os.sep) for a in args]

		# default subcommand
		if all(s not in args for s in ["master", "ls", "add", "rm", "edit", "mv", "load", "copy", "print", "help"]):
			args.insert(0, "copy")
		
		# -n implies -g
		if "-n" in args and "-g" not in args:
			args.append("-g")

		self.logger.debug(f"Processed args: {args}")

		args = self.parser.parse_args(args)

		if args.func is self.load:
			args.arg = os.path.abspath(args.arg)
		
		lvl = 	logging.WARNING if args.command in ["master", "add", "rm", "edit", "mv", "load"] \
				else logging.INFO if args.command in ["copy", "print"] else logging.DEBUG
		self.logger.log(lvl, f"{vars(args)}")
		
		with _chdir(self.dir):
			args.func(args)


	### Command handlers ##################################################


	def master(self, args):
		"""
		Change the master password.
		"""
		if args.yes or Parser._yesno("Change password for existing pass database?", True):
			self.db.key.login(None, "Current Master Password: ")
			self.db.key.save()

	def ls(self, args):
		"""
		Print list of matching accounts.
		"""
		print()
		accounts = self.db.accounts(args.arg)
		print("Accounts:")
		for a in accounts:
			print(f"  {a}")
		print()

	def load(self, args):
		"""
		Load password data from a file. Conflicts will be ignored. File is expected to have	account info in blocks separated by a single blank line. Each block will have the account name as the first line, followed by the password, and then any additional	information.
		"""
		self.db.key.login()

		# read lines
		lines = args.infile.readlines()
		lines = [line.strip() for line in lines]

		# separate into blocks
		blocks = [[]]
		for line in lines:
			if line == "":
				if blocks[-1] != []:
					blocks.append([])
				else:
					pass
			else:
				blocks[-1].append(line)
		if blocks[-1] == []:
			blocks.pop()
		
		# add
		for block in blocks:
			block[0] = block[0].replace(".", "-")
			block[0] = block[0].replace("/", os.sep)
			try:
				# check if account name is unavailable
				if os.path.isfile(block[0]):
					raise ValueError(f"Error: Account {account} already exists.")
				if os.path.isdir(block[0]):
					raise ValueError(f"Error: {account} is an existing directory.")
				self.db.add_block(block[0], block[1:])
			except ValueError as e:
				self.logger.error(str(e))
				print(e)

	def add(self, args):
		"""
		Add account to the database.
		"""
		self.db.key.login()
		
		account   = args.arg
		generate  = args.length
		multiline = args.multiline
		symbols   = args.symbols

		# check if account name is unavailable
		if os.path.isfile(account):
			raise ValueError(f"Error: Account {account} already exists.")
		if os.path.isdir(account):
			raise ValueError(f"Error: {account} is an existing directory.")
		
		self.db.add_input(account, generate, multiline, symbols)
		if args.clip:
			Parser._clip_text(self.db.content(account)[0], args.seconds)

	def edit(self, args):
		"""
		Edit account details.
		"""
		self.db.key.login()
		
		args.arg  = self.db.select(args.arg)
		
		account   = args.arg
		generate  = args.length
		multiline = args.multiline
		symbols   = args.symbols
		
		old_account = account + ".old"

		os.rename(account, old_account)

		try:
			lines         = self.db.content(old_account)
			multiline    |= len(lines) > 1
			lines         = "\n".join(lines)
			print(lines)
			print()

			self.db.add_input(account, generate, multiline, symbols)
			
		except Exception as e:
			os.rename(old_account, account)
			raise e

		os.remove(old_account)
		
		if args.clip:
			Parser._clip_text(self.db.content(account)[0], args.seconds)

	def copy(self, args):
		"""
		Copy selected account password to clipboard for 30 seconds.
		"""
		self.db.key.login()
		account = self.db.select(args.arg)
		pw = self.db.content(account)[0]
		if args.clip:
			Parser._clip_text(pw, args.seconds)
		else:
			print(pw)

	def print_account(self, args):
		"""
		Print account details.
		"""
		self.db.key.login()
		account = self.db.select(args.arg)
		lines   = self.db.content(account)
		lines   = "\n".join(lines)
		print(lines)

	def mv(self, args):
		"""
		Rename account.
		"""
		account1 = self.db.select(args.arg)
		account2 = args.arg2
		self.db.mv(account1, account2)
		
	def rm(self, args):
		"""
		Delete account.
		"""
		account = self.db.select(args.arg)
		if args.yes or Parser._yesno("Delete?", False):
			self.db.rm(account)


	### Miscellaneous functions ###########################################

	
	@staticmethod
	def _clip_text(text, seconds):
		"""
		Temporarily copy text to clipboard.
		"""
		old_clip = pyperclip.paste()
		pyperclip.copy(text)
		p = lambda s: print(s, end = "", flush = True)
		try:
			for s in range(seconds, 0, -1):
				p("Copied to clipboard [" + "="*s + " "*(seconds-s) + "]")
				try:
					time.sleep(1)
				finally:
					#p("\b" * 52)
					p("\r")
		except KeyboardInterrupt:
			pass
		finally:
			#p(" "*52 + "\b"*52)
			p(" "*52 + "\r")
			pyperclip.copy(old_clip)
	
	@staticmethod
	def _yesno(prompt, default = True):
		"""
		Ask a prompt, expect a yes or no answer.
		"""
		if default:
			ans = input(f"{prompt} [Y/n]")
			return not ans.strip().lower() in ["n", "no"]
		else:
			ans = input(f"{prompt} [y/N]")
			return ans.strip().lower() in ["y", "yes"]