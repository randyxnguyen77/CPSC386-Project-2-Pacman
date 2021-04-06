import pygame


class Sound:
    def __init__(self, sound):
        pygame.mixer.init()
        pygame.mixer.music.load(sound)
        pygame.mixer.music.set_volume(0.03)
        self.eat_ghost = pygame.mixer.Sound('sounds/pmaneatghost.wav')
        self.eat_ghost.set_volume(0.08)
        self.eat_fruit = pygame.mixer.Sound('sounds/pmaneatfruit.wav')
        self.eat_fruit.set_volume(0.08)
        self.eat_pellet = pygame.mixer.Sound('sounds/pmanpellets.wav')
        self.eat_pellet.set_volume(0.05)
        self.power_pellet = pygame.mixer.Sound('sounds/powerpellet.wav')
        self.power_pellet.set_volume(0.50)
        self.intro_music = pygame.mixer.Sound('sounds/pmanintro.wav')
        self.intro_music.set_volume(0.10)
        self.death = pygame.mixer.Sound('sounds/pmandeath.wav')
        self.death.set_volume(0.10)
        self.playing_bg = True
        self.play()
        self.pause_bg()

    def pause_bg(self):
        self.playing_bg = False
        pygame.mixer.music.pause()

    def toggle_bg(self):
        self.playing_bg = not self.playing_bg
        self.pause_bg() if not self.playing_bg else self.play()

    def unpause_bg(self):
        self.playing_bg = True
        pygame.mixer.music.unpause()

    def play(self):
        self.playing_bg = True
        pygame.mixer.music.play(-1, 0.0)

    def stop_bg(self):
        self.playing_bg = False
        pygame.mixer.music.stop()

    def eat_pellets(self): pygame.mixer.Sound.play(self.eat_pellet)

    def eat_ghosts(self): pygame.mixer.Sound.play(self.eat_ghost)

    def eat_fruits(self): pygame.mixer.Sound.play(self.eat_fruit)

    def pman_died(self):
        pygame.mixer.stop()
        pygame.mixer.Sound.play(self.death)

    def intro(self): pygame.mixer.Sound.play(self.intro_music)

    def strong_pac(self): pygame.mixer.Sound.play(self.power_pellet)


