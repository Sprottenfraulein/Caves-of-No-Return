# Game block for presentations and hiscores.
import os
# Importing objects
from objects import text, sprite
from rules import charts, texts


class Demo:
    def __init__(self, pg, res_man):
        # Receiving link to pygame object, setup settings and resources manager.
        self.pg = pg
        self.res_man = res_man
        self.counter0 = None
        self.pc = None
        self.mode = None
        # Flag for main loop control. Setting False breaks the loop and finishes the block.
        self.playcard = None
        self.active = True
        self.redraw = True
        self.hiscores = None
        self.name_input = ''
        self.name_text_obj = None
        self.name_redraw = False
        self.sc_pc_pos = None

    def start(self, playcard):
        self.active = True
        self.redraw = True
        # Reading playcards.
        # Demo types:
        # 0		player alive but next cave not found
        # 1		intermission message
        # 2		player is dead
        # 3		player alive, quest item obtained, no more caves. True ending.
        self.pc = playcard['pc']
        self.mode = playcard['demo']
        self.lvl = playcard['lvl']
        if self.mode != 1:
            self.hiscores, self.sc_pc_pos = self.hiscores_load(os.path.join('data', 'hiscores.cnr'), self.pc, self.lvl,
                                                               self.mode == 3)
            self.name_input = ''
        self.gui_create()
        if self.mode == 3:
            self.pg.audio.music('ending')

    def hiscores_load(self, filename, pc, p_lvl, won):
        try:
            hiscores = open(filename, 'rb')
        except FileNotFoundError:
            scoreboard = [(' ' * 12, pc.score, p_lvl, won)]
            pc_pos = 0
            self.name_redraw = True
            return scoreboard, pc_pos
        hiscores_bytes = hiscores.read()
        hiscores.close()
        pos_total = hiscores_bytes[0]
        scoreboard = []
        entry_len = 17
        put = False
        pc_pos = None
        pos_max = 10
        for i in range(0, min(pos_total, pos_max)):
            byte_start = 1 + i * entry_len
            score_entry = hiscores_bytes[byte_start:byte_start + entry_len]
            name = score_entry[0:12].decode('utf-8')
            score_bytes = score_entry[12:15]
            score = score_bytes[0] * 65536 + score_bytes[1] * 256 + score_bytes[2]
            lvl = score_entry[15]
            hero = score_entry[16]
            if pc.score > score and not put:
                scoreboard.append((' ' * 12, pc.score, p_lvl, won))
                put = True
                pc_pos = i
                i += 1
                self.name_redraw = True
                if i >= pos_max:
                    break
            scoreboard.append((name, score, lvl, hero))
        if pos_total < pos_max and not put:
            scoreboard.append((' ' * 12, pc.score, p_lvl, won))
            pc_pos = pos_total
            self.name_redraw = True
        return scoreboard, pc_pos

    def hiscores_save(self, filename, hiscores):
        scores_total = min(len(hiscores), 255)
        f = open(filename, 'wb')
        save_list = []
        save_list.append(scores_total)
        for i in range(0, scores_total):
            name = hiscores[i][0] + ' ' * (12 - len(hiscores[i][0]))
            name = name.encode('utf-8')
            save_list.extend(name)
            score = (min(255, hiscores[i][1] // 65536), min(255, hiscores[i][1] % 65536 // 256), hiscores[i][1] % 256)
            save_list.extend(score)
            save_list.append(hiscores[i][2])
            save_list.append(hiscores[i][3])
        f.write(bytes(save_list))
        f.close()

    def tick(self):
        # Setting 'active' flag to 'False' to exit main loop.
        if self.name_redraw:
            self.name_text_obj = text.Text(self.pg, self.res_man, (self.name_input,),
                                           ((120, 120 + self.sc_pc_pos * 8),),
                                           self.res_man.colors['fnt_normal'], align=0)
            self.redraw = True
            self.name_redraw = False

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
            # Draw hiscore player entry on page 1.
            if self.page == 1 and self.name_text_obj is not None:
                self.name_text_obj.draw(surface)

    def finish(self):
        # Concluding the block before returning playcard to the playcards loop in conr.py
        self.pages.clear()
        self.signs.clear()
        self.page = 0
        self.hiscores = None
        self.name_input = ':'
        self.name_text_obj = None
        self.name_redraw = False
        self.sc_pc_pos = None

    def events(self, event):
        # Local block events go here.
        if event.type == self.pg.pygame.KEYDOWN:
            # Switching pages of instructions
            if event.key == self.pg.controls['exit']:
                self.playcard = {
                    'run': 0
                }
                self.active = False
                self.pg.audio.sound('cluck')
            # Continue to next level if intermission.
            if event.key == self.pg.controls['new_game']:
                if self.mode == 1:
                    self.playcard = {
                        'run': 1,
                        'pc': self.pc,
                        'lvl': self.lvl + 1
                    }
                    self.active = False
                    self.redraw = True
                    self.pg.audio.sound('cluck')
                elif self.sc_pc_pos is None or self.page == 0:
                    self.page += 1
                    if self.page == len(self.pages):
                        self.page = 0
                    self.redraw = True
                    self.pg.audio.sound('cluck')
                    return

            # Input name if there is a scoreboard and player got a place in the top 10.
            if self.hiscores is not None and self.sc_pc_pos is not None and self.page == 1:
                if 62 < event.key < 91 or 96 < event.key < 123 or 41 < event.key < 58 or event.key in [32, 33, 58, 63]:
                    self.name_input += chr(event.key)
                    self.name_input = self.name_input[:12]
                    self.name_redraw = True
                    self.pg.audio.sound('cluck')
                elif event.key == 8 and len(self.name_input) > 0:
                    self.name_input = self.name_input[:-1]
                    self.name_redraw = True
                    self.pg.audio.sound('cluck')
                elif event.key == 13:
                    if len(self.name_input) <= 1:
                        self.name_input = '---'
                    self.hiscores[self.sc_pc_pos] = (self.name_input, self.pc.score, self.lvl, self.mode == 3)
                    self.hiscores_save(os.path.join('data', 'hiscores.cnr'), self.hiscores)
                    self.sc_pc_pos = None
                    self.name_redraw = False
                    self.playcard = {
                        'run': 0
                    }
                    self.active = False
                    self.pg.audio.sound('cluck')
                elif event.key == self.pg.controls['exit']:
                    self.name_input = '---'
                    self.hiscores[self.sc_pc_pos] = (self.name_input, self.pc.score, self.lvl, self.mode == 3)
                    self.hiscores_save(os.path.join('data', 'hiscores.cnr'), self.hiscores)
                    self.sc_pc_pos = None
                    self.name_redraw = False
                    self.playcard = {
                        'run': 0
                    }
                    self.active = False
                    self.pg.audio.sound('cluck')

    # Interface creation.
    def gui_create(self):
        # Creating list for groups of objects to be displayed as pages.
        self.pages = []
        self.page = 0
        self.pages_vis = True
        # Creating list of object to be displayed continuously.
        self.signs = []
        self.signs_vis = True
        # Creating constant menu text.
        # If it an intermission.
        if self.mode == 1:
            self.signs.extend([
                text.Text(self.pg, self.res_man, texts.game_text['game_version'],
                          ((4, 4),), self.res_man.colors['fnt_muted']),
                text.Text(self.pg, self.res_man, texts.game_text['menu_intermission_h'],
                          ((200, 104),), self.res_man.colors['fnt_header'], align=1),
                # text.Text(self.pg, self.res_man, texts.game_text['inter_controls'],
                #           ((200, 220),), self.res_man.colors['fnt_muted'], align=1)
            ])
            self.signs.append(
                sprite.Sprite(self.pg, self.res_man,
                              ((0, (0, 64, 172, 36)),),
                              ('0'),
                              ((200, 16),), align=1,
                              size=(172, 36)
                              ),
            )
            self.pages.append((
                text.Text(self.pg, self.res_man, texts.game_text[charts.intermissions[self.lvl]],
                          ((200, 120),), self.res_man.colors['fnt_normal'], align=1),
                text.Text(self.pg, self.res_man, texts.game_text['ending_controls_n'],
                          ((200, 220),), self.res_man.colors['fnt_muted'], align=1)
            ))
        # If it is the end.
        elif self.mode == 3:
            self.signs.extend([
                text.Text(self.pg, self.res_man, texts.game_text['game_version'],
                          ((4, 4),), self.res_man.colors['fnt_muted']),
                text.Text(self.pg, self.res_man, texts.game_text['menu_final'],
                          ((200, 104),), self.res_man.colors['fnt_header'], align=1),
                text.Text(self.pg, self.res_man, texts.game_text['ending_controls_q'],
                          ((200, 228),), self.res_man.colors['fnt_muted'], align=1)
            ])
            self.signs.append(
                sprite.Sprite(self.pg, self.res_man,
                              (
                                  (0, (0, 128, 192, 104)),  # Setting tile 0
                              ),
                              (
                                  '0'
                              ),
                              (
                                  (200, 8),
                              ), align=1,
                              size=(192, 104)
                              ),
            )
        # If it is game over.
        else:
            self.signs.extend([
                text.Text(self.pg, self.res_man, texts.game_text['game_version'],
                          ((4, 4),), self.res_man.colors['fnt_muted']),
                text.Text(self.pg, self.res_man, texts.game_text['menu_gameover_h'],
                          ((200, 104),), self.res_man.colors['fnt_header'], align=1),
                text.Text(self.pg, self.res_man, texts.game_text['ending_controls_q'],
                          ((200, 228),), self.res_man.colors['fnt_muted'], align=1)
            ])
            self.signs.append(
                sprite.Sprite(self.pg, self.res_man,
                              ((0, (0, 64, 172, 36)),),
                              ('0'),
                              ((200, 16),), align=1,
                              size=(172, 36)
                              ),
            )
        # Creating menu text on title page.
        if self.mode == 0:
            self.pages.append((
                text.Text(self.pg, self.res_man, texts.game_text['lost_message'],
                          ((200, 120),), self.res_man.colors['fnt_normal'], align=1),
                text.Text(self.pg, self.res_man, texts.game_text['ending_controls_n'],
                          ((200, 220),), self.res_man.colors['fnt_muted'], align=1)
            ))
        elif self.mode == 2:
            self.pages.append([
                text.Text(self.pg, self.res_man, texts.game_text['dead_message'],
                          ((200, 120),), self.res_man.colors['fnt_normal'], align=1),
                text.Text(self.pg, self.res_man, texts.game_text['ending_controls_n'],
                          ((200, 220),), self.res_man.colors['fnt_muted'], align=1)
            ])
        elif self.mode == 3:
            self.pages.append([
                text.Text(self.pg, self.res_man, texts.game_text['final_message'],
                          ((200, 120),), self.res_man.colors['fnt_normal'], align=1),
                text.Text(self.pg, self.res_man, texts.game_text['ending_controls_n'],
                          ((200, 220),), self.res_man.colors['fnt_muted'], align=1)
            ])
        if self.hiscores is not None and len(self.hiscores) > 0:
            hiscores_page = [text.Text(self.pg, self.res_man, texts.game_text['ending_controls_hs'],
                          ((200, 220),), self.res_man.colors['fnt_muted'], align=1)]
            for i in range(0, len(self.hiscores)):
                score_row = str(i+1).zfill(2) + ' ' + self.hiscores[i][0] + ' ' + str(self.hiscores[i][1]).zfill(8) + ' LEVEL:' + str(self.hiscores[i][2] +1)
                hiscores_entry = [text.Text(self.pg, self.res_man, (score_row,), ((96, 120 + i * 8),),
                                            self.res_man.colors['fnt_normal'], align=0)]
                if self.hiscores[i][3]:
                    hiscores_entry.append(
                        sprite.Sprite(self.pg, self.res_man,
                                      ((0, (16, 0, 8, 8)),), ('0'), ((64, 120 + i * 8),),
                                      size=(8, 8))
                    )

                hiscores_page.extend(hiscores_entry)

            self.pages.append(hiscores_page)
        self.pages.append((
            text.Text(self.pg, self.res_man, texts.game_text['menu_fullcontrols'],
                      ((200, 120),), self.res_man.colors['fnt_normal'], align=1),
        ))
