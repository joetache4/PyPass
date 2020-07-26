import sys
import os
import traceback
import pypass


if __name__ == "__main__":
	try:
		
		print("===== pass =====")
		
		db   = pypass.Database()
		args = sys.argv[1:]
		
		if len(args) == 0: # interactive mode
			# log in
			while True:		
				try:
					db.login()
					break
				except ValueError as e:
					print(e)
			print("Entering interactive mode. Enter a blank line to exit.")
			pypass.parse(db, "ls")
			# parse input
			while True:
				line = input("pass> ")
				if line == "":
					if pypass.parser.yesno("Quit?", "y"):
						break
				else:
					pypass.parse(db, line)
		else: # simply parse command line args
			pypass.parse(db, args)
		
	except (KeyboardInterrupt, EOFError):
		pass
	#except:
	#	track = traceback.format_exc()
	#	print(track)