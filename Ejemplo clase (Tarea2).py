import pygame
import Sprites

pygame.init()
pantalla = pygame.display.set_mode((800, 600))
reloj = pygame.time.Clock()

ejecutando = True

sprite1 = Sprites.Sprite(100, 100, 50, 50, pantalla)
enemigo1 = Sprites.Enemigo(100, 200, 50, 50, 50, 600, pantalla)
enemigo2 = Sprites.Enemigo(400, 450, 30, 30, 100, 700, pantalla)
personaje1 = Sprites.Personaje(200, 300, 50, 50, pantalla)

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        personaje1.manejar_evento(evento)

    enemigo1.muevete()
    enemigo2.muevete() 
    
    if personaje1.detecta_colision(enemigo1):
        print("¡COLISIÓN DETECTADA!")
 
    pantalla.fill((0, 0, 0))
    sprite1.dibujate()
    enemigo1.dibujate()
    enemigo2.dibujate()
    personaje1.dibujate()
    

    pygame.display.update() 

    reloj.tick(60)

pygame.quit()
