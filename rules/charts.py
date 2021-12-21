# GAME TABLES
# Starting levels and score for the new player character:
# hp, power, magic, score.
char_new_stats = (0, 0, 0, 0)
# Random roll min and max values for player character.
# Character stats.
# Character life points for levels 1 to 9. Fixed amount for every level.
char_hp  = (6, 12, 18, 24, 30, 36, 42, 48, 54)
# Character attack value for levels 1 to 9. Number of dice for attack rolls.
char_pow = (
	(1,6),
	(2,8),
	(3,10),
	(4,12),
	(5,14),
	(6,16),
	(7,18),
	(8,20),
	(9,22)
)
# Character magical points for levels 1 to 9. Fixed amount for every level.
char_mag = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
# Amount of score points given for completion of levels 1 to 11.
score_rewards = (100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1000)
flask_reward = 1000
# Starting level of the game.
level = 4	# 0 is the first level, 1 is the second, etc.
# Spells by cave level.
random_spells = True
spells = (
	('DISINTEGRATE', 'sp_disint'),
	('HEAL', 'sp_heal'),
	('INVISIBILITY', 'sp_invis'),
	('BARRIER', 'sp_barrier'),
	('DISPEL', 'sp_dispel'),
	('PETRIFY', 'sp_petrify'),
	('TURN UNDEAD', 'sp_turn'),
	('WARP', 'sp_warp'),
	('TIME STOP', 'sp_stop'),
	('KILL', 'sp_kill'),
)
# Monsters table.
# One monster per row:
# Monster name, hp, speed (4 points = player speed), min damage, max damage, score reward.
monster_book = {
	'rat': 		(4, 2, 1, 1, 0, 'rat', 	None),						# R
	'snake': 	(6, 1, 0, 0, 0, 'snake', 	['venom']),				# S
	'spider':	(8, 1, 1, 2, 0, 'spider', 	['venom']),				# P
	'muss': 	(14, 1, 0, 0, 0, 'muss', 	['rust']),					# M
	'goblin': 	(10, 2, 1, 2, 0, 'goblin', 	['traps','steal']),			# G
	'skeleton': (12, 2, 1, 2, 0, 'skeleton',['dead']),					# K
	'orcus': 	(16, 2, 1, 3, 0, 'orcus', 	['strong']),				# O
	'ghost': 	(14, 1, 1, 2, 0, 'ghost', 	['ghost','dead']),			# H
	'lich': 	(18, 1, 1, 2, 0, 'lich', 	['dead','drain']),			# L
	'daemon': 	(20, 2, 2, 3, 0, 'daemon', ['strong','vampire']),		# A
	'double': 	(4, 2, 1, 3, 0, 'pc', 	['mirror']),				# D
	'wrath': 	(4, 2, 1, 2, 0, 'wrath', 	['mirror','flair','ghost','dead','vampire']),				# D
	# peaceful dwellers
	'spider person':		(8, 2, 3, 4, 0,  'spider', 	['bound', 'peaceful']),				# P
	'goblin person': 	(10, 3, 3, 6, 0, 'goblin', 	['bound', 'peaceful']),			# G
	'skeleton person': 	(12, 2, 3, 6, 0, 'skeleton',	['dead','bound', 'peaceful']),					# K
	'orcus person': 		(16, 2, 4, 8, 0, 'orcus', 		['bound', 'peaceful']),				# O
	'ghost person': 		(14, 2, 3, 4, 0, 'ghost', 		['ghost','dead', 'bound', 'peaceful']),			# H
	'lich person': 		(18, 2, 4, 8, 0, 'lich', 		['dead', 'bound', 'peaceful']),			# L
	'daemon person': 	(20, 3, 4, 8, 0,'daemon', 	['bound', 'peaceful']),		# A
	'human person': 		(4, 2, 1, 3, 0, 'human', 		['bound', 'peaceful']),				# D
}
# EFFECTS
# name		receiver	description
# --------------------------------------
# venom		mob			inflicts poison effect on attack
# poison	pc			lose 1 hp with every step
# rust		mob			lowers hp level by 1 on attack
# traps		mob			occationally plants a trap on the square
# steal		mob			occationally removes item from inventory and shuffle inventory on attack
# dead		mob			can not be damaged without silver blade or magic, can be affected by turn undead spell
# strong	mob			pushes back 1 square on attack
# ghost		mob			can pass through impassable squares
# drain		mob			lowers magic points by 1 on attack
# vampire	mob			rises its hp by inflicted damage on attack
# mirror	mob			copies player character stats when spawns
# invisible	pc			mobs can not see pc untin pc receives any damage.
# timestop	pc			mobs are frozen until pc touches anything (collecting items allowed)
# murderer	pc			pc has killed a peaceful mob or character.
# bound		mob			mov can not move, only watches around
# peaceful	mob			mob wont attack player character.
# flair		mob			mob knows where the player is always.

# Randomize encounter spawn places.
random_spawns = False
# Labyrinth chart. Sets of monsters for every level of the caves: ('<monster_name>', spawn chance (in percents), cost).
encounters = (
	{		# level 1
		'mobs': (('rat', 100, 1),),
		'diff': 5
	},
	{		# level 2
		'mobs': (('snake', 100, 1),),
		'diff': 1
	},
	{		# level 3
		'mobs': (('spider', 100, 1),),
		'diff': 1
	},
	{  # level 4
		'mobs': (('goblin', 100, 1),),
		'diff': 1
	},
	{  # level 5
		'mobs': (('skeleton', 100, 1),),
		'diff': 1
	},
	{  # level 6
		'mobs': (('muss', 100, 1),),
		'diff': 1
	},
	{  # level 7
		'mobs': (('orcus', 100, 1),),
		'diff': 1
	},
	{  # level 8
		'mobs': (('ghost', 100, 1),),
		'diff': 1
	},
	{  # level 9
		'mobs': (('lich', 100, 1),),
		'diff': 1
	},
	{  # level 10
		'mobs': (('daemon', 100, 1),),
		'diff': 1
	},
	{  # level 11
		'mobs': (('double', 100, 1),),
		'diff': 1
	}
)

intermissions = {
	0: 'interm_grounded',
	1: 'interm_meet',
	2: 'interm_fiddle'
}

# Treasure items:
# Name, ID, encounter,
treasure = (
	('some gold', 'gold', None, -1, 1000),
	('a potion', 'ptn_red', None, -1, 0),
	('a potion', 'ptn_yellow', ('muss','goblin','ghost','lich','daemon','double'), -1, 0),
	('a potion', 'ptn_blue', ('muss','goblin','ghost','lich','daemon','double'), -1, 0),
	('a key', 'key_gold', None, -1, 0),
	('a spellbook', 'sp_unknown', None, -1, 0),
	('DISINTEGRATE', 'sp_disint', None, -1, 0),
	('HEAL', 'sp_heal', None, -1, 0),
	('INVISIBILITY', 'sp_invis', None, -1, 0),
	('BARRIER', 'sp_barrier', None, -1, 0),
	('DISPEL', 'sp_dispel', None, -1, 0),
	('PETRIFY', 'sp_petrify', None, -1, 0),
	('TURN UNDEAD', 'sp_turn', None, -1, 0),
	('WARP', 'sp_warp', None, -1, 0),
	('TIME STOP', 'sp_stop', None, -1, 0),
	('KILL', 'sp_kill', None, -1, 0),
	('a silver blade', 'slvr_blade', ('goblin', 'double', 'lich'), 4, 0),
	('the flask of springs', 'm_flask', None, 99, 0)
)
gold = (
	(1, 10),
	(2, 12),
	(4, 16),
	(7, 22),
	(11, 30),
	(16, 40),
	(22, 52),
	(29, 66),
	(37, 82),
	(46, 100),
	(56, 120),
)
