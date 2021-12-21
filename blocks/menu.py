# Game block with title and menu. Importing os module for data paths.
import os
# Importing charts with rule sets for the game.
from rules import charts, texts
# Importing player class.
from objects import pc, text, sprite


class Menu:
    def __init__(self, pg, res_man):
        # Receiving link to pygame object, setup settings and resources manager.
        self.pg = pg
        self.res_man = res_man
        self.counter0 = None
        # Flag for main loop control. Setting False breaks the loop and finishes the block.
        self.playcard = None
        # Flag for redrawing the screen. Canvas is being updated only when the flag is up.
        self.active = True
        self.redraw = True
        self.hiscores = None

    def start(self, playcard):
        # CUSTOM BLOCK ELEMENTS
        self.hiscores = self.hiscores_load(os.path.join('data', 'hiscores.cnr'))
        self.gui_create()

        self.redraw = True
        self.active = True
        self.pg.audio.music('menu')

    def tick(self):
        # Setting 'active' flag to 'False' to exit main loop.
        # self.active = False
        pass

    def draw(self, surface):
        # Drawing the block graphics onto the pygame display.
        # Returning if no need to redraw scene.
        if not self.redraw:
            return
        # Clearing the surface
        surface.fill(self.res_man.colors['bg'])
        # Drawing pages.
        if self.signs_vis:
            for obj in self.signs:
                obj.draw(surface)
        if self.pages_vis:
            for obj in self.pages[self.page]:
                obj.draw(surface)

    def finish(self):
        # Concluding the block before returning playcard to the playcards loop in conr.py
        # Resetting parameters if necessary.
        self.pages.clear()
        self.signs.clear()
        self.page = 0
        self.pg.audio.music_stop()
        self.pg.audio.playlist()

    # MAIN MENU FUNCTIONS
    def char_create(self):
        # Reading initial character stats from rules charts.
        hp_lvl = charts.char_new_stats[0]
        pow_lvl = charts.char_new_stats[1]
        mag_lvl = charts.char_new_stats[2]
        score = charts.char_new_stats[3]
        hp = charts.char_hp[hp_lvl]
        mag = charts.char_mag[mag_lvl]
        # Creating a new player character object.
        pc_new = pc.PC(hp_lvl, hp, pow_lvl, mag_lvl, mag, score)
        # Returning a new pc object.
        return pc_new

    def events(self, event):
        # Local block events go here.
        if event.type == self.pg.pygame.KEYDOWN:
            # Switching pages of instructions
            if event.key in (self.pg.controls['right'], self.pg.controls['down']):
                self.page += 1
                if self.page >= len(self.pages):
                    self.page = 0
                self.redraw = True
                self.pg.audio.sound('cluck')
            if event.key in (self.pg.controls['left'], self.pg.controls['up']):
                self.page -= 1
                if self.page < 0:
                    self.page = len(self.pages) - 1
                self.redraw = True
                self.pg.audio.sound('cluck')
            # Launching a new game
            if event.key == self.pg.controls['new_game']:
                self.pg.audio.sound('cluck')
                self.new_game()
            if event.key == self.pg.controls['exit']:
                self.pg.audio.sound('cluck')
                exit()

    def new_game(self):
        # Creating a new character and a playcard.
        self.playcard = {
            'run': 1,
            'pc': self.char_create(),
            'lvl': charts.level
        }
        # Signal to end the block loop.
        self.active = False

    def hiscores_load(self, filename):
        try:
            hiscores = open(filename, 'rb')
        except FileNotFoundError:
            return None
        hiscores_bytes = hiscores.read()
        hiscores.close()
        pos_total = hiscores_bytes[0]
        scoreboard = []
        entry_len = 17
        for i in range(0, min(pos_total, 10)):
            byte_start = 1 + i * entry_len
            score_entry = hiscores_bytes[byte_start:byte_start + entry_len]
            name = score_entry[0:12].decode('utf-8')
            score_bytes = score_entry[12:15]
            score = score_bytes[0] * 65536 + score_bytes[1] * 256 + score_bytes[2]
            lvl = score_entry[15]
            hero = score_entry[16]
            scoreboard.append((name, score, lvl, hero))
        return scoreboard

    # Interface creation.
    def gui_create(self):
        # Creating list for groups of objects to be displayed as pages.
        self.pages = []
        self.page = 0
        self.pages_vis = True
        # Creating list of object to be displayed continuosly.
        self.signs = []
        self.signs_vis = True
        # Creating constant menu text.
        self.signs.extend([
            text.Text(self.pg, self.res_man, texts.game_text['game_version'],
                      ((4, 4),), self.res_man.colors['fnt_muted']),
            text.Text(self.pg, self.res_man, texts.game_text['game_author'],
                      ((200, 72),), self.res_man.colors['fnt_muted'], align=1),
            text.Text(self.pg, self.res_man, texts.game_text['menu_controls'],
                      ((200, 220),), self.res_man.colors['fnt_muted'], align=1)
        ])
        # Creating menu text on title page.
        self.pages.append([
            text.Text(self.pg, self.res_man, texts.game_text['newbie_message'],
                      ((200, 132),), self.res_man.colors['fnt_normal'], align=1),
        ])
        self.pages.append((
            text.Text(self.pg, self.res_man, texts.game_text['menu_intro_h'],
                      ((200, 104),), self.res_man.colors['fnt_header'], align=1),
            text.Text(self.pg, self.res_man, texts.game_text['menu_intro_p'],
                      ((200, 120),), self.res_man.colors['fnt_normal'], align=1),
        ))
        self.pages.append((
            text.Text(self.pg, self.res_man, texts.game_text['menu_intro_h'],
                      ((200, 104),), self.res_man.colors['fnt_header'], align=1),
            text.Text(self.pg, self.res_man, texts.game_text['menu_fullcontrols'], ((200, 120),),
                      self.res_man.colors['fnt_normal'], align=1),
        ))
        if self.hiscores is not None and len(self.hiscores) > 0:
            hiscores_page = [text.Text(self.pg, self.res_man, texts.game_text['menu_hiscores_h'],
                          ((200, 104),), self.res_man.colors['fnt_header'], align=1)]
            for i in range(0, len(self.hiscores)):
                score_row = str(i+1).zfill(2) + ' ' + self.hiscores[i][0] + ' ' + str(self.hiscores[i][1]).zfill(8) + ' LEVEL:' + str(self.hiscores[i][2]+1)
                hiscores_entry=[text.Text(self.pg, self.res_man, (score_row,), ((96, 120 + i * 8),),
                                            self.res_man.colors['fnt_normal'], align=0)]
                if self.hiscores[i][3]:
                    hiscores_entry.append(
                        sprite.Sprite(self.pg, self.res_man,
                                      ((0, (16, 0, 8, 8)),), ('0'), ((64, 120 + i * 8),),
                                      size=(8, 8))
                    )
                hiscores_page.extend(hiscores_entry)
            self.pages.append(hiscores_page)
        # Creating logo
        self.signs.append(
            sprite.Sprite(self.pg, self.res_man,
                          ((0, (0, 64, 172, 36)),),
                          ('0'),
                          ((200, 16),), align=1,
                          size=(172, 36)
                          ),
        )


