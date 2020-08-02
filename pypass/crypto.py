import sys
import os
import base64
import secrets
import logging

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class MasterKey:

	LENGTH     = 32
	SALT_LEN   = 16
	ITERATIONS = 100000
	
	def __init__(self, master = None, keyfile = ".key", saltfile = ".salt"):
		self.logger = logging.getLogger()
		
		self.keyfile  = os.path.abspath(keyfile)
		self.saltfile = os.path.abspath(saltfile)
		self.bkey = None
		self.fkey = None		
		
		exists = os.path.isfile
		if not (exists(self.keyfile) and exists(self.saltfile)):
			master = self.save(master)
		#if master is not None:
		self.login(master)

	def save(self, master = None, prompt = "New Master Password: "):
		"""
		Encrypt and save the master key.
		"""
		if master is None:
			master = input(prompt)
		if self.bkey is None:
			if os.path.isfile(self.keyfile):
				raise Exception("Error: Login required.")
			with open(self.saltfile, "wb") as f:
				f.write(os.urandom(MasterKey.SALT_LEN))
			self.bkey = Fernet.generate_key()
			self.fkey = Fernet(self.bkey)
		kek = self._kek(master)
		with open(self.keyfile, "wb") as f:
			f.write(kek.encrypt(self.bkey))
		return master
	
	def login(self, master = None, prompt = "Master Password: "):
		"""
		Unlock the master key using the master password.
		"""
		if self.fkey is None:
			if master is None:
				master = input(prompt)
			if master == "":
				raise EOFError()
			kek = self._kek(master)
			try:
				with open(self.keyfile, "rb") as f:
					self.bkey = kek.decrypt(f.read())
					self.fkey = Fernet(self.bkey)
					self.logger.info("Logged in.")
			except InvalidToken:
				self.logger.error(f"Login failed. Incorrect master password: {master}")
				raise ValueError("Error: Invalid Master Password.")
	
	def encrypt(self, message):
		"""
		Encrypt a message into a text (i.e., not bytes) code.
		"""
		return self.fkey.encrypt(message.encode()).decode()

	def decrypt(self, code):
		"""
		Decrypt a text code into plaintext.
		"""
		return self.fkey.decrypt(code.encode()).decode()
	
	def _kek(self, master):
		"""
		Derive the key encrypting key.
		"""
		master = master.encode()
		
		# TODO move this and kdf to login() or something
		with open(self.saltfile, "rb") as f:
			salt = f.read()

		# get key encrypting key (kek)
		kdf = PBKDF2HMAC(
			algorithm  = hashes.SHA256(),
			length     = MasterKey.LENGTH,
			salt       = salt,
			iterations = MasterKey.ITERATIONS,
			backend    = default_backend()
		)
		kek = base64.urlsafe_b64encode(kdf.derive(master))
		kek = Fernet(kek)
		return kek


def generate_password(length = 16, symbols = True):
	"""
	Generate a password of the given length, with or without symbol characters.
	"""
	if length < 8:
		raise ValueError("Password must be at least 8 characters long.")
	charsets = []
	charsets.append("abcdefghijkmnpqrstuvwxyz")
	charsets.append("ABCDEFGHJKLMNPQRSTUVWXYZ")
	charsets.append("23456789")
	if symbols:
		charsets.append("!@#$%^&*()-+=.,?<>_:{}|*/")
	alphabet = "".join(charsets)
	while True:
		password = "".join(secrets.choice(alphabet) for i in range(length))
		if all(any(d in password for d in group) for group in charsets):
			# at least one character from each group
			return password