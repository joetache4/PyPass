import os
import time
import shutil
import logging

from .crypto import MasterKey, generate_password


class Database:
	
	def __init__(self, dir = ".", master = None):
		self.logger = logging.getLogger()
		self.dir = dir
		
		old_dir = os.getcwd()
		os.chdir(dir)
		try:
			os.mkdir(".backup")
		except OSError:
			pass # exists
		
		self.key = MasterKey(master)
		
		self.all = set()
		for dirpath, dirnames, filenames in os.walk("."):
			for name in filenames:
				if not name.startswith("."):
					path = os.path.join(dirpath, name)
					self.all.add(os.path.relpath(path, "."))
		
		os.chdir(old_dir)

	def accounts(self, filter = ""):
		matched = []
		for account in self.all:
			if account.startswith(".") and not filter.startswith("."):
				continue
			if filter in account:
				matched.append(account)
		return sorted(matched)

	def select(self, filter = ""):
		"""
		Select an account that (at least partially) matches the filter.
		"""
		matched = self.accounts(filter)
		if len(matched) == 0:
			# no matches
			raise ValueError("Error: No matching account.")
		elif len(matched) == 1:
			# print and return the one matching account
			print(f">>>>>>> {matched[0]}")
			return matched[0]
		else:
			return Database.reduce_selection(matched)
	
	@staticmethod
	def reduce_selection(matched):
		# enumerate and print matched
		width = len(str(len(matched)))
		for i, account in enumerate(matched):
			i = str(i).rjust(width, ' ')
			print(f"{i}. {account}")
		# ask for selection
		while True:
			i = input("select> ")
			if i == "":
				raise EOFError()
			try:
				i = int(i)
				# int input
				return matched[i]
			except ValueError:
				# char input
				new_matched = [m for m in matched if i in m]
				if len(new_matched) == 1:
					return new_matched[0]
				elif len(new_matched) > 1:
					return reduce_selection(new_matched)
			except IndexError:
				pass

	def add_input(self, account, generate, multiline, symbols):
		"""
		Ask for input then call add_block().
		"""				
		lines = []
		
		# generate pw if requested
		if generate > 0:
			lines.insert(0, generate_password(generate, symbols))

		# ask user for password
		if lines == []:
			lines.append(input(f"{account}> "))

		# ask user for multiline input
		if multiline:
			try:
				while True:
					line = input(f"{account}> ")
					if line:
						lines.append(line)
					else:
						break
			except EOFError:
				pass
		
		self.add_block(account, lines)

	def add_block(self, account, lines):
		"""
		Add lines to account file, overwriting existing content.
		"""	
		if account[0] == '.' or account[-1] == '.':
			raise ValueError("Error: Account name can't start or end with a '.' character.")

		# validate lines
		lines = [a.strip() for a in lines]
		lines = [a for a in lines if a != ""]
		if len(lines) == 0:
			raise ValueError(f"Error: Blank password for account {account}.")
		if " " in lines[0]:
			raise ValueError(f"Error: Password cannot contain spaces.")

		# encrypt lines
		pw = lines[0]
		lines = [self.key.encrypt(a) for a in lines]

		# filesystem changes
		Database._make_parent_dirs(account)
		try:
			with open(account, "w") as f:
				for line in lines:
					f.write(line + "\n")
		except FileNotFoundError:
			raise ValueError(f"Error: Could not create account: {account}")
		self.all.add(account)
		self.backup(account)

	def content(self, account):
		"""
		Return the decrypted file contents.
		"""
		lines = []
		with open(account) as f:
			line = f.readline()
			while line:
				lines.append(self.key.decrypt(line))
				line = f.readline()
		return lines
	
	def rm(self, account):
		os.remove(account)
		Database._rm_empty(account)
		self.all.remove(account)
	
	def mv(self, account1, account2):
		if account2[0] == '.' or account2[-1] == '.':
			raise ValueError("Error: Account name can't start or end with a '.' character.")
		# check if account2 name is unavailable
		if os.path.isfile(account2):
			raise ValueError(f"Error: Account {account2} already exists.")
		if os.path.isdir(account2):
			raise ValueError(f"Error: {account2} is an existing directory.")
		
		Database._make_parent_dirs(account2)
		os.rename(account1, account2)
		Database._rm_empty(account1)
		
		self.all.remove(account1)
		self.all.add(account2)
		
		# move ALL backups
		account1 = os.path.join(".backup", account1 + ".")
		account2 = os.path.join(".backup", account2 + ".")
		Database._make_parent_dirs(account2)
		dirname  = os.path.dirname(account1)
		backups  = os.listdir(dirname)
		for b1 in backups:
			b1 = os.path.join(dirname, b1)
			if os.path.isfile(b1) and b1.startswith(account1):
				b2 = b1.replace(account1, account2)
				os.rename(b1, b2)
				self.all.remove(b1)
				self.all.add(b2)
		Database._rm_empty(account1)

	def backup(self, account):
		"""
		Copy the account file into the .backup directory, preserving any folder hierarchy. Also append the current date and time to the backup.
		"""
		account_bak  = os.path.join(".backup", account) 
		account_bak += "." + time.strftime("%y%m%d%H%M%S")
		Database._make_parent_dirs(account_bak)		
		shutil.copyfile(account, account_bak)
		self.all.add(account_bak)

	@staticmethod
	def _rm_empty(account):
		"""
		remove potentially empty dirs
		"""
		try:
			dname = os.path.dirname(account)
			while dname != '':
				os.rmdir(dname)
				dname = os.path.dirname(dname)
		except OSError:
			pass # dir not empty

	@staticmethod
	def _make_parent_dirs(account):
		"""
		Make all parent directories if they do not exist.
		"""
		dname = os.path.dirname(account)
		try:
			os.makedirs(dname)
		except (FileNotFoundError, FileExistsError):
			pass