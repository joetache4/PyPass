import sys
import os
import traceback
from contextlib import ContextDecorator

import pypass


def main():
	try:
		try:
			os.mkdir("db")
		except OSError:
			pass
		pypass.configure_logging("db/.log")
		
		print("==== pypass ====")
		
		# log in
		while True:		
			try:
				parser = pypass.Parser(None, "db")
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