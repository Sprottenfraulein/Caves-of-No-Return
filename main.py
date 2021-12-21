#!/usr/bin/python3.7

# Import pygame setup script and main game script.
import pginit, conr

# Run the scripts if we are 'main'.
if __name__ == '__main__':
	# Run pygame setup and receive setup object.
	pg = pginit.PG()
	# Launch main game loop and pass setup object.
	conr.launch(pg)
