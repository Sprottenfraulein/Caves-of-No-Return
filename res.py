# This script loads and sets game resources.
# Importing os module for paths.
import os

class Res:
	def __init__(self, pg):
		self.pg = pg
		# Loading tilesets. ADD NEW TILESETS IN THIS LIST. HAS TO BE 256x256 pixels.
		self.tilesets = (
			pg.pygame.image.load(os.path.join('data', 'conr01.png')),
		)
		# setting game icon
		icon = pg.pygame.Surface((16,16))
		icon.blit(self.tilesets[0], (0,0), (5,214,16,16))
		pg.pygame.display.set_icon(icon)
		# Declaring font chart.
		# Font chart keeps coordinates of font symbols on a tileset.
		self.font_ts = 0
		self.font_size = (8,8)
		self.font_chart = {
			'1': (0,240),
			'2': (8,240),
			'3': (16,240),
			'4': (24,240),
			'5': (32,240),
			'6': (40,240),
			'7': (48,240),
			'8': (56,240),
			'9': (64,240),
			'0': (72,240),
			'*': (80,240),
			'A': (0,248),
			'B': (8,248),
			'C': (16,248),
			'D': (24,248),
			'E': (32,248),
			'F': (40,248),
			'G': (48,248),
			'H': (56,248),
			'I': (64,248),
			'J': (72,248),
			'K': (80,248),
			'L': (88,248),
			'M': (96,248),
			'N': (104,248),
			'O': (112,248),
			'P': (120,248),
			'Q': (128,248),
			'R': (136,248),
			'S': (144,248),
			'T': (152,248),
			'U': (160,248),
			'V': (168,248),
			'W': (176,248),
			'X': (184,248),
			'Y': (192,248),
			'Z': (200,248),
			'!': (208,248),
			'?': (216,248),
			'.': (224,248),
			',': (232,248),
			':': (240,248),
			'-': (248,248),
			' ': (96,240),
			'/': (88,240),
		}
		# Declaring game colors.
		self.colors = {
			'fnt_muted': (200,50,0),
			'fnt_normal': (200,100,0),
			'fnt_header': (250,150,0),
			'fnt_attent': (255,0,0),
			'fnt_accent': (255,230,0),
			'fnt_bonus': (0,254,0),
			'frm_normal': (200,100,0),
			'fnt_celeb': (255,255,255),
			'bg': (10,10,10),
			'transparent': (0,255,0)
		}
		# Declaring game tiles.
		self.tiles = {
			'wall': (0, (0, 32, 16, 16))
		}
