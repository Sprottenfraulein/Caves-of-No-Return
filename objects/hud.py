# User interface overlay for cave block.
from objects import sprite, text
from rules import texts, charts

class Hud:
    def __init__(self, pg, res_man, grid_size, disp_size_x, disp_size_y, pc=None):
        self.pg = pg
        self.res_man = res_man
        self.GRID_SIZE = grid_size
        self.disp_size_x = disp_size_x
        self.disp_size_y = disp_size_y
        self.message_win = self.pg.pygame.Surface((400, self.GRID_SIZE * 3))
        self.stats_win = self.pg.pygame.Surface((self.GRID_SIZE * 6, self.GRID_SIZE * (self.disp_size_y - 2)))
        self.mw_xy = (0, self.GRID_SIZE * (self.disp_size_y - 2))
        self.sw_xy = (0, 0)
        self.mw_redraw = True
        self.sw_redraw = True
        self.pc = pc
        # Creating text
        # Status Window
        self.stats_text = text.Text(self.pg, self.res_man, texts.game_text['stats_text'],
						((8, 16),), self.res_man.colors['fnt_normal'], align=0)
        self.items_text = text.Text(self.pg, self.res_man, texts.game_text['items_text'],
                                    ((8, 96),), self.res_man.colors['fnt_normal'], align=0)
        self.effects_text = text.Text(self.pg, self.res_man, texts.game_text['effects_text'],
                                    ((8, 64),), self.res_man.colors['fnt_normal'], align=0)
        self.sprites = self.sprites_create()

    def draw(self, surface):
        if self.mw_redraw:
            self.message_win.fill(self.res_man.colors['bg'], (0, 0, 400, self.GRID_SIZE * 3))
            mw_rect = (1, 1, 398, self.GRID_SIZE * 3 - 2)
            self.pg.pygame.draw.rect(self.message_win, self.res_man.colors['frm_normal'], mw_rect, self.pg.APP_SCALE)
            # Drawing log
            if self.pc:
                for i in range(0, mw_rect[3] // 8 - 1):
                    try:
                        text.Text(self.pg, self.res_man,
                                           (self.pc.log[-4 + i][0],),
                                           ((8, i * 8 + 8),), self.pc.log[-4 + i][1], align=0).draw(self.message_win)
                    except IndexError:
                        pass
            self.mw_redraw = False
        if self.sw_redraw:
            # Drawing a player character panel.
            self.stats_win.fill(self.res_man.colors['bg'], (0, 0, self.GRID_SIZE * 6, self.GRID_SIZE * (self.disp_size_y - 2)))
            mw_rect = (1, 1, self.GRID_SIZE * 6 - 2, self.GRID_SIZE * (self.disp_size_y - 2) - 2)
            self.pg.pygame.draw.rect(self.stats_win, self.res_man.colors['frm_normal'], mw_rect, self.pg.APP_SCALE)
            # Drawing stats.
            self.stats_text.draw(self.stats_win)
            self.items_text.draw(self.stats_win)
            self.effects_text.draw(self.stats_win)
            # Recreating text surfaces with numbers.
            if self.pc:
                text.Text(self.pg, self.res_man,
                                            ('%s/%s' % (self.pc.hp, charts.char_hp[self.pc.hp_lvl]),),
                                            ((88, 16),), self.stat_col(self.pc.hp, charts.char_hp[self.pc.hp_lvl]),
                                            align=2).draw(self.stats_win)
                text.Text(self.pg, self.res_man,
                                            (str(self.pc.pow_lvl + 1),),
                                            ((88, 24),), self.res_man.colors['fnt_normal'], align=2).draw(self.stats_win)
                text.Text(self.pg, self.res_man,
                                            ('%s/%s' % (self.pc.mag, charts.char_mag[self.pc.mag_lvl]),),
                                            ((88, 32),), self.res_man.colors['fnt_normal'], align=2).draw(self.stats_win)
                text.Text(self.pg, self.res_man,
                                            (str(self.pc.score).zfill(8),),
                                            ((88, 48),), self.res_man.colors['fnt_normal'], align=2).draw(self.stats_win)
            # Drawing effects:
            if 'poison' in self.pc.effects:
                self.stats_win.blit(self.sprites['poison'], (16, 72))
            if 'invisible' in self.pc.effects:
                self.stats_win.blit(self.sprites['invisible'], (40, 72))
            if 'timestop' in self.pc.effects:
                self.stats_win.blit(self.sprites['timestop'], (72, 72))
            # Drawing inventory:
            for i in range(0, len(self.pc.inventory)):
                dest = (16 + (i % 3) * (self.GRID_SIZE * 1.5), 112 + (i // 3) * (self.GRID_SIZE * 1.5))
                self.stats_win.blit(self.pc.inventory[i][2], dest)
                text.Text(self.pg, self.res_man,
                          (str(i+1),),
                          (dest,), self.res_man.colors['fnt_normal'], align=0).draw(self.stats_win)
            self.sw_redraw = False
        surface.blit(self.message_win, self.mw_xy)
        surface.blit(self.stats_win, self.sw_xy)

    def stat_col(self, stat, max_stat):
        colors = (self.res_man.colors['fnt_normal'],
                  self.res_man.colors['fnt_accent'],
                  self.res_man.colors['fnt_attent'])
        if stat <= max_stat //4:
            return colors[2]
        if stat < max_stat //2:
            return colors[1]
        return colors[0]

    def sprites_create(self):
        sprites = {
            'poison': sprite.Sprite(self.pg, self.res_man,
                          ((0, (112, 0, 16, 16)),),('0'),((0, 0),),size=(16, 16)).sprite_surface,
            'invisible': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (128, 0, 16, 16)),), ('0'), ((0, 0),), size=(16, 16)).sprite_surface,
            'timestop': sprite.Sprite(self.pg, self.res_man,
                                       ((0, (144, 0, 16, 16)),), ('0'), ((0, 0),), size=(16, 16)).sprite_surface
        }
        return sprites
