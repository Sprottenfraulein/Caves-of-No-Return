import random

class Audio:
    def __init__(self, pygame):
        self.pygame = pygame
        self.bank_sounds = {
            'arcane': pygame.mixer.Sound('data/arcane.wav'),
            'blade': pygame.mixer.Sound('data/blade.wav'),
            'heart': pygame.mixer.Sound('data/heart.wav'),
            'spell': pygame.mixer.Sound('data/spell.wav'),
            'coins': pygame.mixer.Sound('data/gold.wav'),
            'book': pygame.mixer.Sound('data/book.wav'),
            'paper': pygame.mixer.Sound('data/paper.wav'),
            'drink': pygame.mixer.Sound('data/gulp.wav'),
            'clicks': pygame.mixer.Sound('data/clicks.wav'),
            'cluck': pygame.mixer.Sound('data/cluck.wav'),
            'stairs': pygame.mixer.Sound('data/stairs.wav'),
            'open': pygame.mixer.Sound('data/open.wav'),
            'door': pygame.mixer.Sound('data/door.wav'),
            'safe': pygame.mixer.Sound('data/safe.wav'),
            #'pierce': pygame.mixer.Sound('data/pierce.wav'),
            'fall': pygame.mixer.Sound('data/fall.wav'),
            'drop': pygame.mixer.Sound('data/drop.wav'),
            'hit_pc': pygame.mixer.Sound('data/hit1.wav'),
            'hit_en': pygame.mixer.Sound('data/hit0.wav'),
            'step': pygame.mixer.Sound('data/step.wav'),
            'stone': pygame.mixer.Sound('data/stone.wav'),
            'pickup': pygame.mixer.Sound('data/item.wav'),
            'defeat': pygame.mixer.Sound('data/blow.wav')
        }

        self.bank_music = {
            'menu': 'data/0.mid',
            'ending': 'data/1.mid',
            'st1': 'data/2.mid',
            'st2': 'data/3.mid',
            'st3': 'data/4.mid',
            'st4': 'data/5.mid',
            'st5': 'data/6.mid'
            #'under': 'data/descent.ogg',
            #'tense': 'data/fairy_lights.ogg'
        }
        self.music_playing = None
        self.mute_snd = False
        self.mute_mus = False

    def music(self, name, loops=-1):
        if not self.pygame.mixer.music.get_busy() and self.music_playing is not name:
            self.pygame.mixer.music.load(self.bank_music[name])
            self.pygame.mixer.music.play(loops)
        self.music_playing = name

    def playlist(self):
        self.music(random.choice(('st1','st2','st3', 'st4', 'st5')), 1)

    def music_stop(self):
        self.pygame.mixer.music.stop()
        self.music_playing = None

    def sound(self, name):
        if not self.mute_snd:
            self.bank_sounds[name].play()