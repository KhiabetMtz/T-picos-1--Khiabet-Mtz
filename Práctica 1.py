import pygame
import sys

pygame.init()

Ancho = 800
Alto = 600 

pantalla = pygame.display.set_mode((Ancho, Alto))
pygame.display.set_caption("Práctica 1")

rosa = (255,182,193)
cafe = (139,69,19)
negro = (0,0,0)

#Rectángulo rosa

ancho_rosa = Ancho // 8
alto_rosa = Alto // 8

rect_rosa = pygame.Rect(0, 0, ancho_rosa, alto_rosa)
rect_rosa.center = (Ancho // 8, Alto // 8)

#Rectángulo café

rect_cafe = pygame.Rect(Ancho -40, 100, 80, 30)

while True: 
    for evento in pygame.event.get ():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pantalla.fill(negro)

    pygame.draw.rect(pantalla, rosa, rect_rosa)
    pygame.draw.rect(pantalla, cafe, rect_cafe)

    pygame.display.flip()