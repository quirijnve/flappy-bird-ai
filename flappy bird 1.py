import pygame
import neat
import time
import os
import random


WIN_WIDTH = 500
WIN_HEIGHT = 800

win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "bird1.png"))), 
			pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "bird2.png"))), 
			pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "bg.png")))



class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25
	ROT_VEL = 20
	ANIMATION_TIME = 5

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.tilt = 0
		self.tick_count = 0
		self.vel = 0
		self.height = self.y
		self.img_count = 0
		self.img = self.IMGS[0]

	def jump(self):
		self.vel = -10.5
		self.tick_count = 0
		self.height = self.y

	def move(self):
		self.tick_count += 1

		d = self.vel*self.tick_count + 1.5*self.tick_count**2

		if d >= (16):
			d = 16 #zorgt ervoor dat flappy niet te snel valt

		if d < 0:
			d -= 2 #als je omhoog gaat hoeveel heid omhoog

		self.y =self.y + d

		if d < 0 or self.y < self.height + 50:
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION  #flappy draait wat omhoog
		else:
			if self.tilt > -90:
				self.tilt -= self.ROT_VEL #flappy draait naar beneden

	def draw(self, win):
		self.img_count += 1

		if self.img_count < self.ANIMATION_TIME: #als image count minder is dan 5 laat de eerste flappy bird foto zien
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2: #als image count meer dan 5 minder is dan 10 laat de tweede flappy bird foto zien
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3: #als image count meer dan 10 minder is dan 15 laat de laatste flappy bird foto zien
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4: #als image count meer dan 15 minder is dan 20 laat de tweede flappy bird foto zien
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4 + 1: #als image count 21 is laat de eerste flappy bird foto zien en reset image count naar 0
			self.img = self.IMGS[0]
			self.img_count = 0

		if self.tilt <= -80:
			self.img = self.IMGS[1] #als flappy naar beneden valt laat foto van flappy zien waar de vleugels recht zijn
			self.img_count = self.ANIMATION_TIME*2

		rotated_image = pygame.transform.rotate(self.img, self.tilt) #zorg ervoor dat de foto van flappy om het midden draaid
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(rotated_image, new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)

def draw_window(window, bird):
	win.blit(BG_IMG, (0,0))  #blit betekend teken
	bird.draw(win)
	pygame.display.update()


def main():
    print('test1')
    bird = Bird(200, 200)
    clock = pygame.time.Clock()

    run = True
    print("test")
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        bird.move()
        draw_window(win, bird)

    pygame.quit()
    quit()
main()