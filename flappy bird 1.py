import pygame
import neat
import time
import os
import random
import pickle


pygame.font.init()  # init font

WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 0

win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "bird1.png"))), 
			pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "bird2.png"))), 
			pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("E:/PY/files/flappy_bird/imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsansms", 40)

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
		return pygame.mask.from_surface(self.img) #geeft een lijst waar pixels zijn in de foto

class Pipe:
	GAP = 200
	VEL = 5

	def __init__(self, x):
		self.x = x
		self.height = 0

		self.top = 0  #variable voor waar bovenkant van pipe wordt getekend
		self.bottom = 0 #en voor onderkant van pipe
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)  #foto van pipe opstekop voor boven
		self.PIPE_BOTTOM = PIPE_IMG #foto voor beneden pipe

		self.passed = False
		self.set_height()
	
	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height() #zorgt ervoor dat de pipe in goed positie is want top left is de orgin van pijp
		self.bottom = self.height + self.GAP
	
	def move(self):
		self.x -= self.VEL #flappy gaat vooruit (pipe beweegt naar achter)

	def draw(self, win): #teken boven en onder pipe
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	def collide(self, bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP) #geeft een lijst waar pixels zijn in de foto
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) #geeft een lijst waar pixels zijn in de foto

		top_offset = (self.x - bird.x, self.top - round(bird.y)) #berekend de afstand tussen de mask en orgin
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset) #vertelt het punt van waar de masks elkaar aanraken
		t_point = bird_mask.overlap(top_mask, top_offset)

		if t_point or b_point: #als b_point niet none doorgeevd dus ze botsen, return true, ander False
			return True
		
		return False

class Base:
	VEL = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__ (self, y):
		self.y = y
		self.x1 = 0 #foto 1 start bij x = 0
		self.x2 = self.WIDTH #foto 2 achter de eerste

	def move(self): #we hebben 2 fotos van base achterelkaar, ze schuiven beide, als de eerste axter de y as komt, kleiner is dan 0 wordt die verplaatst naar achter de andere foto van de base,
		self.x1 -= self.VEL #zo lijkt het dat de grond beweegt zonder een hele grote foto te hebben
		self.x2 -= self.VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH
		
		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH
	
	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))




def draw_window(window, birds, pipes, base, score, gen):
	win.blit(BG_IMG, (0,0))  #blit betekend teken
	for pipe in pipes:
		pipe.draw(win)
	
	text = STAT_FONT.render("Score: " + str(score), 1,(255,255,255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))  #plaats waar de score moet staan

	text = STAT_FONT.render("Gen: " + str(gen), 1,(255,255,255))
	win.blit(text, (10, 10))

	base.draw(win)
	for bird in birds:
		bird.draw(win)
	
	pygame.display.update()


def main(genomes, config):
	global GEN
	GEN += 1
	nets = []
	ge = []
	birds = []

	for _, g in genomes: #meerdere genomes zijn neuralnetworks
		net = neat.nn.FeedForwardNetwork.create(g, config) #maken nuralnetwork aan voor genome
		nets.append(net)	#voegen het toe aan de lijst
		birds.append(Bird(230, 350))	#voeg bird ook aan de lijst
		g.fitness = 0
		ge.append(g)  #genoma ook toevoegen aan de lijst

	base = Base(730)
	pipes = [Pipe(600)]
	clock = pygame.time.Clock()
	
	score = 0
	
	run = True
	while run:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
		
		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): #kijkt naar welke pipe de neural network moet kijken
				pipe_ind = 1
		else:
			run = False #als er geen vogels meer zijn stop
			break

		for x, bird in enumerate(birds):
			bird.move()
			ge[x].fitness += 0.1  # geeft bird 1 fitnespoint per seconde

			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom))) #geeft output

			if output[0] > 0.5: #als output boven 0.5 is Spring
				bird.jump()
		
		#bird.move()
		add_pipe = False
		rem = [] #lijst om dingen te verwijderen
		
		for pipe in pipes:
			for x, bird in enumerate(birds):
				if pipe.collide(bird): #als botsing
					ge[x]. fitness -= 1 #zorgt ervoor als een bird een pipe raakt gaat zijn fitness score omlaag
					birds.pop(x)
					nets.pop(x)
					ge.pop(x) #zorgt ervoor dat ale een bird een pipe raakt verwijderd wordt
			
				if not pipe.passed and pipe.x < bird.x: #kijkt of we langs de pipe zijn geweest, doorheen zijn gegaan
					pipe.passed = True 
					add_pipe = True # maak een nieuwe pipe aan
			
			if pipe.x + pipe.PIPE_TOP.get_width() < 0: #als de pipe weg is van het scherm
				rem.append(pipe) #verwijder pipe


			pipe.move()

		if add_pipe:
			score += 1 #score + 1
			for g in ge:
				g.fitness += 5 # als een bird door eenn pipe gaat krijgt ie 5 punter bij zn fitness
			pipes.append(Pipe(600)) #maak nieuwe pipe op afstand van ()

		for r in rem:
			pipes.remove(r) 

		for x, bird in enumerate(birds):
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)  #haalt bird weg als die grond raakt of plafond

		base.move() #beweeg base
		draw_window(win, birds, pipes, base, score, GEN)





def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
						 neat.DefaultSpeciesSet, neat.DefaultStagnation,
						 config_path)  #geeft de belangrijke instellingen van Neat

	p = neat.Population(config)	 #creeert population

	p.add_reporter(neat.StdOutReporter(True)) #geeft statestieken in console
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(main,10000) #hoeveelheid generations in fitnesfunction 



if __name__ == "__main__":
	local_dir = "E:/PY/files/flappy_bird/"
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)