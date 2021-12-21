# Effects object

class Particle:
    def __init__(self, x, y, anim_frames, timer, frame_time):
        self.x = x
        self.y = y
        self.anim_frames = anim_frames
        self.timer = timer
        self.frame_time = frame_time
        self.frame_timer = 0
        self.frame_index = 0

    def tick(self):
        self.timer -= 1
        self.frame_timer += 1
        if self.timer <= 0:
            return 0
        if self.frame_timer >= self.frame_time:
            self.frame_index += 1
            self.frame_timer = 0
            return 2
        return 1

