import sys
import os
import traceback

import pypass


if __name__ == "__main__":
	try:
		
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