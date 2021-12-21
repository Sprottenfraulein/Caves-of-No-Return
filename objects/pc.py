# Player character class.
import random

class PC:
	def __init__(self, hp_lvl, hp, pow_lvl, mag_lvl, mag, score, effects=None, inventory=None, name=None):
		# Declaring initial stats.
		self.hp_lvl = hp_lvl
		self.hp = hp
		self.pow_lvl = pow_lvl
		self.mag_lvl = mag_lvl
		self.mag = mag
		self.score = score
		if effects is None:
			self.effects = []
		else:
			self.effects = effects
		if inventory is None:
			self.inventory = []
		else:
			self.inventory = inventory
		self.name = name
		self.effects = set()
		# Declaring maze-related variables.
		self.log = [
			('ONLY ECHOING FOOTSTEPS ACCOMPANIED YOU', (255,255,255)),
			('WHILE YOU DESCENDED INTO THE DARK...', (255,255,255))
		]
		self.x = None
		self.y = None
		self.offset_x = 0
		self.offset_y = 0
		self.mov_dir = 0
		self.last_frame = None
		self.sp = 1
		self.vis = True
		self.ani_name = 'pc'

	def attack(self, target, charts):
		# Making get_frame function rotate character towards the enemy
		self.offset_x = (target.x - self.x) * -1
		self.offset_y = (target.y - self.y) * -1
		# Applying a wound to target
		dmg_min, dmg_max = charts.char_pow[self.pow_lvl]
		dmg = random.randrange(dmg_min, dmg_max + 1)
		return target.wound(dmg)

	def wound(self, dmg, effects=None):
		hp_loss = dmg
		# Last chance.
		if self.hp > 1:
			self.hp = max(self.hp - hp_loss, 1)
		else:
			self.hp -= hp_loss
		if effects:
			self.effects.update(effects)
		if 'invisible' in self.effects:
			self.effects.remove('invisible')
			self.last_frame = None
		return hp_loss

