import pygame
import Sprites 

pygame.init()

ANCHO, ALTO = 1000, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Arena + Personaje + Murciélagos")

reloj = pygame.time.Clock()
FPS = 30

DEBUG_BOXES = True
DEBUG_OBST  = True


#mapa
Tileset_arena = Sprites.TileSetArena(
    0, 0, 32, 32,
    'Arena_Tileset.png',
    pantalla, 32, 32
)
obstaculos = Tileset_arena.get_obstaculos()

#personaje
personaje = Sprites.personaje(100, 600, 64, 64, pantalla,archivo_imagen_personaje='monitoB.png')

#enemigos
enemigos = [] 
num_enemigos = 12


for i in range(num_enemigos):
    x = 60 + i * 70
    y = 40 + (i % 3) * 25
    enemigos.append(
        Sprites.Enemigo(
            x, y, 48, 48,
            vel=2 + (i % 2),
            x_min=20,
            x_max = ANCHO - 80,
            pantalla=pantalla,
            archivo_imagen_enemigo='Bat_Sprites.png'
        )
    )

#controles
fuente = pygame.font.SysFont('monitoB', 13)
controles = [
    "w/a/s/d  ->  mover",
    "j        ->  espada",
    "k        ->  arco",
    "l        ->  morir",
]

ejecutar = True
while ejecutar:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutar = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                ejecutar = False

#logica
    personaje.muevete(obstaculos)           
    personaje.rect.clamp_ip(pantalla.get_rect())

    for enemigo in enemigos:
        enemigo.muevete(personaje)

    #dibujo
    pantalla.fill((0, 0, 0))
    pantalla.blit(Tileset_arena.getImagen(), (0, 0))

    #obstáculos 
    if DEBUG_OBST:
        for obs in obstaculos:
            pygame.draw.rect(pantalla, (120, 120, 120), obs, 2)

    for enemigo in enemigos:
        enemigo.dibujate()
        if DEBUG_BOXES:
            pygame.draw.rect(pantalla, (255, 255, 0), enemigo.rect, 1)

    personaje.dibujate()
    if DEBUG_BOXES:
        pygame.draw.rect(pantalla, (0, 200, 255), personaje.rect, 1)

    for idx, texto in enumerate(controles):
        surf = fuente.render(texto, True, (200, 200, 200))
        pantalla.blit(surf, (10, 10 + idx * 16))


    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()   

