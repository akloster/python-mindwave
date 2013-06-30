import pygame, sys
from numpy import *
from pygame.locals import *
import scipy
from pymindwave.pyeeg import bin_power

pygame.init()

fpsClock= pygame.time.Clock()

window = pygame.display.set_mode((1280,720))
pygame.display.set_caption("Mindwave Viewer")

from pymindwave.parser import Parser

p = Parser('/dev/ttyUSB0')

blackColor = pygame.Color(0,0,0)
redColor = pygame.Color(255,0,0)
greenColor = pygame.Color(0,255,0)
deltaColor = pygame.Color(100,0,0)
thetaColor = pygame.Color(0,0,255)
alphaColor = pygame.Color(255,0,0)
betaColor = pygame.Color(0,255,00)
gammaColor = pygame.Color(0,255,255)


background_img = pygame.image.load("sdl_viewer_background.png")


font = pygame.font.Font("freesansbold.ttf",20)
raw_eeg = True
spectra = []
iteration = 0

meditation_img = font.render("Meditation", False, redColor)
attention_img = font.render("Attention", False, redColor)

record_baseline = False

while True:
	p.update()
	#window.blit(background_img,(0,0))
	if p.sending_data:
		iteration+=1

		flen = 50

		if len(p.raw_values)>=500:
			spectrum, relative_spectrum = bin_power(p.raw_values[-p.buffer_len:], range(flen),512)
			spectra.append(array(relative_spectrum))
			if len(spectra)>30:
				spectra.pop(0)

			spectrum = mean(array(spectra),axis=0)
			for i in range (flen-1):
				value = float(spectrum[i]*1000)
				if i<3:
					color = deltaColor
				elif i<8:
					color = thetaColor
				elif i<13:
					color = alphaColor
				elif i<30:
					color = betaColor
				else:
					color = gammaColor
				pygame.draw.rect(window, color, (25+i*10,400-value, 5,value))
		else:
			pass
		pygame.draw.circle(window,redColor, (800,200),p.current_attention/2)
		pygame.draw.circle(window,greenColor, (800,200),60/2,1)
		pygame.draw.circle(window,greenColor, (800,200),100/2,1)
		window.blit(attention_img, (760,260))
		pygame.draw.circle(window,redColor, (700,200),p.current_meditation/2)
		pygame.draw.circle(window,greenColor, (700,200),60/2,1)
		pygame.draw.circle(window,greenColor, (700,200),100/2,1)

		window.blit(meditation_img, (600,260))
		if len(p.current_vector)>7:
			m = max(p.current_vector)
			for i in range(7):
				value = p.current_vector[i] *100.0/m
				pygame.draw.rect(window, redColor, (600+i*30,450-value, 6,value))

		if raw_eeg:
			lv = 0
			for i,value in enumerate(p.raw_values[-1000:]):
				v = value/ 255.0/ 5
				pygame.draw.line(window, redColor, (i+25,500-lv),(i+25, 500-v))
				lv = v
	else:
                img = font.render("Mindwave Headset is not sending data... Press F5 to autoconnect or F6 to disconnect.", False, redColor)
                window.blit(img,(100,100))
		pass

	for event in pygame.event.get():
		if event.type==QUIT:
			pygame.quit()
			sys.exit()
		if event.type==KEYDOWN:
			if event.key== K_F5:
				p.write_serial("\xc2")
			elif event.key== K_F6:
				p.write_serial("\xc1")
			elif event.key==K_ESCAPE:
				pygame.quit()
				sys.exit()
			elif event.key == K_F7:
				record_baseline = True
				p.start_raw_recording("baseline_raw.csv")
				p.start_esense_recording("baseline_esense.csv")
			elif event.key == K_F8:
				record_baseline = False
				p.stop_esense_recording()
				p.stop_raw_recording()
	pygame.display.update()
	fpsClock.tick(30)
