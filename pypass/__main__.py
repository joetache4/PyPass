import sys
import os
import traceback
from contextlib import ContextDecorator

from .parser import Parser
from .database import Database
from .log import configure_logging


def main():
	try:
	
		os.chdir(os.path.dirname(__file__))
		try:
			os.mkdir("db")
		except OSError:
			pass
		configure_logging("db/.log")
		
		print("==== pypass ====")
		
		# log in
		while True:		
			try:
				db = Database("db")
				parser = Parser(db)
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
				except (KeyboardInterrupt, EOFError):
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