import pygame, sys
from numpy import *
from pygame.locals import *
import scipy
from pymindwave.pyeeg import bin_power
from time import time
fpsClock= pygame.time.Clock()
from random import random, choice

class FeedbackTask:
	def __init__(self):
		font = pygame.font.Font("freesansbold.ttf",20)
		self.title_img = font.render(self.name,False, pygame.Color(255,0,0))

	def process_baseline_recording(raw_values):
		pass

	def frame(self,p,surface):
		surface.blit(self.title_img,(300,50))


class FeedbackGraph:
	def __init__(self):
		self.values = []
		self.times = []

	def insert_value(self,t, value):

		self.values.append(value)
		self.times.append(time())

	def draw_graph(self,surface, scale):
		x = 600
		i = len(self.values)
		if len(self.values)>3:
			while x>0:
				i-=1
				v = self.values[i]
				t = self.times[i]
				x = 500-(time()-t)*10
				y = 400-v*scale
				if i<len(self.values)-1:
					pygame.draw.line(surface, pygame.Color(255,0,0),(x,y),(lx,ly), 5)
				ly = y
				lt = t
				lx = x
				if i==0:
					break


class Attention(FeedbackTask):
	name = "Attention"
	def __init__(self):
		FeedbackTask.__init__(self)
		self.values = []
		self.times = []
		self.graph = FeedbackGraph()

	def process_baseline_recording(raw_values):
		pass

	def frame(self,p, window):
		FeedbackTask.frame(self, p, window)
		value = p.current_attention
		if value>0 and value<=100:
			if len(self.graph.times)==0 or time()>=self.graph.times[-1]+1:
				self.graph.insert_value(time(), value)

		for i in range(6):
			pygame.draw.line(window, pygame.Color(0,0,200),(0,400-i*20*3),(600,400-i*20*3), 2)
		self.graph.draw_graph(window,3.0)


class Meditation(FeedbackTask):
	name = "Meditation"
	def __init__(self):
		FeedbackTask.__init__(self)
		self.values = []
		self.times = []
		self.graph = FeedbackGraph()

	def process_baseline_recording(raw_values):
		pass

	def frame(self,p, window):
		FeedbackTask.frame(self, p, window)
		value = p.current_meditation
		if value>0 and value<=100:
			if len(self.graph.times)==0 or time()>=self.graph.times[-1]+1:
				self.graph.insert_value(time(), value)

		for i in range(6):
			pygame.draw.line(window, pygame.Color(0,0,200),(0,400-i*20*3),(600,400-i*20*3), 2)
		self.graph.draw_graph(window,3.0)



class ThetaLowerTask(FeedbackTask):
	name = "Lower Theta"
	def __init__(self):
		FeedbackTask.__init__(self)
		self.spectra = []
		self.graph = FeedbackGraph()

	def process_baseline_recording(raw_values):
		pass

	def frame(self, p,window):
		flen = 50
		spectrum, relative_spectrum = bin_power(p.raw_values[-p.buffer_len:], range(flen),512)
		self.spectra.append(array(relative_spectrum))
		if len(self.spectra)>30:
			self.spectra.pop(0)
		spectrum = mean(array(self.spectra),axis=0)
		value = (1-sum(spectrum[3:8]))*100
		self.graph.insert_value(time(), value)
		for i in range(6):
			pygame.draw.line(window, pygame.Color(0,0,200),(0,400-i*20*3),(600,400-i*20*3), 2)
		self.graph.draw_graph(window,3.0)



class ThetaIncreaseTask(FeedbackTask):
	name = "Increase Theta"
	def __init__(self):
		FeedbackTask.__init__(self)
		self.spectra = []
		self.graph = FeedbackGraph()
	def process_baseline_recording(raw_values):
		pass
	def frame(self, p,window):
		FeedbackTask.frame(self,p,window)
		flen = 50
		spectrum, relative_spectrum = bin_power(p.raw_values[-p.buffer_len:], range(flen),512)
		self.spectra.append(array(relative_spectrum))
		if len(self.spectra)>10:
			self.spectra.pop(0)
		spectrum = mean(array(self.spectra),axis=0)
		value = (sum(spectrum[3:8] / sum(spectrum[8:40])))*200
		self.graph.insert_value(time(), value)
		for i in range(6):
			pygame.draw.line(window, pygame.Color(0,0,200),(0,400-i*20*3),(600,400-i*20*3), 2)
		self.graph.draw_graph(window,3.0)


tasks = [Attention, Meditation, ThetaLowerTask, ThetaIncreaseTask]

task_keys ={
	K_1: Attention,
	K_2: Meditation,
	K_3: ThetaLowerTask,
	K_4: ThetaIncreaseTask

}

def feedback_menu(window,p):
	quit = False
	font = pygame.font.Font("freesansbold.ttf",20)
	task_images = [font.render("%i: %s" % (i+1, cls.name), False, pygame.Color(255,0,0)) for i,cls in enumerate(tasks)]
	while not quit:
		window.fill(pygame.Color(0,0,0))
		y= 300
		for img in task_images:
			window.blit(img, (400,y))
			y+= img.get_height()
		p.update()
		pygame.display.update()
		for event in pygame.event.get():
			if event.type==QUIT:
				pygame.quit()
				sys.exit()
			if event.type==KEYDOWN:
					if event.key== K_F5:
						pass
					elif event.key == K_ESCAPE:
						quit = True
					elif event.key in task_keys:
						start_session(task_keys[event.key])

def start_session(Task):
	quit = False
	font = pygame.font.Font("freesansbold.ttf",20)
	task = Task()
	while not quit:
		window.fill(pygame.Color(0,0,0))
		p.update()
		for event in pygame.event.get():
			if event.type==QUIT:
				pygame.quit()
				sys.exit()
			if event.type==KEYDOWN:
				if event.key== K_F5:
					pass
				elif event.key == K_ESCAPE:
					quit = True
		task.frame(p,window)
		pygame.display.update()
		fpsClock.tick(20)

if __name__=="__main__":
	pygame.init()

	fpsClock= pygame.time.Clock()

	window = pygame.display.set_mode((1280,720))
	pygame.display.set_caption("PyGame Neurofeedback Trainer")

	from pymindwave.parser import Parser
	p = Parser('/dev/ttyUSB0')
	feedback_menu(window, p)

