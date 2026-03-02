import pygame
import Sprites 

pygame.init()
pantalla = pygame.display.set_mode((1000,700))
reloj = pygame.time.Clock()

enemigos = [] 
num_enemigos = 20

for i in range(num_enemigos):
    enemigos.append(Sprites.Enemigo(100, (i * 20), 30, 30, i, 1, 600 - (i * 20), pantalla))
                
personaje = Sprites.personaje(0, 0, 200, 200, pantalla)

ejecutar = True

while ejecutar:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutar = False

    personaje.muevete()                 
    personaje.rect.clamp_ip(pantalla.get_rect())

    for enemigo in enemigos:
        enemigo.muevete(personaje)

        #if personaje.detectacolision(enemigos[i]):
            #print("colision")

    #ejecutar = personaje.muevete()
    pantalla.fill((0, 0, 0))

    #keys = pygame.key.get_pressed()
    
    for enemigo in enemigos:
        enemigo.dibujate()
        
    personaje.dibujate()

    pygame.display.update() 

    pygame.time.wait(50)

pygame.quit()   
