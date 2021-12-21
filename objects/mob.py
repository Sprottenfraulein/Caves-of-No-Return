# Monsters object
import random

class Mob:
    def __init__(self, mob_name, x, y, mob_stats):
        self.name = mob_name
        self.x = x
        self.y = y
        self.max_hp, self.speed, self.dmg_min, self.dmg_max, self.reward, self.ani_name, self.effects = mob_stats
        if self.effects is None:
            self.effects = []
            # effects:
            # ghost     going through walls
        self.hp = self.max_hp
        # Variables regulating how frequently mob will move
        self.sp_pts = 0
        self.max_sp_pts = 4
        # Declaring maze-related variables.
        self.offset_x = 0
        self.offset_y = 0
        self.mov_dir = 0
        self.sight_dir = 0
        self.last_frame = None
        self.sp = 1
        self.vis = True
        self.turn_ind = False
        self.alert = False

    def attack(self, target, charts):
        # Making get_frame function rotate mob towards player character
        self.offset_x = (target.x - self.x) * -1
        self.offset_y = (target.y - self.y) * -1
        # Applying a wound to target
        dmg = random.randrange(self.dmg_min, self.dmg_max + 1)
        effects = []
        if 'venom' in self.effects:
            effects.append('poison')
            target.mov_dir = 0
        if 'rust' in self.effects and random.randrange(1, 101) <= 50:
            target.hp_lvl = max(target.hp_lvl - 1, 0)
        if 'steal' in self.effects and random.randrange(1, 101) <= 50:
            if len(target.inventory) > 0:
                random.shuffle(target.inventory)
                del target.inventory[0]
        if 'drain' in self.effects:
            target.mag = max(0, target.mag - 1)
        if 'vampire' in self.effects:
            self.hp += dmg

        return target.wound(dmg, effects)

    def wound(self, dmg, effect=None):
        hp_loss = dmg
        self.hp -= hp_loss
        return hp_loss