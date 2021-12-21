# Map legend.

tiles = {
    'floor_stone': 8,
    'floor_plate': 9,
    'floor_grass': 24,
    'wall_stone': 64,
    'wall_plate': 65,
    'wall_tree': 80,
    'hazard_spikes': 96,
    'trap_invis': 104,
    'stairs_up': 112,
    'stairs_down': 116,
    'door_wood': 120,
    'door_iron': 124,
    'port_stone': 128,
    'pit_hole': 136,
    'pit_stone': 152
}

objects = {
    'memo_page': 26,
    'mov_stone': 96,
    'chest': 144,
    'ptn_red': 152,
    'ptn_yellow': 153,
    'ptn_blue': 154,
    'sp_disint': 160,
    'sp_heal': 161,
    'sp_invis': 162,
    'sp_barrier': 163,
    'sp_dispel': 164,
    'sp_petrify': 165,
    'sp_turn': 166,
    'sp_warp': 167,
    'sp_stop': 168,
    'sp_kill': 169,
    'sp_unknown': 170,
    'key_gold': 192,
    'hp_up': 200,
    'pow_up': 201,
    'mag_up': 202,
    'slvr_blade': 203,
    'm_flask': 204,
    'gold': 205
}

mobs = {
    125: 'spider person',
    128: 'goblin person',
    129: 'skeleton person',
    130: 'orcus person',
    131: 'ghost person',
    132: 'lich person',
    133: 'daemon person',
    134: 'human person',

    224: 'rat',
    225: 'spider',
    226: 'snake',
    227: 'muss',
    228: 'goblin',
    229: 'skeleton',
    230: 'orcus',
    231: 'ghost',
    232: 'lich',
    233: 'daemon',
    234: 'double',
    235: 'wrath',
}

flags = {
    'space': 0,
    'wall': 8,
    'fake_wall': 9,
    'magic_wall': 10,
    'spikes': 11,
    'trap': 12,
    'pit': 13,
    'trap_poison': 14,
    'door': 16,
    'metal_door': 18,
    'start': 24,
    'exit': 25
}

# Cave names and maps.
# Map byte format:
#| BYTE POSITION	 |		MEANING
#+-------------------+------------------
#| 0				 |		width
#| 1				 |		height
#| 2 to 2+n			 |		maze body (n = width*height)
#| 2+n+1 to 2+n+1+n	 |		maze flags
#| 2+n+1+n+1 to end	 |		maze title
#+-------------------+------------------