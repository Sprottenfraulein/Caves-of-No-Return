# Object for composing tiles into bigger images.

class Sprite:
	def __init__(self, pg, res_man, tiles_list, matrix, xy_list=None, align=0, size=(8,8)):
		self.pg = pg
		self.res_man = res_man
		# self.tiles_list = tiles_list
		# self.matrix = matrix
		self.xy_list = xy_list
		self.sprite_surface = self.compose(tiles_list, matrix, size)
		self.x_offset = 0
		if align == 1:
			self.x_offset = self.sprite_surface.get_width() // 2 * -1
		elif align == 2:
			self.x_offset = self.sprite_surface.get_width() * -1

	def compose(self, tiles_list, matrix, size):
		# Creating surface according to matrix size.
		ss_width = len(max(matrix, key=len)) * size[0]
		ss_height = len(matrix) * size[1]
		sprite_surface = self.pg.pygame.Surface((ss_width, ss_height))
		sprite_surface.fill(self.res_man.colors['transparent'])
		# Drawing fragments of tileset onto the created surface according to matrix.
		for i in range(0, len(matrix)):
			for j in range(0, len(matrix[i])):
				try:
					tile_index = int(matrix[i][j])
				except ValueError:
					continue
				# Reading tileset index and then tileset itself from resources manager.
				tileset = self.res_man.tilesets[tiles_list[tile_index][0]]
				# Reading area from tiles_list
				tile_area = tiles_list[tile_index][1]
				# Drawing the tile onto the surface
				sprite_surface.blit(tileset, (j * size[0], i * size[1]), tile_area)
		# Setting transparency.
		sprite_surface.set_colorkey(self.res_man.colors['transparent'])
		# Returning finished surface
		return sprite_surface

	def draw(self, surface):
		if not self.xy_list:
			return
		for xy in self.xy_list:
			x, y = xy
			surface.blit(self.sprite_surface, (x + self.x_offset, y))
