# Game block with labyrinth gameplay. Importing os module for paths.
import os, random, math
# Importing levels.
from library import drop, build
from rules import mazes, texts, charts
from objects import sprite, text, hud, mob, particle


class Cave:
    def __init__(self, pg, res_man):
        # Receiving link to pygame object, setup settings and resources manager.
        self.pg = pg
        self.res_man = res_man
        self.counter0 = None
        # Setting the offset and grid size for maze displaying.
        self.GRID_SIZE = 16
        self.offset_x = self.GRID_SIZE * 5
        self.offset_y = self.GRID_SIZE * -1
        # Radius around player character in which cave will be drawn.
        self.DISP_SIZE_X = 21
        self.DISP_SIZE_Y = 14
        # Flag for main loop control. Setting False breaks the loop and finishes the block.
        self.playcard = None
        # Declaring level variables.
        self.maze_name = None
        self.maze_size = None
        self.maze_body = None
        self.maze_objects = None
        self.maze_flags = None
        self.maze_actors = None
        self.maze_memos = None
        self.lvl = None
        self.pc = None
        self.pc_start_x = None
        self.pc_start_y = None
        self.mobs = None
        self.particles = []
        self.cave_anims = None
        # Declaring variables for HUD surfaces.
        self.gui = hud.Hud(pg, res_man, self.GRID_SIZE, self.DISP_SIZE_X, self.DISP_SIZE_Y)
        self.say_input = False
        self.dm_done = True
        self.checks_done = True
        # Flag to redraw the surface with graphics.
        self.active = True
        self.redraw = True
        self.pc_vision = None

    def start(self, playcard):
        self.active = True
        self.redraw = True
        self.gui.mw_redraw = True
        self.gui.sw_redraw = True
        if 'lvl' not in playcard or 'pc' not in playcard:
            self.active = False
            return
        # Getting player character from playcard.
        self.pc = playcard['pc']
        self.lvl = playcard['lvl']
        # Updating link to pc object for hud
        self.gui.pc = self.pc
        # Retrieving maze map and name from rulebook.
        try:
            self.maze_name, self.maze_size, self.maze_body, self.maze_flags, object_list, self.maze_memos, mob_list = self.maze_load(self.lvl)
        except TypeError:
            # if there is no level with provided index, creating playcard for game over block.
            self.playcard = {
                'run': 2,  # demo block index
                'pc': self.pc,
                'demo': 0,
                'lvl': self.lvl - 1
            }
            if self.inv_check('m_flask'):
                self.playcard['demo'] = 3
                self.pc.score += charts.flask_reward
            self.active = False
            self.redraw = False
            return
        # Creating a maze body double for actors.
        self.maze_actors = bytearray(len(self.maze_body))
        self.maze_objects = bytearray(len(self.maze_body))
        # Spawning monsters.
        self.mobs = []
        for mb in mob_list:
            self.spawn_mob(mb[2], (mb[0], mb[1]))
        for obj in object_list:
            self.maze_objects[self.xy_to_pos(self.maze_size, (obj[0], obj[1]))] = obj[2]
        self.maze_diff = charts.encounters[min(self.lvl, len(charts.encounters) - 1)]['diff']
        # Finding the starting point for player character.
        # Setting x and y for player character.
        self.pc.x, self.pc.y = self.pc_start_x, self.pc_start_y = self.find_byte(self.maze_flags, self.maze_size, mazes.flags['start'], n=1)
        self.maze_actors[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 2
        # Creating sprites and animations.
        self.sprites_tiles, self.sprites_objects, self.sprites_anims = self.sprites_create()
        self.cave_anims = self.anims_create(self.sprites_anims)
        self.pc_vision_check()

        """
        if charts.random_spawns:
            while self.maze_diff > 0:
                self.roll_mob()
        """

    def tick(self):
        # Setting 'active' flag to 'False' to exit main loop.
        # Reducing offset of a player character if it is not zero.
        if self.pc.offset_x > 0:
            self.pc.offset_x -= self.pc.sp
            self.redraw = True
        elif self.pc.offset_x < 0:
            self.pc.offset_x += self.pc.sp
            self.redraw = True
        elif self.pc.offset_y > 0:
            self.pc.offset_y -= self.pc.sp
            self.redraw = True
        elif self.pc.offset_y < 0:
            self.pc.offset_y += self.pc.sp
            self.redraw = True

        if self.pc.offset_x == 0 and self.pc.offset_y == 0 and not self.checks_done:
            self.check_pc()

        if not self.dm_done:
            self.dm()

        if self.pc.mov_dir == 1:
            self.pc_move(0, -1)
        elif self.pc.mov_dir == 2:
            self.pc_move(1, 0)
        elif self.pc.mov_dir == 3:
            self.pc_move(0, 1)
        elif self.pc.mov_dir == 4:
            self.pc_move(-1, 0)

        # Working with mobs
        for mb in self.mobs:
            # Reducing offset of a mob if it is not zero.
            if mb.offset_x > 0:
                mb.offset_x -= mb.sp
                self.redraw = True
            elif mb.offset_x < 0:
                mb.offset_x += mb.sp
                self.redraw = True
            elif mb.offset_y > 0:
                mb.offset_y -= mb.sp
                self.redraw = True
            elif mb.offset_y < 0:
                mb.offset_y += mb.sp
                self.redraw = True

            if mb.mov_dir == 1:
                self.mob_move(mb, 0, -1)
            elif mb.mov_dir == 2:
                self.mob_move(mb, 1, 0)
            elif mb.mov_dir == 3:
                self.mob_move(mb, 0, 1)
            elif mb.mov_dir == 4:
                self.mob_move(mb, -1, 0)

        # Working with particles.
        for i in range(0, len(self.particles)):
            try:
                p_resp = self.particles[i].tick()
                if p_resp == 0:
                    del self.particles[i]
                    i -= 1
                if p_resp != 1:
                    self.redraw = True
            except IndexError:
                continue

    def draw(self, surface):
        # Drawing the block graphics onto the pygame display.
        if not self.redraw:
            return
        # Clear screen
        surface.fill(self.res_man.colors['bg'],
                     (self.GRID_SIZE * 6, 0, 400 - self.GRID_SIZE * 6, self.GRID_SIZE * (self.DISP_SIZE_Y - 2))
                     )
        # Drawing the cave.
        """
        for i in range(0, self.DISP_SIZE_Y):
            for j in range(0, self.DISP_SIZE_X):
                byte_x = self.pc.x - self.DISP_SIZE_X // 2 + j
                byte_y = self.pc.y - self.DISP_SIZE_Y // 2 + i
                if byte_x < 0 or byte_x >= self.maze_size[0] or byte_y < 0 or byte_y > self.maze_size[1]:
                    continue
                try:
                    byte = self.maze_body[self.xy_to_pos(self.maze_size, (byte_x, byte_y))]
                    surface.blit(
                        self.sprites_tiles[byte].sprite_surface,
                        (j * self.GRID_SIZE + self.offset_x - self.pc.offset_x,
                         i * self.GRID_SIZE + self.offset_y - self.pc.offset_y)
                    )
                    # drawing objects
                    byte = self.maze_objects[self.xy_to_pos(self.maze_size, (byte_x, byte_y))]
                    if byte == 0:
                        continue
                    surface.blit(
                        self.sprites_objects[byte].sprite_surface,
                        (j * self.GRID_SIZE + self.offset_x - self.pc.offset_x,
                         i * self.GRID_SIZE + self.offset_y - self.pc.offset_y)
                    )
                except KeyError:
                    continue
                except IndexError:
                    continue
        """
        for vis_x, vis_y in self.pc_vision:
            draw_x = (vis_x - (self.pc.x - self.DISP_SIZE_X // 2)) * self.GRID_SIZE + self.offset_x - self.pc.offset_x
            draw_y = (vis_y - (self.pc.y - self.DISP_SIZE_Y // 2)) * self.GRID_SIZE + self.offset_y - self.pc.offset_y

            byte = self.maze_body[self.xy_to_pos(self.maze_size, (vis_x, vis_y))]
            if byte:
                surface.blit(self.sprites_tiles[byte].sprite_surface, (draw_x, draw_y))

            byte = self.maze_objects[self.xy_to_pos(self.maze_size, (vis_x, vis_y))]
            if byte:
                surface.blit(self.sprites_objects[byte].sprite_surface, (draw_x, draw_y))

        # Drawing the mobs.
        for mb in self.mobs:
            """
            if self.pc.x - self.DISP_SIZE_X // 2 < mb.x < self.pc.x + self.DISP_SIZE_X // 2 \
                    and self.pc.y - self.DISP_SIZE_Y // 2 < mb.y < self.pc.y + self.DISP_SIZE_Y // 2:
            """
            mb_x = (mb.x - (self.pc.x - self.DISP_SIZE_X // 2)) * self.GRID_SIZE + mb.offset_x + self.offset_x - self.pc.offset_x
            mb_y = (mb.y - (self.pc.y - self.DISP_SIZE_Y // 2)) * self.GRID_SIZE + mb.offset_y + self.offset_y - self.pc.offset_y
            if (mb.x, mb.y) in self.pc_vision:
                surface.blit(self.get_frame(mb, self.cave_anims[mb.ani_name]), (mb_x,mb_y))
                if mb.alert:
                    surface.blit(self.sprites_tiles['mb_alert'].sprite_surface, (mb_x + 8, mb_y))
                elif mb.turn_ind:
                    surface.blit(self.sprites_tiles['mb_turn'].sprite_surface, (mb_x + 8, mb_y))

        # Drawing the player character.
        if self.pc.vis:
            surface.blit(self.get_frame(self.pc, self.cave_anims[self.pc.ani_name]),
                         (self.DISP_SIZE_X // 2 * self.GRID_SIZE + self.offset_x,
                          self.DISP_SIZE_Y // 2 * self.GRID_SIZE + self.offset_y))

        # Drawing particles.
        for pt in self.particles:
            """
            if self.pc.x - self.DISP_SIZE_X // 2 < pt.x < self.pc.x + self.DISP_SIZE_X // 2 \
                    and self.pc.y - self.DISP_SIZE_Y // 2 < pt.y < self.pc.y + self.DISP_SIZE_Y // 2:
            """
            if (pt.x, pt.y) in self.pc_vision:
                surface.blit(pt.anim_frames[pt.frame_index],
                             ((pt.x - (
                                     self.pc.x - self.DISP_SIZE_X // 2)) * self.GRID_SIZE + self.offset_x - self.pc.offset_x,
                              (pt.y - (
                                      self.pc.y - self.DISP_SIZE_Y // 2)) * self.GRID_SIZE + self.offset_y - self.pc.offset_y))

        # Drawing a message window background.
        self.gui.draw(surface)

    def finish(self):
        # Concluding the block before returning playcard to the playcards loop in conr.py
        self.pc = None
        self.sprites_objects = None
        self.sprites_tiles = None
        self.sprites_anims = None
        self.cave_anims = None
        self.mobs.clear()
        self.particles.clear()
        self.lvl = None
        self.maze_body = None

    def events(self, event):
        if self.say_input:
            if event.type == self.pg.pygame.KEYDOWN:
                if 62 < event.key < 91 or 96 < event.key < 123 or 41 < event.key < 58 or event.key in [32, 33, 58, 63]:
                    self.pc.log[-1][0] += chr(event.key)
                    self.pc.log[-1][0] = self.pc.log[-1][0][:36]
                    self.pg.audio.sound('cluck')
                elif event.key == 8 and len(self.pc.log[-1][0]) > 1:
                    self.pc.log[-1][0] = self.pc.log[-1][0][:-1]
                    self.pg.audio.sound('cluck')
                elif event.key == 13:
                    self.comprehend(self.pc.log[-1][0][1:])
                    self.say_input = False
                    self.pg.audio.sound('paper')
                elif event.key == self.pg.controls['exit']:
                    self.pc.log[-1] = ('-NOTHING-', self.res_man.colors['fnt_muted'])
                    self.say_input = False
                self.gui.mw_redraw = True
                self.redraw = True
            return

        if event.type == self.pg.pygame.KEYDOWN or event.type == self.pg.pygame.KEYUP:
            keys = self.pg.pygame.key.get_pressed()
            if keys[self.pg.controls['up']]:
                self.pc.mov_dir = 1
            elif keys[self.pg.controls['right']]:
                self.pc.mov_dir = 2
            elif keys[self.pg.controls['down']]:
                self.pc.mov_dir = 3
            elif keys[self.pg.controls['left']]:
                self.pc.mov_dir = 4
            else:
                self.pc.mov_dir = 0

        if event.type == self.pg.pygame.KEYDOWN:
            if event.key == self.pg.controls['exit']:
                self.playcard = {
                    'run': 2,
                    'pc': self.pc,
                    'lvl': self.lvl,
                    'demo': 0
                }
                self.active = False
            elif event.key == self.pg.controls['say']:
                self.log(texts.game_text['cave_say'], self.res_man.colors['fnt_normal'])
                self.pc.log.append([':', self.res_man.colors['fnt_accent']])
                self.say_input = True
                self.gui.mw_redraw = True
                self.redraw = True
            elif event.key == self.pg.controls['wait']:
                self.log(texts.game_text['cave_wait'], self.res_man.colors['fnt_normal'])
                self.check_pc()
                self.dm()
            elif event.key == self.pg.controls['spell1'] and len(self.pc.inventory) > 0:
                if self.use_item(self.pc.inventory[0][0], self.pc.inventory[0][1]):
                    del self.pc.inventory[0]
                    self.gui.sw_redraw = True
                    self.redraw = True
                self.check_pc()
                self.dm()
            elif event.key == self.pg.controls['spell2'] and len(self.pc.inventory) > 1:
                if self.use_item(self.pc.inventory[1][0], self.pc.inventory[1][1]):
                    del self.pc.inventory[1]
                    self.gui.sw_redraw = True
                    self.redraw = True
                self.check_pc()
                self.dm()
            elif event.key == self.pg.controls['spell3'] and len(self.pc.inventory) > 2:
                if self.use_item(self.pc.inventory[2][0], self.pc.inventory[2][1]):
                    del self.pc.inventory[2]
                    self.gui.sw_redraw = True
                    self.redraw = True
                self.check_pc()
                self.dm()
            elif event.key == self.pg.controls['spell4'] and len(self.pc.inventory) > 3:
                if self.use_item(self.pc.inventory[3][0], self.pc.inventory[3][1]):
                    del self.pc.inventory[3]
                    self.gui.sw_redraw = True
                    self.redraw = True
                self.check_pc()
                self.dm()
            elif event.key == self.pg.controls['spell5'] and len(self.pc.inventory) > 4:
                if self.use_item(self.pc.inventory[4][0], self.pc.inventory[4][1]):
                    del self.pc.inventory[4]
                    self.gui.sw_redraw = True
                    self.redraw = True
                self.check_pc()
                self.dm()
            elif event.key == self.pg.controls['spell6'] and len(self.pc.inventory) > 5:
                if self.use_item(self.pc.inventory[5][0], self.pc.inventory[5][1]):
                    del self.pc.inventory[5]
                    self.gui.sw_redraw = True
                    self.redraw = True
                self.check_pc()
                self.dm()
            elif event.key == self.pg.controls['spell7'] and len(self.pc.inventory) > 6:
                if self.use_item(self.pc.inventory[6][0], self.pc.inventory[6][1]):
                    del self.pc.inventory[6]
                    self.gui.sw_redraw = True
                    self.redraw = True
                self.check_pc()
                self.dm()
            elif event.key == self.pg.controls['spell8'] and len(self.pc.inventory) > 7:
                if self.use_item(self.pc.inventory[7][0], self.pc.inventory[7][1]):
                    del self.pc.inventory[7]
                    self.gui.sw_redraw = True
                    self.redraw = True
                self.check_pc()
                self.dm()
            elif event.key == self.pg.controls['spell9'] and len(self.pc.inventory) > 8:
                if self.use_item(self.pc.inventory[8][0], self.pc.inventory[8][1]):
                    del self.pc.inventory[8]
                    self.gui.sw_redraw = True
                    self.redraw = True
                self.check_pc()
                self.dm()

    def maze_load(self, level_index):
        # Trying to load bytes sequence from file.
        try:
            maze_bytes = open(os.path.join('data', str(level_index) + '.cav'), 'rb')
        except FileNotFoundError:
            print('Can not find cave binary data.')
            return
        """
        #try:
        maze = self.maze_build(32, 32)
        self.maze_save(level_index, 'Builder 1', maze)
        # Reopening maze file for reading.
        maze_bytes = open(os.path.join('data', str(level_index) + '.cav'), 'rb')
        except IndexError:
        except IndexError:
            print('Can not find cave string data in rules.')
            return
        except FileNotFoundError:
            print('Can not create cave binary data.')
            return"""
        # Getting maze
        # Reading maze width and height.
        maze_width, maze_height = maze_bytes.read(2)
        # Calculating maze length in bytes.
        maze_len = maze_width * maze_height
        # Reading maze bytes sequence.
        maze_body = bytearray(maze_bytes.read(maze_len))
        maze_flags = bytearray(maze_bytes.read(maze_len))
        maze_obj_total = maze_bytes.read(1)[0]
        obj_list = []
        for i in range(0, maze_obj_total):
            obj_x, obj_y = maze_bytes.read(2)
            obj_byte = maze_bytes.read(1)[0]
            obj_list.append(
                (obj_x, obj_y, obj_byte)
            )
        maze_mobs_total = maze_bytes.read(1)[0]
        mobs_list = []
        for i in range(0, maze_mobs_total):
            mob_x, mob_y = maze_bytes.read(2)
            mob_byte = maze_bytes.read(1)[0]
            if mob_byte == 0:
                continue
            mobs_list.append(
                (mob_x, mob_y, mazes.mobs[mob_byte])
            )
        maze_memos_total = maze_bytes.read(1)[0]
        maze_memos = {}
        for i in range(0, maze_memos_total):
            memo_x, memo_y = maze_bytes.read(2)
            memo_len = maze_bytes.read(1)[0]
            memo_text = maze_bytes.read(memo_len).decode('utf-8')
            memo_color_r, memo_color_g, memo_color_b = maze_bytes.read(3)
            maze_memos[str(memo_x).zfill(3) + str(memo_y).zfill(3)] = (
                memo_text, (memo_color_r, memo_color_g, memo_color_b)
            )
        # Reading and decoding maze name.
        maze_name_len = maze_bytes.read(1)[0]
        maze_name = maze_bytes.read(maze_name_len).decode('utf-8')
        # Close file.
        maze_bytes.close()
        # Returning maze name and bytes sequence.
        return maze_name, (maze_width, maze_height), maze_body, maze_flags, obj_list, maze_memos, mobs_list

    def find_byte(self, byte_seq, size, byte, n=0):
        xy_list = []
        for i in range(0, len(byte_seq)):
            if byte_seq[i] == byte:
                xy = self.pos_to_xy(size, i)
                xy_list.append(xy)
        if len(xy_list) == 0:
            return
        elif n == 1:
            return xy_list[0]
        elif n == 0:
            return xy_list
        else:
            return xy_list[:n]

    def pos_to_xy(self, maze_size, pos):
        y = pos // maze_size[0]
        x = pos % maze_size[0]
        return x, y

    def xy_to_pos(self, maze_size, xy):
        pos = xy[1] * maze_size[0] + xy[0]
        return pos

    def sprites_create(self):
        sprites_tiles = {
            mazes.tiles['wall_stone']: sprite.Sprite(self.pg, self.res_man, ((0, (0, 32, 16, 16)),), ('0',),
                                                      size=(16, 16)),
            mazes.tiles['wall_plate']: sprite.Sprite(self.pg, self.res_man, ((0, (112, 48, 16, 16)),), ('0',),
                                                     size=(16, 16)),
            mazes.tiles['wall_tree']: sprite.Sprite(self.pg, self.res_man, ((0, (48, 48, 16, 16)),), ('0',),
                                                     size=(16, 16)),
            mazes.tiles['floor_stone']: sprite.Sprite(self.pg, self.res_man, ((0, (16, 16, 16, 16)),), ('0',),
                                                       size=(16, 16)),
            mazes.tiles['floor_plate']: sprite.Sprite(self.pg, self.res_man, ((0, (128, 48, 16, 16)),), ('0',),
                                                     size=(16, 16)),
            mazes.tiles['floor_grass']: sprite.Sprite(self.pg, self.res_man, ((0, (64, 48, 16, 16)),), ('0',),
                                                      size=(16, 16)),
            mazes.tiles['hazard_spikes']: sprite.Sprite(self.pg, self.res_man, ((0, (0, 0, 16, 16)),), ('0',),
                                                        size=(16, 16)),
            mazes.tiles['stairs_down']: sprite.Sprite(self.pg, self.res_man, ((0, (176, 32, 16, 16)),), ('0',),
                                                       size=(16, 16)),
            mazes.tiles['stairs_up']: sprite.Sprite(self.pg, self.res_man, ((0, (176, 48, 16, 16)),), ('0',),
                                                     size=(16, 16)),
            mazes.tiles['door_wood']: sprite.Sprite(self.pg, self.res_man,
                                                     ((0, (16, 32, 16, 16)),),
                                                     ('0',), size=(16, 16)),
            mazes.tiles['door_iron']: sprite.Sprite(self.pg, self.res_man,
                                                     ((0, (16, 48, 16, 16)),),
                                                     ('0',), size=(16, 16)),
            mazes.tiles['port_stone']: sprite.Sprite(self.pg, self.res_man,
                                                      ((0, (32, 48, 16, 16)),),
                                                      ('0',), size=(16, 16)),
            mazes.tiles['pit_hole']: sprite.Sprite(self.pg, self.res_man,
                                                    ((0, (0, 48, 16, 16)),),
                                                    ('0',), size=(16, 16)),
            mazes.tiles['pit_stone']: sprite.Sprite(self.pg, self.res_man,
                                                   ((0, (96, 48, 16, 16)),),
                                                   ('0',), size=(16, 16)),
            'mb_turn': sprite.Sprite(self.pg, self.res_man,
                                                    ((0, (216, 248, 8, 8)),),
                                                    ('0',), size=(8, 8)),
            'mb_alert': sprite.Sprite(self.pg, self.res_man,
                                                     ((0, (208, 248, 8, 8)),),
                                                     ('0',), size=(8, 8)),
        }
        sprites_objects = {
            mazes.objects['memo_page']: sprite.Sprite(self.pg, self.res_man,
                                                    ((0, (160, 32, 16, 16)),),
                                                    ('0',), size=(16, 16)),
            mazes.objects['mov_stone']: sprite.Sprite(self.pg, self.res_man, ((0, (0, 16, 16, 16)),), ('0',),
                                                      size=(16, 16)),
            mazes.objects['hp_up']: sprite.Sprite(self.pg, self.res_man,
                                                   ((0, (112, 16, 16, 16)),),
                                                   ('0',), size=(16, 16)),
            mazes.objects['pow_up']: sprite.Sprite(self.pg, self.res_man,
                                                    ((0, (128, 16, 16, 16)),),
                                                    ('0',), size=(16, 16)),
            mazes.objects['mag_up']: sprite.Sprite(self.pg, self.res_man,
                                                    ((0, (144, 16, 16, 16)),),
                                                        ('0',), size=(16, 16)),
            mazes.objects['ptn_blue']: sprite.Sprite(self.pg, self.res_man,
                                                      ((0, (160, 16, 16, 16)),),
                                                      ('0',), size=(16, 16)),
            mazes.objects['ptn_red']: sprite.Sprite(self.pg, self.res_man,
                                                     ((0, (176, 16, 16, 16)),),
                                                     ('0',), size=(16, 16)),
            mazes.objects['ptn_yellow']: sprite.Sprite(self.pg, self.res_man,
                                                        ((0, (144, 48, 16, 16)),),
                                                        ('0',), size=(16, 16)),
            mazes.objects['key_gold']: sprite.Sprite(self.pg, self.res_man,
                                                      ((0, (48, 32, 16, 16)),),
                                                      ('0',), size=(16, 16)),
            mazes.objects['slvr_blade']: sprite.Sprite(self.pg, self.res_man,
                                                        ((0, (176, 0, 16, 16)),),
                                                        ('0',), size=(16, 16)),
            mazes.objects['m_flask']: sprite.Sprite(self.pg, self.res_man,
                                                     ((0, (160, 0, 16, 16)),),
                                                     ('0',), size=(16, 16)),
            mazes.objects['gold']: sprite.Sprite(self.pg, self.res_man,
                                                  ((0, (80, 48, 16, 16)),),
                                                  ('0',), size=(16, 16)),
            mazes.objects['sp_unknown']: sprite.Sprite(self.pg, self.res_man,
                                                        ((0, (160, 48, 16, 16)),),
                                                        ('0',), size=(16, 16)),
            mazes.objects['chest']: sprite.Sprite(self.pg, self.res_man,
                                                       ((0, (64, 32, 16, 16)),),
                                                       ('0',), size=(16, 16)),
            # Spells.
            mazes.objects['sp_disint']: sprite.Sprite(self.pg, self.res_man, ((0, (32, 0, 16, 16)),), ('0',),
                                                           size=(16, 16)),
            mazes.objects['sp_barrier']: sprite.Sprite(self.pg, self.res_man, ((0, (48, 0, 16, 16)),), ('0',),
                                                            size=(16, 16)),
            mazes.objects['sp_dispel']: sprite.Sprite(self.pg, self.res_man, ((0, (64, 0, 16, 16)),), ('0',),
                                                           size=(16, 16)),
            mazes.objects['sp_heal']: sprite.Sprite(self.pg, self.res_man, ((0, (80, 0, 16, 16)),), ('0',),
                                                         size=(16, 16)),
            mazes.objects['sp_stop']: sprite.Sprite(self.pg, self.res_man, ((0, (96, 0, 16, 16)),), ('0',),
                                                         size=(16, 16)),
            mazes.objects['sp_kill']: sprite.Sprite(self.pg, self.res_man, ((0, (32, 16, 16, 16)),), ('0',),
                                                         size=(16, 16)),
            mazes.objects['sp_warp']: sprite.Sprite(self.pg, self.res_man, ((0, (48, 16, 16, 16)),), ('0',),
                                                         size=(16, 16)),
            mazes.objects['sp_petrify']: sprite.Sprite(self.pg, self.res_man, ((0, (64, 16, 16, 16)),), ('0',),
                                                            size=(16, 16)),
            mazes.objects['sp_turn']: sprite.Sprite(self.pg, self.res_man, ((0, (80, 16, 16, 16)),), ('0',),
                                                         size=(16, 16)),
            mazes.objects['sp_invis']: sprite.Sprite(self.pg, self.res_man, ((0, (96, 16, 16, 16)),), ('0',),
                                                          size=(16, 16))
        }

        sprites_anims = {
            'pc_s': sprite.Sprite(self.pg, self.res_man,
                                  ((0, (192, 0, 16, 16)),),
                                  ('0',), size=(16, 16)),
            'pc_n': sprite.Sprite(self.pg, self.res_man,
                                  ((0, (208, 0, 16, 16)),),
                                  ('0',), size=(16, 16)),
            'pc_e1': sprite.Sprite(self.pg, self.res_man,
                                   ((0, (224, 0, 16, 16)),),
                                   ('0',), size=(16, 16)),
            'pc_e2': sprite.Sprite(self.pg, self.res_man,
                                   ((0, (240, 0, 16, 16)),),
                                   ('0',), size=(16, 16)),
            'invis_s': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (192, 176, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'invis_n': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (208, 176, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'invis_e1': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (224, 176, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'invis_e2': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (240, 176, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'rat_s': sprite.Sprite(self.pg, self.res_man,
                                   ((0, (192, 16, 16, 16)),),
                                   ('0',), size=(16, 16)),
            'rat_n': sprite.Sprite(self.pg, self.res_man,
                                   ((0, (208, 16, 16, 16)),),
                                   ('0',), size=(16, 16)),
            'rat_e1': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (224, 16, 16, 16)),),
                                    ('0',), size=(16, 16)),
            'rat_e2': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (240, 16, 16, 16)),),
                                    ('0',), size=(16, 16)),
            'snake_s': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (192, 32, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'snake_n': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (208, 32, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'snake_e1': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (224, 32, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'snake_e2': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (240, 32, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'spider_s': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (192, 48, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'spider_n': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (208, 48, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'spider_e1': sprite.Sprite(self.pg, self.res_man,
                                       ((0, (224, 48, 16, 16)),),
                                       ('0',), size=(16, 16)),
            'spider_e2': sprite.Sprite(self.pg, self.res_man,
                                       ((0, (240, 48, 16, 16)),),
                                       ('0',), size=(16, 16)),
            'muss_s': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (192, 64, 16, 16)),),
                                    ('0',), size=(16, 16)),
            'muss_n': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (208, 64, 16, 16)),),
                                    ('0',), size=(16, 16)),
            'muss_e1': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (224, 64, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'muss_e2': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (240, 64, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'goblin_s': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (192, 80, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'goblin_n': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (208, 80, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'goblin_e1': sprite.Sprite(self.pg, self.res_man,
                                       ((0, (224, 80, 16, 16)),),
                                       ('0',), size=(16, 16)),
            'goblin_e2': sprite.Sprite(self.pg, self.res_man,
                                       ((0, (240, 80, 16, 16)),),
                                       ('0',), size=(16, 16)),
            'skeleton_s': sprite.Sprite(self.pg, self.res_man,
                                        ((0, (192, 96, 16, 16)),),
                                        ('0',), size=(16, 16)),
            'skeleton_n': sprite.Sprite(self.pg, self.res_man,
                                        ((0, (208, 96, 16, 16)),),
                                        ('0',), size=(16, 16)),
            'skeleton_e1': sprite.Sprite(self.pg, self.res_man,
                                         ((0, (224, 96, 16, 16)),),
                                         ('0',), size=(16, 16)),
            'skeleton_e2': sprite.Sprite(self.pg, self.res_man,
                                         ((0, (240, 96, 16, 16)),),
                                         ('0',), size=(16, 16)),
            'orcus_s': sprite.Sprite(self.pg, self.res_man,
                                   ((0, (192, 112, 16, 16)),),
                                   ('0',), size=(16, 16)),
            'orcus_n': sprite.Sprite(self.pg, self.res_man,
                                   ((0, (208, 112, 16, 16)),),
                                   ('0',), size=(16, 16)),
            'orcus_e1': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (224, 112, 16, 16)),),
                                    ('0',), size=(16, 16)),
            'orcus_e2': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (240, 112, 16, 16)),),
                                    ('0',), size=(16, 16)),
            'lich_s': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (192, 128, 16, 16)),),
                                    ('0',), size=(16, 16)),
            'lich_n': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (208, 128, 16, 16)),),
                                    ('0',), size=(16, 16)),
            'lich_e1': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (224, 128, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'lich_e2': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (240, 128, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'daemon_s': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (192, 144, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'daemon_n': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (208, 144, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'daemon_e1': sprite.Sprite(self.pg, self.res_man,
                                       ((0, (224, 144, 16, 16)),),
                                       ('0',), size=(16, 16)),
            'daemon_e2': sprite.Sprite(self.pg, self.res_man,
                                       ((0, (240, 144, 16, 16)),),
                                       ('0',), size=(16, 16)),
            'ghost_s': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (192, 160, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'ghost_n': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (208, 160, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'ghost_e1': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (224, 160, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'ghost_e2': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (240, 160, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'human_s': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (192, 192, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'human_n': sprite.Sprite(self.pg, self.res_man,
                                     ((0, (208, 192, 16, 16)),),
                                     ('0',), size=(16, 16)),
            'human_e1': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (224, 192, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'human_e2': sprite.Sprite(self.pg, self.res_man,
                                      ((0, (240, 192, 16, 16)),),
                                      ('0',), size=(16, 16)),
            'wrath_s': sprite.Sprite(self.pg, self.res_man,
                                   ((0, (192, 208, 16, 16)),),
                                   ('0',), size=(16, 16)),
            'wrath_n': sprite.Sprite(self.pg, self.res_man,
                                   ((0, (208, 208, 16, 16)),),
                                   ('0',), size=(16, 16)),
            'wrath_e1': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (224, 208, 16, 16)),),
                                    ('0',), size=(16, 16)),
            'wrath_e2': sprite.Sprite(self.pg, self.res_man,
                                    ((0, (240, 208, 16, 16)),),
                                    ('0',), size=(16, 16)),
            'hit1': sprite.Sprite(self.pg, self.res_man,
                                  (
                                      (0, (96, 32, 16, 16)),  # Setting tile 0
                                  ),
                                  ('0',),
                                  size=(16, 16)
                                  ),
            'hit2': sprite.Sprite(self.pg, self.res_man,
                                  (
                                      (0, (112, 32, 16, 16)),  # Setting tile 0
                                  ),
                                  ('0',),
                                  size=(16, 16)
                                  ),
            'hit3': sprite.Sprite(self.pg, self.res_man,
                                  (
                                      (0, (128, 32, 16, 16)),  # Setting tile 0
                                  ),
                                  ('0',),
                                  size=(16, 16)
                                  ),
            'hit4': sprite.Sprite(self.pg, self.res_man,
                                  (
                                      (0, (144, 32, 16, 16)),  # Setting tile 0
                                  ),
                                  ('0',),
                                  size=(16, 16)
                                  ),
        }
        return sprites_tiles, sprites_objects, sprites_anims

    def anims_create(self, sprites):
        cave_anims = {
            'pc': (sprites['pc_s'].sprite_surface,
                   sprites['pc_n'].sprite_surface,
                   sprites['pc_e1'].sprite_surface,
                   sprites['pc_e2'].sprite_surface),
            'invis': (sprites['invis_s'].sprite_surface,
                      sprites['invis_n'].sprite_surface,
                      sprites['invis_e1'].sprite_surface,
                      sprites['invis_e2'].sprite_surface),
            'rat': (sprites['rat_s'].sprite_surface,
                    sprites['rat_n'].sprite_surface,
                    sprites['rat_e1'].sprite_surface,
                    sprites['rat_e2'].sprite_surface),
            'snake': (sprites['snake_s'].sprite_surface,
                      sprites['snake_n'].sprite_surface,
                      sprites['snake_e1'].sprite_surface,
                      sprites['snake_e2'].sprite_surface),
            'spider': (sprites['spider_s'].sprite_surface,
                       sprites['spider_n'].sprite_surface,
                       sprites['spider_e1'].sprite_surface,
                       sprites['spider_e2'].sprite_surface),
            'muss': (sprites['muss_s'].sprite_surface,
                     sprites['muss_n'].sprite_surface,
                     sprites['muss_e1'].sprite_surface,
                     sprites['muss_e2'].sprite_surface),
            'goblin': (sprites['goblin_s'].sprite_surface,
                       sprites['goblin_n'].sprite_surface,
                       sprites['goblin_e1'].sprite_surface,
                       sprites['goblin_e2'].sprite_surface),
            'skeleton': (sprites['skeleton_s'].sprite_surface,
                         sprites['skeleton_n'].sprite_surface,
                         sprites['skeleton_e1'].sprite_surface,
                         sprites['skeleton_e2'].sprite_surface),
            'orcus': (sprites['orcus_s'].sprite_surface,
                    sprites['orcus_n'].sprite_surface,
                    sprites['orcus_e1'].sprite_surface,
                    sprites['orcus_e2'].sprite_surface),
            'lich': (sprites['lich_s'].sprite_surface,
                     sprites['lich_n'].sprite_surface,
                     sprites['lich_e1'].sprite_surface,
                     sprites['lich_e2'].sprite_surface),
            'daemon': (sprites['daemon_s'].sprite_surface,
                       sprites['daemon_n'].sprite_surface,
                       sprites['daemon_e1'].sprite_surface,
                       sprites['daemon_e2'].sprite_surface),
            'ghost': (sprites['ghost_s'].sprite_surface,
                      sprites['ghost_n'].sprite_surface,
                      sprites['ghost_e1'].sprite_surface,
                      sprites['ghost_e2'].sprite_surface),
            'hit': (sprites['hit1'].sprite_surface,
                    sprites['hit2'].sprite_surface,
                    sprites['hit3'].sprite_surface,
                    sprites['hit4'].sprite_surface),
            'human': (sprites['human_s'].sprite_surface,
                      sprites['human_n'].sprite_surface,
                      sprites['human_e1'].sprite_surface,
                      sprites['human_e2'].sprite_surface),
            'wrath': (sprites['wrath_s'].sprite_surface,
                      sprites['wrath_n'].sprite_surface,
                      sprites['wrath_e1'].sprite_surface,
                      sprites['wrath_e2'].sprite_surface),
        }
        return cave_anims

    def into_bag(self, item_id):
        if len(self.pc.inventory) >= 9:
            return
        for itm in charts.treasure:
            if itm[1] == item_id:
                inv_itm = (itm[0], itm[1], self.sprites_objects[mazes.objects[item_id]].sprite_surface)
                self.pc.inventory.append(inv_itm)
                self.maze_objects[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 0
                self.gui.sw_redraw = True
                self.redraw = True
        self.pg.audio.sound('pickup')

    def inv_check(self, item_id, remove=False):
        for i in range(0, len(self.pc.inventory)):
            if self.pc.inventory[i][1] == item_id:
                itm = self.pc.inventory[i]
                if remove:
                    del self.pc.inventory[i]
                    self.gui.sw_redraw = True
                    self.redraw = True
                return itm
        return None

    def use_item(self, item_name, item_id):
        # Doing things according to item_id. Return True to delete item after use.
        if item_id == 'key_gold':
            itm_x, itm_y = self.can_drop(self.pc.x, self.pc.y)
            self.maze_objects[self.xy_to_pos(self.maze_size, (itm_x, itm_y))] = mazes.objects['key_gold']
            self.log(texts.game_text['cave_drop'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pg.audio.sound('drop')
            return True
        elif item_id == 'm_flask':
            itm_x, itm_y = self.can_drop(self.pc.x, self.pc.y)
            self.maze_objects[self.xy_to_pos(self.maze_size, (itm_x, itm_y))] = mazes.objects['m_flask']
            self.log(texts.game_text['cave_drop'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pg.audio.sound('drop')
            return True
        elif item_id == 'ptn_red':
            # self.maze_body[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = ord(mazes.objects['key'])
            self.pc.hp = min(self.pc.hp + 3, charts.char_hp[self.pc.hp_lvl])
            self.log(texts.game_text['cave_ptn_red'] % (item_name, 3), self.res_man.colors['fnt_bonus'])
            self.pg.audio.sound('drink')
            return True
        elif item_id == 'ptn_yellow':
            # self.maze_body[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = ord(mazes.objects['key'])
            if 'poison' in self.pc.effects:
                self.pc.effects.remove('poison')
            self.log(texts.game_text['cave_ptn_yellow'] % (item_name), self.res_man.colors['fnt_bonus'])
            self.pg.audio.sound('drink')
            return True
        elif item_id == 'ptn_blue':
            # self.maze_body[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = ord(mazes.objects['key'])
            self.pc.mag = min(self.pc.mag + 1, charts.char_mag[self.pc.mag_lvl])
            self.log(texts.game_text['cave_ptn_blue'] % (item_name, 1), self.res_man.colors['fnt_bonus'])
            self.pg.audio.sound('drink')
            return True
        elif item_id == 'slvr_blade':
            itm_x, itm_y = self.can_drop(self.pc.x, self.pc.y)
            self.maze_objects[self.xy_to_pos(self.maze_size, (itm_x, itm_y))] = mazes.objects['slvr_blade']
            self.log(texts.game_text['cave_drop'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pg.audio.sound('drop')
            return True
        # Spells.
        elif item_id == 'sp_heal':
            if self.pc.mag < 1:
                self.log(texts.game_text['cave_lowmag'], self.res_man.colors['fnt_accent'])
                return True
            self.pc.hp = charts.char_hp[self.pc.hp_lvl]
            self.log(texts.game_text['cave_cast'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pc.mag -= 1
            self.pg.audio.sound('spell')
            return True
        elif item_id == 'sp_invis':
            if self.pc.mag < 1:
                self.log(texts.game_text['cave_lowmag'], self.res_man.colors['fnt_accent'])
                return True
            self.pc.effects.add('invisible')
            self.log(texts.game_text['cave_cast'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pc.mag -= 1
            self.pc.last_frame = None
            self.pg.audio.sound('spell')
            return True
        elif item_id == 'sp_barrier':
            if self.pc.mag < 1:
                self.log(texts.game_text['cave_lowmag'], self.res_man.colors['fnt_accent'])
                return True
            self.maze_body[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = mazes.tiles['door_wood']
            self.maze_flags[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = mazes.flags['door']
            self.log(texts.game_text['cave_cast'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pc.mag -= 1
            self.pg.audio.sound('spell')
            return True
        elif item_id == 'sp_dispel':
            if self.pc.mag < 1:
                self.log(texts.game_text['cave_lowmag'], self.res_man.colors['fnt_accent'])
                return True
            for i in range(self.pc.x - (self.DISP_SIZE_X // 2), self.pc.x + (self.DISP_SIZE_X // 2 + 1)):
                for j in range(self.pc.y - (self.DISP_SIZE_Y // 2), self.pc.y + (self.DISP_SIZE_Y // 2 + 1)):
                    try:
                        if self.maze_flags[self.xy_to_pos(self.maze_size, (i, j))] == mazes.flags['magic_wall']:
                            self.maze_body[self.xy_to_pos(self.maze_size, (i, j))] = mazes.tiles['port_stone']
                            self.maze_flags[self.xy_to_pos(self.maze_size, (i, j))] = 0
                    except IndexError:
                        pass
            self.log(texts.game_text['cave_cast'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pc.mag -= 1
            self.pg.audio.sound('open')
            self.pg.audio.sound('spell')
            return True
        elif item_id == 'sp_disint':
            if self.pc.mag < 1:
                self.log(texts.game_text['cave_lowmag'], self.res_man.colors['fnt_accent'])
                return True
            walls = self.nearby_bytes(
                (
                    (self.maze_flags, (
                        mazes.flags['wall'],
                        mazes.flags['fake_wall'],
                        mazes.flags['spikes'],
                        mazes.flags['trap'],
                        mazes.flags['door']
                    )),
                ), self.pc.x, self.pc.y, 1, r_max=1)
            walls.extend(self.nearby_bytes(
                (
                    (self.maze_objects, (
                        mazes.objects['mov_stone'],
                    )),
                ), self.pc.x, self.pc.y, 1, r_max=1))
            for wall in walls:
                try:
                    self.maze_flags[self.xy_to_pos(self.maze_size, wall)] = 0
                    self.maze_objects[self.xy_to_pos(self.maze_size, wall)] = 0
                    self.maze_body[self.xy_to_pos(self.maze_size, wall)] = mazes.tiles['floor_stone']
                    self.part_gen(wall[0], wall[1], 'hit', 8, 2)
                except IndexError:
                    continue
            self.log(texts.game_text['cave_cast'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pc.mag -= 1
            self.pg.audio.sound('defeat')
            return True
        elif item_id == 'sp_petrify':
            if self.pc.mag < 1:
                self.log(texts.game_text['cave_lowmag'], self.res_man.colors['fnt_accent'])
                return True
            mobs_remove = []
            for mb in self.mobs:
                if abs(mb.x - self.pc.x) > self.DISP_SIZE_X // 2 or \
                        abs(mb.y - self.pc.y) > self.DISP_SIZE_Y // 2:
                    continue
                mobs_remove.append(mb)
                self.maze_actors[self.xy_to_pos(self.maze_size, (mb.x, mb.y))] = 0
                self.maze_objects[self.xy_to_pos(self.maze_size, (mb.x, mb.y))] = mazes.objects['mov_stone']
            for mb in mobs_remove:
                self.mobs.remove(mb)
            self.log(texts.game_text['cave_cast'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pc.mag -= 1
            if len(mobs_remove) > 0:
                self.pg.audio.sound('clicks')
            self.pg.audio.sound('spell')
            return True
        elif item_id == 'sp_turn':
            if self.pc.mag < 1:
                self.log(texts.game_text['cave_lowmag'], self.res_man.colors['fnt_accent'])
                return True
            for mb in self.mobs:
                if abs(mb.x - self.pc.x) > self.DISP_SIZE_X // 2 or \
                        abs(mb.y - self.pc.y) > self.DISP_SIZE_Y // 2:
                    continue
                if 'dead' in mb.effects:
                    mb.effects.remove('dead')
                    if 'turned' not in mb.effects:
                        mb.effects.append('turned')
            self.log(texts.game_text['cave_cast'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pc.mag -= 1
            self.pg.audio.sound('spell')
            return True
        elif item_id == 'sp_warp':
            if self.pc.mag < 1:
                self.log(texts.game_text['cave_lowmag'], self.res_man.colors['fnt_accent'])
                return True
            self.log(texts.game_text['cave_cast'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pc.mag -= 1
            self.maze_actors[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 0
            self.pc.x = self.pc_start_x
            self.pc.y = self.pc_start_y
            self.maze_actors[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 2
            self.pg.audio.sound('spell')
            return True
        elif item_id == 'sp_stop':
            if self.pc.mag < 1:
                self.log(texts.game_text['cave_lowmag'], self.res_man.colors['fnt_accent'])
                return True
            self.pc.effects.add('timestop')
            self.log(texts.game_text['cave_cast'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pc.mag -= 1
            self.pg.audio.sound('spell')
            return True
        elif item_id == 'sp_kill':
            if self.pc.mag < 1:
                self.log(texts.game_text['cave_lowmag'], self.res_man.colors['fnt_accent'])
                return True
            for mb in self.mobs:
                if self.get_dist(self.pc.x, self.pc.y, mb.x, mb.y) < 3 \
                        and self.cast_ray(self.pc.x, self.pc.y, mb.x, mb.y):
                    mb.hp = 0
                    self.part_gen(mb.x, mb.y, 'hit', 8, 2)
            self.log(texts.game_text['cave_cast'] % (item_name), self.res_man.colors['fnt_normal'])
            self.pc.mag -= 1
            self.pg.audio.sound('spell')
            return True
        return False

    def can_drop(self, x, y):
        try:
            itm_x, itm_y = self.nearby_bytes(
                (
                    (self.maze_objects, (0,)),
                    (self.maze_flags, (
                        mazes.flags['space'],
                        mazes.flags['spikes'],
                        mazes.flags['trap'],
                        mazes.flags['start'],
                    )),
                ),
                x, y, 1, r_max=1)[0]
        except IndexError:
            return None
        return itm_x, itm_y

    def cast_ray(self, x1, y1, x2, y2):
        dist_x = x2 - x1
        dist_y = y2 - y1
        if abs(dist_x) >= abs(dist_y):
            if dist_x != 0:
                step_y = abs(dist_y / dist_x) * self.sign(dist_y)
            else:
                step_y = 0
            step_x = self.sign(dist_x)
        else:
            step_y = self.sign(dist_y)
            if dist_y != 0:
                step_x = abs(dist_x / dist_y) * self.sign(dist_x)
            else:
                step_x = 0
        temp_x = x1
        temp_y = y1
        hit = False
        while not hit and (abs(temp_x - x2) >= 1 or abs(temp_y - y2) >= 1):
            # self.part_gen(round(temp_x), round(temp_y), 'hit', 8, 2)
            if self.maze_flags[self.xy_to_pos(self.maze_size, (round(temp_x), round(temp_y)))] in (
                    mazes.flags['wall'],
                    mazes.flags['fake_wall'],
                    mazes.flags['magic_wall'],
                    mazes.flags['door'],
                    mazes.flags['metal_door']
            ) or self.maze_objects[self.xy_to_pos(self.maze_size, (round(temp_x), round(temp_y)))] in (
                    mazes.objects['chest'],
            ):
                hit = True
            # test ray calculation
            temp_x += step_x
            temp_y += step_y
        if hit:
            return False
        else:
            return True

    def sign(self, x):
        sign = 0
        if x > 0:
            sign = 1
        elif x < 0:
            sign = -1
        return sign

    def bytes_repl(self, byte_seq, b_orig_list, b_repl):
        count = 0
        for i in range(0, len(byte_seq)):
            if byte_seq[i] in b_orig_list:
                byte_seq[i] = b_repl
                count += 1
        return count

    # Player character movement.
    def pc_move(self, step_x, step_y):
        pc_pos = self.xy_to_pos(self.maze_size, (self.pc.x + step_x, self.pc.y + step_y))
        pc_pos_f = self.xy_to_pos(self.maze_size, (self.pc.x + step_x * 2, self.pc.y + step_y * 2))
        if not self.pc.vis or self.pc.offset_x or self.pc.offset_y:
            return
        # Getting a square in the way.
        # Check if there is a wall in the way.
        if self.maze_flags[pc_pos] in (
                mazes.flags['wall'], mazes.flags['magic_wall']
        ):
            self.pc.mov_dir = 0
            return
        elif self.maze_flags[pc_pos] == mazes.flags['door']:
            self.maze_flags[pc_pos] = 0
            self.maze_body[pc_pos] = mazes.tiles['port_stone']
            self.pc.mov_dir = 0
            self.redraw = True
            self.pg.audio.sound('door')
            self.dm_done = False
            self.checks_done = False
            # Removing timestop if applied.
            if 'timestop' in self.pc.effects:
                self.pc.effects.remove('timestop')
                self.gui.sw_redraw = True
                self.redraw = True
            return
        elif self.maze_objects[pc_pos] == mazes.objects['chest']:
            self.maze_objects[pc_pos] = mazes.objects[drop.chest(self.lvl)]
            self.part_gen(self.pc.x + step_x, self.pc.y + step_y, 'hit', 8, 2)
            self.pg.audio.sound('open')
            self.pc.mov_dir = 0
            self.redraw = True
            self.dm_done = False
            self.checks_done = False
            # Removing timestop if applied.
            if 'timestop' in self.pc.effects:
                self.pc.effects.remove('timestop')
                self.gui.sw_redraw = True
                self.redraw = True
            return
        elif self.maze_flags[pc_pos] == mazes.flags['metal_door']:
            itm = self.inv_check('key_gold', remove=True)
            if itm is not None:
                self.maze_flags[pc_pos] = 0
                self.maze_body[pc_pos] = mazes.tiles['port_stone']
                self.log(texts.game_text['cave_use'] % itm[0], self.res_man.colors['fnt_normal'])
                self.pg.audio.sound('safe')
            self.pc.mov_dir = 0
            self.gui.sw_redraw = True
            self.redraw = True
            self.dm_done = False
            self.checks_done = False
            # Removing timestop if applied.
            if 'timestop' in self.pc.effects:
                self.pc.effects.remove('timestop')
                self.gui.sw_redraw = True
                self.redraw = True
            return
        elif self.maze_objects[pc_pos] in (
                mazes.objects['mov_stone'],
        ):
            # Removing timestop if applied.
            if 'timestop' in self.pc.effects:
                self.pc.effects.remove('timestop')
                self.gui.sw_redraw = True
                self.redraw = True
            if self.maze_flags[pc_pos_f] in (0, mazes.flags['fake_wall']) and self.maze_objects[pc_pos_f] not in (
                    mazes.objects['chest'],
                    mazes.objects['mov_stone']
            ):
                if self.maze_actors[pc_pos_f] == 0:
                    self.maze_objects[pc_pos], self.maze_objects[pc_pos_f] = 0, self.maze_objects[pc_pos]
                    self.pg.audio.sound('stone')
                    self.redraw = True
                elif self.maze_actors[pc_pos_f] == 1:
                    for mb in self.mobs:
                        if self.xy_to_pos(self.maze_size, (mb.x, mb.y)) == pc_pos_f:
                            print('hit')
                            mb.wound(1)
                            self.part_gen(mb.x, mb.y, 'hit', 8, 2)
                            self.log(texts.game_text['cave_stoneblock'] % mb.name, self.res_man.colors['fnt_normal'])
                    self.pg.audio.sound('stone')
                    self.redraw = True
                    self.dm_done = False
                    self.checks_done = False
                    self.pc.mov_dir = 0
                    return
            elif self.maze_flags[pc_pos_f] == mazes.flags['pit']:
                self.maze_flags[pc_pos_f] = self.maze_objects[pc_pos] = 0
                self.maze_body[pc_pos_f] = mazes.tiles['pit_stone']
                self.pg.audio.sound('stone')
                self.log(texts.game_text['cave_rockpit'], self.res_man.colors['fnt_normal'])
            else:
                self.pc.mov_dir = 0
                self.dm_done = False
                self.checks_done = False
                return
        elif self.maze_flags[pc_pos] == mazes.flags['start']:
            self.log(texts.game_text['cave_npgb'], self.res_man.colors['fnt_normal'])

        # Checking if there is a mob in the way.
        if self.maze_actors[pc_pos] == 1:
            for mb in self.mobs:
                if mb.x == self.pc.x + step_x and mb.y == self.pc.y + step_y:
                    mb.sight_dir = self.get_dir(mb.x, mb.y, self.pc.x, self.pc.y)
                    # Creating particle indicating the strike
                    self.part_gen(mb.x, mb.y, 'hit', 8, 2)
                    if 'dead' in mb.effects and self.inv_check('slvr_blade') is None:
                        self.log(texts.game_text['cave_immune'] % mb.name, self.res_man.colors['fnt_accent'])
                        self.pg.audio.sound('hit_pc')
                        break
                    att_dmg = self.pc.attack(mb, charts)
                    if 'dead' in mb.effects and mb.hp <= 0:
                        self.inv_check('slvr_blade', True)
                    # Removing timestop if applied.
                    if 'timestop' in self.pc.effects:
                        self.pc.effects.remove('timestop')
                        self.gui.sw_redraw = True
                        self.redraw = True
                    self.pg.audio.sound('hit_pc')
                    self.log(texts.game_text['cave_pc_attack'] % (mb.name, att_dmg), self.res_man.colors['fnt_accent'])
                    break
            self.pc.mov_dir = 0
            self.dm_done = False
            self.checks_done = False
            return
        # Updating maze flags. 1 = mob, 2 = player character.
        self.maze_actors[pc_pos] = 2
        self.maze_actors[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 0

        self.pc.x += step_x
        self.pc.y += step_y
        self.pc.offset_x = step_x * self.GRID_SIZE * -1
        self.pc.offset_y = step_y * self.GRID_SIZE * -1
        self.dm_done = False
        self.checks_done = False
        self.redraw = True
        # Checking dungeon master.
        self.pg.audio.sound('step')

    # Mob movement.
    def mob_move(self, mb, step_x, step_y):
        mb.sight_dir = mb.mov_dir
        if not mb.vis or mb.offset_x or mb.offset_y:
            return
        mb_pos = self.xy_to_pos(self.maze_size, (mb.x + step_x, mb.y + step_y))
        if mb.x + step_x < 0 or mb.y + step_y < 0 or mb.x + step_x >= self.maze_size[0] or mb.y + step_y >= self.maze_size[1]:
            mb.mov_dir = random.choice((1, 2, 3, 4))
            return
        mb_pos_f = self.xy_to_pos(self.maze_size, (mb.x + step_x * 2, mb.y + step_y * 2))
        if self.maze_actors[mb_pos] == 2:
            if 'peaceful' in mb.effects:
                mb.mov_dir = random.choice((1, 2, 3, 4))
                return
            mb.mov_dir = 0
            att_dmg = mb.attack(self.pc, charts)
            self.log(texts.game_text['cave_mob_attack'] % (mb.name, att_dmg), self.res_man.colors['fnt_attent'])
            # Checking effects
            if 'strong' in mb.effects and self.maze_actors[mb_pos_f] == 0 \
                    and self.maze_flags[mb_pos_f] not in (
                    mazes.flags['wall'],
                    mazes.flags['magic_wall'],
                    mazes.flags['door'],
                    mazes.flags['metal_door']
            ) and self.maze_objects[mb_pos_f] not in (
                    mazes.objects['chest'],
                    mazes.objects['mov_stone'],
            ):
                self.maze_actors[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 0
                self.pc.x += step_x
                self.pc.y += step_y
                self.maze_actors[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 2
                self.log(texts.game_text['cave_blowaway'], self.res_man.colors['fnt_normal'])
            # Creating particle indicating the strike
            self.part_gen(self.pc.x, self.pc.y, 'hit', 8, 2)
            self.gui.sw_redraw = True
            self.pg.audio.sound('hit_en')
            return
        # Getting a square in the way.
        # Checking if there is a wall in the way.
        if self.maze_flags[mb_pos] not in (
                mazes.flags['space'],
                mazes.flags['spikes'],
                mazes.flags['trap'],
                mazes.flags['start'],
                mazes.flags['exit']
        ) or self.maze_objects[mb_pos] in (
                mazes.objects['chest'],
                mazes.objects['mov_stone'],
        ):
            if 'ghost' not in mb.effects:
                mb.mov_dir = random.choice((1, 2, 3, 4))
                return
        # Checking if there is a mob in the way.
        if self.maze_actors[mb_pos] == 1:
            mb.mov_dir = random.choice((1, 2, 3, 4))
            return

        mb.mov_dir = 0

        # Updating maze flags.
        self.maze_actors[mb_pos] = 1
        self.maze_actors [self.xy_to_pos(self.maze_size, (mb.x, mb.y))] = 0
        mb.x += step_x
        mb.y += step_y
        mb.offset_x = step_x * self.GRID_SIZE * -1
        mb.offset_y = step_y * self.GRID_SIZE * -1
        self.redraw = True

    def get_sq(self, grid, x, y):
        sq_byte = grid[self.xy_to_pos(self.maze_size, (x, y))]
        return sq_byte

    def get_frame(self, obj, frames):
        if obj.offset_x < 0 and not self.counter0.step % 2:
            frame = frames[2]
        elif obj.offset_x < 0 and self.counter0.step % 2:
            frame = frames[3]
        elif obj.offset_x > 0 and not self.counter0.step % 2:
            frame = self.pg.pygame.transform.flip(frames[2], True, False)
        elif obj.offset_x > 0 and self.counter0.step % 2:
            frame = self.pg.pygame.transform.flip(frames[3], True, False)
        elif obj.offset_y < 0 and not self.counter0.step % 2:
            frame = frames[0]
        elif obj.offset_y < 0 and self.counter0.step % 2:
            frame = self.pg.pygame.transform.flip(frames[0], True, False)
        elif obj.offset_y > 0 and not self.counter0.step % 2:
            frame = frames[1]
        elif obj.offset_y > 0 and self.counter0.step % 2:
            frame = self.pg.pygame.transform.flip(frames[1], True, False)
        elif obj.last_frame:
            frame = obj.last_frame
        else:
            frame = frames[0]
        obj.last_frame = frame
        return frame

    # Reacting to SAY ALOUD words.
    def comprehend(self, word):
        word = word.upper()
        person = None
        for mb in self.mobs:
            if mb.name in (
                mazes.mobs[125],
                mazes.mobs[128],
                mazes.mobs[129],
                mazes.mobs[130],
                mazes.mobs[131],
                mazes.mobs[132],
                mazes.mobs[133],
                mazes.mobs[134],
            ) and self.get_dist(mb.x, mb.y, self.pc.x, self.pc.y) < 2:
                person = mb
                break

        if word == 'SMOKE':
            self.log(texts.game_text['cave_smoke'], self.res_man.colors['fnt_normal'])
            self.pc.wound(1)
            self.gui.sw_redraw = True
            self.redraw = True
        elif word == 'ARCUS DESTRO':
            self.into_bag('sp_disint')
            self.gui.sw_redraw = True
            self.redraw = True
        elif word == 'LUCIO':
            self.pc.score = 900000
            self.gui.sw_redraw = True
            self.redraw = True
        elif word == 'PRAY':
            self.pc.hp = charts.char_hp[self.pc.hp_lvl]
            self.log(texts.game_text['cave_cured'], self.res_man.colors['fnt_normal'])
            self.gui.sw_redraw = True
        elif word == 'PROFOUND DAZE':
            self.log('CODE %s' % self.maze_body[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))], self.res_man.colors['fnt_normal'])
        elif person is None:
            self.log(texts.game_text['cave_echo'] % (word), self.res_man.colors['fnt_normal'])

        if person is None:
            return

        # dialogue system
        phrase = word.split()
        # common responses.
        if 'murderer' in self.pc.effects:
            self.log(texts.dlg_common['murderer'], self.res_man.colors['fnt_normal'])
            return
        if 'BYE' in phrase or 'GOODBYE' in phrase or 'FAREWELL' in phrase:
            self.log(texts.dlg_common['bye'], self.res_man.colors['fnt_normal'])
        # human responses:
        if person.name == mazes.mobs[134]:
            if 'NAME' in phrase:
                self.log(texts.dlg_human['name'], self.res_man.colors['fnt_normal'])
            elif 'HELLO' in phrase or 'HI' in phrase:
                self.log(texts.dlg_human['hello'], self.res_man.colors['fnt_normal'])
            elif 'LORE' in phrase or 'KNOWLEDGE' in phrase or 'HINT' in phrase:
                self.log(texts.dlg_human['lore'], self.res_man.colors['fnt_normal'])
            elif 'HEAL' in phrase or 'HELP' in phrase:
                cost = 100 * (self.lvl + 1)
                self.log(texts.dlg_human['heal'] % cost, self.res_man.colors['fnt_normal'])
            elif 'PREPARE' in phrase:
                if self.pc.score < 100 * (self.lvl + 1):
                    self.log(texts.dlg_common['no_gold'], self.res_man.colors['fnt_normal'])
                    return
                self.log(texts.dlg_human['prepare'], self.res_man.colors['fnt_accent'])
                self.pc.score -= 100 * (self.lvl + 1)
                self.pc.hp = min(charts.char_hp[self.pc.hp_lvl], self.pc.hp + random.randrange(2,5) * (self.lvl + 1))
                self.gui.sw_redraw = True
            elif 'MUSIC' in phrase or 'TUNE' in phrase or 'MELODY' in phrase:
                self.log(texts.dlg_human['melody'], self.res_man.colors['fnt_normal'])
            elif 'BIZARRE' in phrase:
                self.log(texts.dlg_human['bizarre'], self.res_man.colors['fnt_normal'])
            elif 'PLAY' in phrase:
                self.log(texts.dlg_human['play'], self.res_man.colors['fnt_normal'])
                self.pg.audio.music('menu', 1)
            elif 'STOP' in phrase:
                self.log(texts.dlg_human['stop'], self.res_man.colors['fnt_normal'])
                self.pg.audio.music_stop()
            else:
                self.log(texts.game_text['cave_echo'] % (word), self.res_man.colors['fnt_normal'])
        # goblin responses
        elif person.name == mazes.mobs[128]:
            if 'NAME' in phrase:
                self.log(texts.dlg_goblin['name'], self.res_man.colors['fnt_normal'])
            elif 'HELLO' in phrase or 'HI' in phrase:
                self.log(texts.dlg_goblin['hello'], self.res_man.colors['fnt_normal'])
            elif 'LORE' in phrase or 'KNOWLEDGE' in phrase or 'HINT' in phrase:
                self.log(texts.dlg_goblin['lore'], self.res_man.colors['fnt_normal'])
            elif 'DSSCHRGE' in phrase or 'DISCHARGE' in phrase or 'REMOVE' in phrase:
                self.log(texts.dlg_goblin['dsschrge'], self.res_man.colors['fnt_normal'])
            elif 'TRAPS' in phrase or 'BSSTRDS' in phrase or 'TRPSS' in phrase:
                self.log(texts.dlg_goblin['traps'], self.res_man.colors['fnt_normal'])
            elif 'PAI' in phrase or 'PAY' in phrase:
                cost = 1000
                for i in self.maze_flags:
                    if i in (
                        mazes.flags['trap'],
                    ):
                        cost += (self.lvl + 1) * 100
                if self.pc.score >= cost:
                    self.pc.score -= cost
                    self.gui.sw_redraw = True
                    self.bytes_repl(self.maze_flags, (mazes.flags['trap'],), 0)
                    self.log(texts.dlg_goblin['pai'], self.res_man.colors['fnt_normal'])
                    self.mobs.remove(person)
                    self.maze_actors[self.xy_to_pos(self.maze_size, (person.x, person.y))] = 0
                else:
                    self.log(texts.dlg_common['no_gold'], self.res_man.colors['fnt_normal'])
                    return

    def check_pc(self):
        self.checks_done = True
        if not self.pg.pygame.mixer.music.get_busy() and random.randrange(1, 101) <= 2:
            self.pg.audio.playlist()
        # Checking player square.
        flag_byte = self.get_sq(self.maze_flags, self.pc.x, self.pc.y)
        if flag_byte == mazes.flags['spikes']:
            dmg = (self.lvl + 1)
            self.log(texts.game_text['cave_harm'] % dmg, self.res_man.colors['fnt_attent'])
            self.pc.wound(dmg)
            self.gui.sw_redraw = True
            self.part_gen(self.pc.x, self.pc.y, 'hit', 8, 2)
            self.pg.audio.sound('hit_en')
        elif flag_byte == mazes.flags['trap']:
            dmg = (self.lvl + 1)
            self.log(texts.game_text['cave_harm'] % dmg, self.res_man.colors['fnt_attent'])
            self.maze_flags[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 0
            self.pc.wound(dmg)
            self.gui.sw_redraw = True
            self.part_gen(self.pc.x, self.pc.y, 'hit', 8, 2)
            self.pg.audio.sound('hit_en')
            self.pc.mov_dir = 0
        elif flag_byte == mazes.flags['trap_poison']:
            if 'poison' not in self.pc.effects:
                self.pc.effects.add('poison')
            self.log(texts.game_text['cave_poison'], self.res_man.colors['fnt_attent'])
            self.maze_flags[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 0
            self.gui.sw_redraw = True
            self.part_gen(self.pc.x, self.pc.y, 'hit', 8, 2)
            self.pg.audio.sound('hit_en')
            self.pc.mov_dir = 0
        elif flag_byte == mazes.flags['pit']:
            self.pg.audio.sound('fall')
            self.pc.hp = 0
        elif flag_byte == mazes.flags['exit']:
            # self.pc.score += charts.score_rewards[min(self.lvl, len(charts.score_rewards) - 1)]
            self.pg.audio.sound('stairs')
            if 'murderer' in self.pc.effects:
                self.pc.effects.remove('murderer')
            # checking if there is an intermission for the completed level
            if self.lvl in charts.intermissions:
                self.playcard = {
                    'run': 2,
                    'pc': self.pc,
                    'lvl': self.lvl,
                    'demo': 1
                }
            else:
                # if there is no intermission, loading the next cave
                self.playcard = {
                    'run': 1,  # re-running a cave block
                    'pc': self.pc,
                    'lvl': self.lvl + 1
                }
            self.active = False
            self.redraw = False
        obj_byte = self.maze_objects[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))]
        if obj_byte == mazes.objects['memo_page']:
            n_code = str(self.pc.x).zfill(3) + str(self.pc.y).zfill(3)
            memo_text = self.maze_memos[n_code][0]
            memo_pref = self.maze_memos[n_code][1]
            try:
                self.log(memo_text, memo_pref)
            except KeyError:
                self.log(texts.game_text['cave_unreadable'], self.res_man.colors['fnt_normal'])
            self.pg.audio.sound('paper')
        elif obj_byte == mazes.objects['hp_up']:
            self.bytes_repl(self.maze_objects,
                            (mazes.objects['hp_up'], mazes.objects['pow_up'], mazes.objects['mag_up']), 0)
            if len(charts.char_hp) > self.pc.hp_lvl + 1:
                self.pc.hp_lvl += 1
                self.gui.sw_redraw = True
                self.log(texts.game_text['cave_hpup'], self.res_man.colors['fnt_accent'])
            else:
                self.log(texts.game_text['cave_maxed'], self.res_man.colors['fnt_accent'])
            self.pg.audio.sound('heart')
        elif obj_byte == mazes.objects['pow_up']:
            self.bytes_repl(self.maze_objects,
                            (mazes.objects['hp_up'], mazes.objects['pow_up'], mazes.objects['mag_up']), 0)
            if len(charts.char_pow) > self.pc.pow_lvl + 1:
                self.pc.pow_lvl += 1
                self.gui.sw_redraw = True
                self.log(texts.game_text['cave_powup'], self.res_man.colors['fnt_accent'])
            else:
                self.log(texts.game_text['cave_maxed'], self.res_man.colors['fnt_accent'])
            self.pg.audio.sound('blade')
        elif obj_byte == mazes.objects['mag_up']:
            self.bytes_repl(self.maze_objects,
                            (mazes.objects['hp_up'], mazes.objects['pow_up'], mazes.objects['mag_up']), 0)
            if len(charts.char_mag) > self.pc.mag_lvl + 1:
                self.pc.mag_lvl += 1
                self.gui.sw_redraw = True
                self.log(texts.game_text['cave_magup'], self.res_man.colors['fnt_accent'])
            else:
                self.log(texts.game_text['cave_maxed'], self.res_man.colors['fnt_accent'])
            self.pg.audio.sound('arcane')
        elif obj_byte == mazes.objects['gold']:
            gold = charts.gold[min(self.lvl, len(charts.gold) - 1)]
            self.pc.score += (random.randrange(gold[0], gold[1] + 1))
            self.maze_objects[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 0
            self.gui.sw_redraw = True
            self.redraw = True
            self.pg.audio.sound('coins')
        elif obj_byte == mazes.objects['sp_unknown']:
            # Detect spell based on cave level.
            if len(self.pc.inventory) >= 9:
                return
            if charts.random_spells:
                spell = random.choice(charts.spells)
            else:
                spell = charts.spells[min(self.lvl, len(charts.spells) - 1)]
            inv_itm = (spell[0], spell[1], self.sprites_objects[mazes.objects[spell[1]]].sprite_surface)
            self.pc.inventory.append(inv_itm)
            self.maze_objects[self.xy_to_pos(self.maze_size, (self.pc.x, self.pc.y))] = 0
            self.gui.sw_redraw = True
            self.redraw = True
            self.pg.audio.sound('book')
        elif obj_byte == mazes.objects['m_flask']:
            self.into_bag('m_flask')
            self.log(texts.game_text['cave_flask'], self.res_man.colors['fnt_celeb'])
        # other items that just are put into inventory.
        elif obj_byte in mazes.objects.values():
            for key, value in mazes.objects.items():
                if obj_byte == value:
                    self.into_bag(key)
        # Checking player effects.
        if 'poison' in self.pc.effects and not 'timestop' in self.pc.effects:
            self.pc.wound(1)
            self.gui.sw_redraw = True
            self.redraw = True
            if random.randrange(1, 101) <= 10:
                self.pc.effects.remove('poison')
                self.log(texts.game_text['cave_cured'], self.res_man.colors['fnt_normal'])
            else:
                self.log(texts.game_text['cave_poisoned'], self.res_man.colors['fnt_normal'])
            self.pg.audio.sound('hit_en')
        if 'invisible' in self.pc.effects:
            self.pc.ani_name = 'invis'
        else:
            self.pc.ani_name = 'pc'
        if self.pc.hp <= 0:
            self.playcard = {
                'run': 2,
                'pc': self.pc,
                'lvl': self.lvl,
                'demo': 2
            }
            self.active = False
            self.redraw = False

    def pc_vision_check(self):
        self.pc_vision = self.vision_calc((
            (self.maze_flags, (
                mazes.flags['wall'],
                mazes.flags['fake_wall'],
                mazes.flags['magic_wall'],
                mazes.flags['door'],
                mazes.flags['metal_door']
            )),
            (self.maze_objects, (
                mazes.objects['mov_stone'],
            )),
        ), self.pc.x, self.pc.y, 0)
        self.redraw = True

    def check_mob(self, mb):
        if mb.hp <= 0:
            self.maze_actors[self.xy_to_pos(self.maze_size, (mb.x, mb.y))] = 0

            new_itm = drop.get_drop(mb.name, self.lvl)
            if new_itm is None:
                return False
            try:
                itm_x, itm_y = self.can_drop(mb.x, mb.y)
                self.maze_objects[self.xy_to_pos(self.maze_size, (itm_x, itm_y))] = mazes.objects[new_itm[1]]
                self.log(texts.game_text['cave_loot'] % (mb.name, new_itm[0]), self.res_man.colors['fnt_normal'])
            except TypeError:
                self.log(texts.game_text['cave_noloot'] % (mb.name), self.res_man.colors['fnt_normal'])

            if 'peaceful' in mb.effects:
                self.pc.score = max(0, self.pc.score - mb.reward * 10)
                self.log(texts.game_text['cave_murder'], self.res_man.colors['fnt_normal'])
                self.pc.effects.add('murderer')
                # spawning hostile wrath seeking revenge if unlucky.
                if random.randrange(1, 101) <= 10:
                    self.spawn_mob('wrath', (mb.x, mb.y))
            else:
                self.pc.score += mb.reward
            self.gui.sw_redraw = True
            self.redraw = True

            return False
        return True

    def log(self, msg, color):
        self.pc.log.append((msg, color))
        self.gui.mw_redraw = True
        self.redraw = True

    def dm(self):
        self.pc_vision_check()
        self.dm_done = True
        # Rolling for random encounters.
        # if self.maze_diff > 0:
        #     self.roll_mob()
        # Checking if any mob can move:
        mobs_remove = []
        for mb in self.mobs:
            if abs(mb.x - self.pc.x) > self.DISP_SIZE_X // 2 or \
                    abs(mb.y - self.pc.y) > self.DISP_SIZE_Y // 2:
                continue
            if not self.check_mob(mb):
                mobs_remove.append(mb)
                continue
            if 'timestop' in self.pc.effects:
                continue
            mb.sp_pts += mb.speed

            if mb.alert:
                mb.sp_pts += 2
            # Letting mob move if it has enough speed points.
            if mb.sp_pts >= mb.max_sp_pts:
                mb.sp_pts -= mb.max_sp_pts
                # Checking mobs effects.
                if 'bound' in mb.effects:
                    mb.last_frame = random.choice(self.cave_anims[mb.ani_name])
                    continue

                if 'traps' in mb.effects and random.randrange(1, 101) <= 15 and self.get_sq(self.maze_flags, mb.x, mb.y) == 0:
                    self.maze_flags[self.xy_to_pos(self.maze_size, (mb.x, mb.y))] = mazes.flags['trap']
                    self.log(texts.game_text['cave_sus'] % mb.name, self.res_man.colors['fnt_normal'])
                    self.pg.audio.sound('clicks')
                    continue

                pc_dir = self.get_dir(mb.x, mb.y, self.pc.x, self.pc.y)
                if 'turned' in mb.effects:
                    mb.mov_dir = self.get_dir(self.pc.x, self.pc.y, mb.x, mb.y)
                elif 'invisible' in self.pc.effects:
                    mb.mov_dir = random.choice((1, 2, 3, 4))
                elif 'flair' in mb.effects:
                    mb.mov_dir = pc_dir
                    mb.alert = True
                elif self.get_dist(mb.x, mb.y, self.pc.x, self.pc.y) == 1 or (mb.sight_dir == pc_dir and self.cast_ray(mb.x, mb.y, self.pc.x, self.pc.y)):
                    mb.mov_dir = pc_dir
                    mb.alert = True
                else:
                    if mb.alert:
                        mb.sp_pts = 0
                        mb.mov_dir = mb.sight_dir
                    else:
                        if self.get_dist(mb.x, mb.y, self.pc.x, self.pc.y) < 5:
                            mb.mov_dir = pc_dir
                        else:
                            mb.mov_dir = random.choice((1, 2, 3, 4))
                    mb.alert = False

            # Checking turn indicator
            if mb.speed + mb.sp_pts < mb.max_sp_pts and 'bound' not in mb.effects:
                mb.turn_ind = True
            else:
                mb.turn_ind = False

        for mb in mobs_remove:
            self.mobs.remove(mb)
        if len(mobs_remove) > 0:
            self.pg.audio.sound('defeat')

    # Random encounters generations
    def roll_mob(self):
        chances_sum = 0
        for enc in charts.encounters[min(self.lvl, len(charts.encounters) - 1)]['mobs']:
            chances_sum += enc[1]

        roll = random.randrange(1, chances_sum + 1)
        chances_sum = 0
        for enc in charts.encounters[min(self.lvl, len(charts.encounters) - 1)]['mobs']:
            chances_sum += enc[1]
            if roll <= chances_sum and self.maze_diff >= enc[2]:
                self.maze_diff -= enc[2]
                if self.maze_diff <= 0:
                    self.log(texts.game_text['cave_faints'], self.res_man.colors['fnt_normal'])
                return self.spawn_mob(enc[0])

    def spawn_mob(self, mob_name, xy=None):
        mob_stats = charts.monster_book[mob_name]
        if xy is None:
            try:
                mob_x, mob_y = self.rnd_spawn_point(0, 0, self.maze_size[0] - 1, self.maze_size[1] - 1)
            except TypeError:
                return None
        else:
            mob_x, mob_y = xy
        new_mob = mob.Mob(mob_name, mob_x, mob_y, mob_stats)
        new_mob.sp_pts = random.randrange(0, new_mob.max_sp_pts + 1)
        # Checking mob effects.
        if 'mirror' in new_mob.effects:
            new_mob.hp = new_mob.max_hp = charts.char_hp[self.pc.hp_lvl]
            new_mob.dmg_min, new_mob.dmg_max = charts.char_pow[self.pc.pow_lvl]
        self.maze_actors[self.xy_to_pos(self.maze_size, (mob_x, mob_y))] = 1
        self.mobs.append(new_mob)
        return new_mob

    def get_dist(self, x1, y1, x2, y2):
        dist = round(math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2)))
        return dist

    def get_dir(self, x1, y1, x2, y2):
        x_dif = x2 - x1
        y_dif = y2 - y1
        if abs(x_dif) > abs(y_dif):
            if x_dif > 0:
                return 2
            elif x_dif < 0:
                return 4
            else:
                return 0
        else:
            if y_dif > 0:
                return 3
            elif y_dif < 0:
                return 1
            else:
                return 0

    def rnd_spawn_point(self, left, top, right, bottom):
        rnd_x = random.randrange(left, right + 1)
        rnd_y = random.randrange(top, bottom + 1)
        xy_list = self.nearby_bytes(((self.maze_flags,(0)),), rnd_x, rnd_y, 1)
        if len(xy_list) > 0:
            return random.choice(xy_list)
        else:
            return None

    def nearby_bytes(self, byte_samples, start_x, start_y, space_number, xy_list=None, r=None, r_max=4):
        if xy_list is None:
            xy_list = []
            r = 1
        spaces_list = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        # random.shuffle(spaces_list)
        for tile_x, tile_y in spaces_list:
            abs_x, abs_y = start_x + tile_x, start_y + tile_y
            if abs_x < 0 or abs_y < 0 or abs_x > self.maze_size[0] or abs_y > self.maze_size[1]:
                continue
            xy_fit = True
            for sample in byte_samples:
                if sample[0][self.xy_to_pos(self.maze_size, (abs_x, abs_y))] not in sample[1]:
                    xy_fit = False
            if xy_fit:
                xy_list.append((abs_x, abs_y))
        if len(xy_list) < space_number and r < r_max:
            for tile_x, tile_y in spaces_list:
                abs_x, abs_y = start_x + tile_x, start_y + tile_y
                self.nearby_bytes(byte_samples, abs_x, abs_y, space_number, xy_list, r + 1, r_max)
        return xy_list

    def part_gen(self, x, y, anim_name, time, frame_time):
        new_particle = particle.Particle(x, y, self.cave_anims[anim_name], time, frame_time)
        self.particles.append(new_particle)

    def maze_build(self, width, height):
        maze = build.maze_array(width, height, ' ')
        min_w = 3
        min_h = 3
        rooms = build.split_build(0, 0, height - 1, width - 1, min_w, min_h, True)
        random.shuffle(rooms)
        for rm in rooms:
            build.square(maze, rm.top, rm.left, rm.bottom + 1, rm.right + 1, '0', ' ', True)
        for rm in rooms:
            build.rooms_attached(maze, rooms, rm, 2, 2, max(min_w, min_h))
        # Starting point
        rnd_room = random.choice(rooms)
        rnd_x = random.randrange(rnd_room.left + 1, rnd_room.right)
        rnd_y = random.randrange(rnd_room.top + 1, rnd_room.bottom)
        maze[rnd_y][rnd_x] = mazes.objects['pc_start']
        # Exit point
        rnd_room = random.choice(rooms)
        rnd_x = random.randrange(rnd_room.left + 1, rnd_room.right)
        rnd_y = random.randrange(rnd_room.top + 1, rnd_room.bottom)
        maze[rnd_y][rnd_x] = mazes.objects['exit']
        return maze

    def vision_calc(self, byte_samples, start_x, start_y, space_number, xy_stop_list=None, r=None, r_max=20):
        if xy_stop_list is None:
            xy_stop_list = [(start_x, start_y)]
            r = 1
        spaces_list = [(0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1,1)]
        # random.shuffle(spaces_list)
        for tile_x, tile_y in spaces_list:
            abs_x, abs_y = start_x + tile_x, start_y + tile_y
            if (abs_x, abs_y) in xy_stop_list:
                continue
            if abs_x < 0 or abs_y < 0 or abs_x >= self.maze_size[0] or abs_y >= self.maze_size[1]:
                continue
            if abs(self.pc.x - abs_x) > self.DISP_SIZE_X // 2 or abs(self.pc.y - abs_y) > self.DISP_SIZE_Y // 2:
                continue
            xy_stop_list.append((abs_x, abs_y))
            xy_stop = False
            for sample in byte_samples:
                if sample[0][self.xy_to_pos(self.maze_size, (abs_x, abs_y))] in sample[1]:
                    xy_stop = True
            if xy_stop:
                pass
            else:
                abs_x, abs_y = start_x + tile_x, start_y + tile_y
                self.vision_calc(byte_samples, abs_x, abs_y, space_number, xy_stop_list, r + 1, r_max)

        return xy_stop_list
