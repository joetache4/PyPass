import sys
import os
import time
import shlex
import argparse
import textwrap
import pyperclip


parser = argparse.ArgumentParser(
	prog = 'pypass',
	formatter_class = argparse.RawDescriptionHelpFormatter,
	description = 'Create, store, and retrieve passwords for multiple accounts.',
	epilog = textwrap.dedent('''
	commands:
	  master	
	  ls	 [ACCOUNT]
	  load	  FILE
	  add	 [ACCOUNT]
	  edit	 [ACCOUNT]
	  copy	 [ACCOUNT]
	  print	 [ACCOUNT]
	  mv	  ACCOUNT_FROM ACCOUNT_TO
	  rm	 [ACCOUNT]
	'''))
parser.add_argument('command', metavar = 'command', nargs = '?', default = 'copy',
					help = 'command to perform')
parser.add_argument('arg', metavar = 'arg', nargs = '?', default = '',
					help = 'command argument (usually an account name)')
parser.add_argument('arg2', metavar = 'arg2', nargs = '?', default = '',
					help = '2nd argument for the mv command')
parser.add_argument('-g', '--generate', dest = 'length', nargs = '?', action = 'store',
					default = -1, const = 16, type = int,
					help = 'generate password (default: False/16 characters)')
parser.add_argument('-n', '--no-symbols', dest = 'symbols', action = 'store_false',
					help = 'exclude symbols from generated passwords (default: False)')
parser.add_argument('-m', '--multiline', dest = 'multiline', action = 'store_true',
					help = 'ask user for multiple lines of input')
parser.add_argument('-y', '--yes', dest = 'yes', action = 'store_true',
					help = 'answer yes to any [y/n] prompts')
parser.add_argument('--no-clip', dest = 'clip', action = 'store_false',
					help = 'do not copy passwords to the clipboard')
parser.add_argument('-t', '--time', dest = 'seconds', nargs = 1, default = 20,
					help = 'time, in seconds, to keep the password copied to the clipboard')

def parse(db, args):
	"""
	Parse the command line args and run the appropriate command.
	"""
	run = {
		"master": lambda db, args: master       (db, args),
		"ls"    : lambda db, args: ls           (db, args),
		"copy"  : lambda db, args: copy         (db, args),
		"add"   : lambda db, args: add          (db, args),
		"rm"    : lambda db, args: rm           (db, args),
		"edit"  : lambda db, args: edit         (db, args),
		"mv"    : lambda db, args: mv           (db, args),
		"print" : lambda db, args: print_account(db, args),
		"load"  : lambda db, args: load         (db, args),
		"help"  : lambda db, args: parser.print_help()
	}
	
	if isinstance(args, str):
		args = args.replace("\\", "\\\\")
		args = shlex.split(args)
	
	args = [a.replace("/", os.sep) for a in args]

	# -n implies -g
	if "-n" in args and "-g" not in args:
		args.append("-g")

	args = parser.parse_args(args)
	
	try:
		if args.command not in run.keys():
			if args.arg:
				raise ValueError("Error: Could not parse arguments.")
			args.command, args.arg = "copy", args.command
		
		run[args.command](db, args)
	except KeyboardInterrupt:
		print() # do nothing else
	except ValueError as e:
		print(e)
		return False
	return True


### Command handlers ##################################################


def master(db, args):
	"""
	Change the master password.
	"""
	if args.yes or yesno("Change password for existing pass database?", True):
		db.key.login(None, "Current Master Password: ")
		db.key.save()

def ls(db, args):
	"""
	Print list of matching accounts.
	"""
	print()
	accounts = db.accounts(args.arg)
	print("Accounts:")
	for a in accounts:
		print(f"  {a}")
	print()

def load(db, args):
	"""
	Load password data from a file. Conflicts will be ignored. File is expected to have	account info in blocks separated by a single blank line. Each block will have the account name as the first line, followed by the password, and then any additional	information.
	"""
	db.key.login()
	# get input file path
	fname = args.arg
	if not os.path.isabs(fname):
		fname = os.path.join("..", fname) # TODO this seems janky

	# read lines
	lines = []
	with open(fname, "r") as f:
		line = f.readline()
		while line:
			lines.append(line.strip("\n"))
			line = f.readline()

	# separate into blocks
	blocks = [[]]
	for line in lines:
		if line == "" and blocks[-1] != []:
			blocks.append([])
		else:
			blocks[-1].append(line)
	if blocks[-1] == []:
		blocks.pop()

	# add
	for block in blocks:
		block[0] = block[0].replace(".", "-")
		try:
			# check if account name is unavailable
			if os.path.isfile(block[0]):
				raise ValueError(f"Error: Account {account} already exists.")
			if os.path.isdir(block[0]):
				raise ValueError(f"Error: {account} is an existing directory.")
			db.add_block(block[0], block[1:], db)
		except ValueError as e:
			print(e)

def add(db, args):
	"""
	Add account to the database.
	"""
	db.key.login()
	
	account   = args.arg
	generate  = args.length
	multiline = args.multiline
	symbols   = args.symbols

	# check if account name is unavailable
	if os.path.isfile(account):
		raise ValueError(f"Error: Account {account} already exists.")
	if os.path.isdir(account):
		raise ValueError(f"Error: {account} is an existing directory.")
	
	db.add_input(account, generate, multiline, symbols)
	if args.clip:
		clip_text(db.content(account)[0], args.seconds)

def edit(db, args):
	"""
	Edit account details.
	"""
	db.key.login()
	
	args.arg  = db.select(args.arg)
	
	account   = args.arg
	generate  = args.length
	multiline = args.multiline
	symbols   = args.symbols
	
	old_account = account + ".old"

	os.rename(account, old_account)

	try:
		lines         = db.content(old_account, db)
		multiline    |= len(lines) > 1
		lines         = "\n".join(lines)
		print(lines)
		print()

		db.add_input(account, generate, multiline, symbols)
		
	except Exception as e:
		os.rename(old_account, account)
		raise e

	os.remove(old_account)
	
	if args.clip:
		clip_text(db.content(account)[0], args.seconds)

def copy(db, args):
	"""
	Copy selected account password to clipboard for 30 seconds.
	"""
	db.key.login()
	account = db.select(args.arg)
	if args.clip:
		clip_text(db.content(account)[0], args.seconds)

def print_account(db, args):
	"""
	Print account details.
	"""
	db.key.login()
	account = db.select(args.arg)
	lines   = db.content(account)
	lines   = "\n".join(lines)
	print(lines)

def mv(db, args):
	"""
	Rename account.
	"""
	account1 = db.select(args.arg)
	account2 = args.arg2
	db.mv(account1, account2)
	
def rm(db, args):
	"""
	Delete account.
	"""
	account = db.select(args.arg)
	if args.yes or yesno("Delete?", False):
		db.rm(account)


### Miscellaneous functions ###########################################


def clip_text(text, seconds):
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

def yesno(prompt, default = True):
	"""
	Ask a prompt, expect a yes or no answer.
	"""
	if default:
		ans = input(f"{prompt} [Y/n]")
		return not ans.strip().lower() in ["n", "no"]
	else:
		ans = input(f"{prompt} [y/N]")
		return ans.strip().lower() in ["y", "yes"]