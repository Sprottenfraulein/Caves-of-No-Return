# Importing pygame and game settings modules.
import pygame, settings
from library import audio

class PG:
	def __init__(self):
		# Removing pygame audio playback delay.
		pygame.mixer.pre_init(44100, -16, 1, 512)
		# Initializing pygame and audio mixer.
		pygame.init()
		pygame.mixer.init()
		# Hiding OS cursor.
		pygame.mouse.set_visible(False)
		self.pygame = pygame
		self.audio = audio.Audio(pygame)
		# Initializing pygame display.
		self.APP_SCALE = settings.app_scale
		self.screen_res = (settings.APP_RES[0] * self.APP_SCALE, 
				  		  settings.APP_RES[1] * self.APP_SCALE)
		self.screen = pygame.display.set_mode(self.screen_res)
		# Creating buffer canvas.
		self.canvas = pygame.Surface(settings.APP_RES)
		# Setting game caption.
		self.pygame.display.set_caption(settings.APP_CAPTION)
		# Retrieving fps variable.
		self.fps = settings.FPS
		# Creating pygame Clock object for maintaining stable framerate.
		self.clock = pygame.time.Clock()
		# Reading controls.
		self.controls = {
			'up': settings.cntrls_up,
			'right': settings.cntrls_right,
			'down': settings.cntrls_down,
			'left': settings.cntrls_left,
			'new_game': settings.cntrls_newgame,
			'wait': settings.cntrls_wait,
			'say': settings.cntrls_say,
			'spell1': settings.cntrls_spell1,
			'spell2': settings.cntrls_spell2,
			'spell3': settings.cntrls_spell3,
			'spell4': settings.cntrls_spell4,
			'spell5': settings.cntrls_spell5,
			'spell6': settings.cntrls_spell6,
			'spell7': settings.cntrls_spell7,
			'spell8': settings.cntrls_spell8,
			'spell9': settings.cntrls_spell9,
			'exit': settings.cntrls_exit
		}
		print('Pygame initialized successfully.')
