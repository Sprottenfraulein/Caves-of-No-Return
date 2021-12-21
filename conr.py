# Main script with pygame loop.
# Importing resources manager.
import res
# Importing game blocks. ADD NEW BLOCK IMPORTS AT THE END OF 
# THE LINE, SEPARATED BY COMMAS.
from blocks import menu, cave, demo
from objects import counter

def launch(pg):
	# Creating resource manager.
	res_man = res.Res(pg)
	# Creating game blocks objects.
	# INSERT NEW BLOCKS INITIALISINGS IN THIS LIST.
	app_blocks = (
		menu.Menu(pg, res_man),
		cave.Cave(pg, res_man),
		demo.Demo(pg, res_man)
	)
	# Composing initial playcard for the first block.
	playcard = {
		'run': 0,	# Starting the first block from app_blocks.
	}
	while playcard:
		# Run block and receive a new playcard when the block is finished.
		playcard = block_run(pg, app_blocks, playcard)
	print("No more playcards. Game over.")

# Run playcard
def block_run(pg, app_blocks, playcard):
	# Trying to get a block index from playcard and aborting if it is absent.
	try:
		block = app_blocks[playcard['run']]
	except KeyError:
		return

	block.counter0 = counter.Counter(15,4)
	
	block.start(playcard)

	while block.active:
		# Checking events.
		events(pg, block)
		# Making calculations of what's going on.
		block.tick() 
		block.counter0.tick()
		# Drawing what's going on.
		block.draw(pg.canvas)
		# Exposing game screen to display.
		if block.redraw:
			pg.screen.blit(
				pg.pygame.transform.scale(pg.canvas, pg.screen_res), 
				(0,0)
			)
			block.redraw = False
		pg.clock.tick_busy_loop(pg.fps)
		pg.pygame.display.flip()

	block.finish()

	# Returning necessary data from game block to main loop.
	return block.playcard

# Pygame events check.
def events(pg, block):
	for event in pg.pygame.event.get():
		# Checking for keys pressed globally.
		if event.type == pg.pygame.KEYDOWN:
			# Exit the app when Esc is pressed.
			if event.key == pg.pygame.K_q:
				# exit()
				pass

		# Checking for keys in block locally.
		block.events(event)
