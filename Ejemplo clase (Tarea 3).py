import pygame
from pygame.key import ScancodeWrapper
import Sprites

pygame.init()
pantalla = pygame.display.set_mode((800, 600))
reloj = pygame.time.Clock()

enemigos = [] 
num_enemigos = 20

for i in range(num_enemigos):
    enemigos.append(Sprites.Enemigo(100, (i * 20), 30, 30, i, 1, 600 - (i * 20), pantalla))
                
personaje = Sprites.personaje(400,300,25,25,pantalla)

ejecutando = True

while ejecutando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False  

    for i in range(num_enemigos):
        enemigos[i].muevete()

        if personaje.detectacolision(enemigos[i]):
            print("colision")


    keys = pygame.key.get_pressed()
    personaje.muevete()

    
    pantalla.fill((0, 0, 0))
    
    for i in range(num_enemigos): 
        enemigos[i].dibujate(0,100,200)
        
    personaje.dibujate(128,0,128)

    pygame.display.update() 

    reloj.tick(60)

pygame.quit()
