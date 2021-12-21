# Text object for drawing letters with tiles.

class Text:	
	def __init__(self, pg, res_man, text, xy_list, t_color=None, align=0):
		self.pg = pg
		self.colors = res_man.colors
		self.tileset = res_man.tilesets[res_man.font_ts]
		self.font_size = res_man.font_size
		self.font_chart = res_man.font_chart
		self.text_surface = self.convert(text, t_color)
		self.xy_list = xy_list
		self.x_offset = self.get_offset(self.text_surface, align)

	def get_offset(self, text_surface, align):
		x_offset = 0
		if align == 1:
			x_offset = text_surface.get_width() // 2 * -1
		elif align == 2:
			x_offset = text_surface.get_width() * -1
		return x_offset

	def convert(self, text, t_color):
		# Creating surface for text.
		surf_w = self.font_size[0] * len(max(text, key=len))
		surf_h = self.font_size[1] * len(text)
		text_surface = self.pg.pygame.Surface((surf_w, surf_h))
		text_surface.fill(self.colors['transparent'])
		# Only upper case available. Converting all characters to upper case.
		for i in range(0, len(text)):
			txt_str = text[i].upper()
			for j in range(0, len(txt_str)):
				# Drawing letter segments of tileset onto text surface one by one.
				dest = (self.font_size[0] * j, self.font_size[1] * i)
				symb_left, symb_top = self.font_chart[txt_str[j]]
				area = (symb_left, symb_top, self.font_size[0], self.font_size[1])
				text_surface.blit(self.tileset, dest, area)
		# Returning text surface if color not set.
		if t_color is None:
			# Setting transparent color to bright green.
			text_surface.set_colorkey(self.colors['transparent'])
			return text_surface
		# Creating new surface and filling it with needed color.
		text_surface_color = self.pg.pygame.Surface((surf_w, surf_h))
		text_surface_color.fill(t_color)
		# Setting text surface transparency to white
		text_surface.set_colorkey((255,255,255))
		# Layering the surface onto one filled with needed color
		text_surface_color.blit(text_surface, (0,0))
		# Setting colorful text surface transparency to bright green.
		text_surface_color.set_colorkey(self.colors['transparent'])
		# Returning colorful text surface.
		return text_surface_color

	# Drawing text on the given surface
	def draw(self, surface):
		for xy in self.xy_list:
			x, y = xy
			surface.blit(self.text_surface, (x + self.x_offset, y))
