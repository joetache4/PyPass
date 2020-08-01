import sys
import os
import traceback
from contextlib import ContextDecorator

import pypass


class chdir (ContextDecorator):
	def __init__(self, dir):
		self.dir = dir
	def __enter__(self):
		self.old_dir = os.getcwd()
		try:
			os.chdir(self.dir)
		except FileNotFoundError:
			os.mkdir(self.dir)
			os.chdir(self.dir)
		return self
	def __exit__(self, typ, val, traceback):
		os.chdir(self.old_dir)
		

@chdir("db")
def main():
	try:
		pypass.configure_logging(".log.txt")
		
		print("==== pypass ====")
		
		# log in
		while True:		
			try:
				parser = pypass.Parser()
				break
			except ValueError as e:
				print(e)
		print("Entering interactive mode. Enter a blank line to exit.")
		parser.parse("ls")
		
		# parse input
		while True:
			line = input("pypass> ")
			if line:
				try:
					parser.parse(line)
				except KeyboardInterrupt:
					print() # do nothing else
				except ValueError as e:
					print(e)
			elif input("Quit? [Y/n]").lower() not in ["n", "no"]:
				break
		
	except (KeyboardInterrupt, EOFError):
		pass
	#except:
	#	track = traceback.format_exc()
	#	print(track)

if __name__ == "__main__":
	main()