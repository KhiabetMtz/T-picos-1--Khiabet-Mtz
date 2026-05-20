import pygame
import random
import math
import Sprites_pueblo as Sprites

pygame.init()

ANCHO, ALTO = 1000, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("  M I    A L D E A  ")

reloj = pygame.time.Clock()
FPS   = 50

tiempo_dia = 1200   # arrancar en "día" 
MAX_TIEMPO = 6000

def get_sky_color(t):
    fases = [
        (   0, ( 18,  18,  55)),   # noche
        ( 500, (255, 135,  70)),   # amanecer
        (1200, (130, 200, 235)),   # día
        (4500, (255, 155,  55)),   # atardecer
        (5200, ( 75,  55, 115)),   # crepúsculo
        (5600, ( 18,  18,  55)),   # noche
    ]
    for idx in range(len(fases) - 1):
        t0, c0 = fases[idx]
        t1, c1 = fases[idx + 1]
        if t0 <= t < t1:
            alpha = (t - t0) / (t1 - t0)
            return tuple(int(c0[k] + (c1[k] - c0[k]) * alpha) for k in range(3))
    return fases[0][1]

def nombre_fase(t):
    if   t <  500: return 'Noche'
    elif t < 1200: return 'Amanecer'
    elif t < 4500: return 'Dia'
    elif t < 5200: return 'Atardecer'
    elif t < 5600: return 'Crepusculo'
    else:          return 'Noche'

# -------------------------------------------------------
#  Personaje
# -------------------------------------------------------
personaje = Sprites.Personaje(
    2450, 2450, 64, 64,
    'monitoB.png',
    pantalla
)

# -------------------------------------------------------
#  Mapa del pueblo 
# -------------------------------------------------------
tileset_pueblo = Sprites.TileSetPueblo(
    0, 0, 32, 32,
    'Arena_Tileset.png',
    pantalla, 32, 32,
    personaje=personaje,
    archivo_csv=None    
)
obstaculos  = tileset_pueblo.get_obstaculos()
mapa_celdas = tileset_pueblo.get_mapa_celdas()
print(f'[DEBUG] Obstaculos generados: {len(obstaculos)}')

# -------------------------------------------------------
#  Aldeanos simples 
# -------------------------------------------------------
nombres_ald = ['Pico', 'Luna', 'Mochis', 'Dali', 'Benji']
zonas_ald   = [
    (1200, 1200, 350),
    (3800, 1200, 300),
    (1200, 3800, 300),
    (3500, 3500, 380),
    (2500, 900,  270),
]

aldeanos = []
for i, (zx, zy, zr) in enumerate(zonas_ald):
    aldeanos.append(
        Sprites.Aldeano(
            zx, zy, 48, 48,
            vel=1.4 + (i % 3) * 0.3,
            zona_cx=zx, zona_cy=zy, zona_radio=zr,
            pantalla=pantalla,
            personaje=personaje,
            nombre=nombres_ald[i],
            indice_color=i
        )
    )

# -------------------------------------------------------
#  Habitante especial con A*
# -------------------------------------------------------
habitante = Sprites.Habitante(
    2800, 2350, 56, 56,
    vel=2,
    zona_cx=2800, zona_cy=2350, zona_radio=220,
    pantalla=pantalla,
    personaje=personaje,
    nombre='Toni-mon',
    indice_color=3,
    mapa_celdas=mapa_celdas
)

# -------------------------------------------------------
#  Ítems dispersos por el mapa
# -------------------------------------------------------
tipos_item = ['manzana', 'naranja', 'flor', 'concha', 'estrella']
items = []

for _ in range(40):
    intentos = 0
    while intentos < 50:
        intentos += 1
        ix = random.randint(200, 4700)
        iy = random.randint(200, 4700)
        celda  = (ix // 32, iy // 32)
        t_celda = mapa_celdas.get(celda, 0)
        if t_celda in (0, 1, 4):   
            items.append(Sprites.Item(ix, iy, random.choice(tipos_item)))
            break

print(f'[DEBUG] Items colocados: {len(items)}')

# -------------------------------------------------------
#  Fuentes
# -------------------------------------------------------
fuente_hud  = pygame.font.SysFont(None, 20)
fuente_noti = pygame.font.SysFont(None, 26)

# -------------------------------------------------------
#  Notificación temporal
# -------------------------------------------------------
notificacion        = ''
tiempo_notificacion = 0

ICONOS = {
    'manzana': 'Manzana',
    'naranja': 'Naranja',
    'flor':    'Flor',
    'concha':  'Concha',
    'estrella':'Estrella',
}

# -------------------------------------------------------
#  Función HUD
# -------------------------------------------------------
def dibujar_hud():
    # Barra de inventario
    base_x = 10
    base_y = ALTO - 55

    fondo_inv = pygame.Surface(
        (personaje.max_inventario * 34 + 12, 44), pygame.SRCALPHA
    )
    fondo_inv.fill((0, 0, 0, 130))
    pantalla.blit(fondo_inv, (base_x - 6, base_y - 6))

    for k in range(personaje.max_inventario):
        sx = base_x + k * 34
        sy = base_y
        pygame.draw.rect(pantalla, (90, 90, 90),  (sx, sy, 30, 30), 1)
        if k < len(personaje.inventario):
            tipo = personaje.inventario[k]
            c_map = {
                'manzana': (210, 45, 45), 'naranja': (255, 145, 0),
                'flor':    (255, 80,175), 'concha':  (240,215,165),
                'estrella':(255,225, 30),
            }
            pygame.draw.circle(pantalla, c_map.get(tipo,(255,255,255)),
                               (sx + 15, sy + 15), 8)

    # Textos de posición e ítems
    mx, my = personaje.get_pos_mundo()
    pos_txt = fuente_hud.render(
        f'Pos: ({int(mx)}, {int(my)})   Items: {len(personaje.inventario)}/{personaje.max_inventario}',
        True, (255, 255, 200)
    )
    pantalla.blit(pos_txt, (10, ALTO - 72))

    # Controles (esquina superior izquierda)
    controles = [
        'Flechas : mover',
        'Shift   : correr',
        'Espacio : recoger',
        'Esc     : salir',
    ]
    for k, txt in enumerate(controles):
        s = fuente_hud.render(txt, True, (200, 200, 200))
        pantalla.blit(s, (10, 10 + k * 18))

    # Hora del día
    fase_txt = fuente_hud.render(nombre_fase(tiempo_dia), True, (255, 230, 100))
    pantalla.blit(fase_txt, (ANCHO - fase_txt.get_width() - 14, 10))

    # Notificación de ítem recogido
    if notificacion:
        n_surf = fuente_noti.render(notificacion, True, (40, 40, 40))
        nx     = ANCHO // 2 - n_surf.get_width() // 2
        ny     = ALTO  // 2 - 50
        fondo_n = pygame.Surface(
            (n_surf.get_width() + 22, n_surf.get_height() + 12), pygame.SRCALPHA
        )
        fondo_n.fill((255, 245, 190, 215))
        pygame.draw.rect(fondo_n, (195, 175, 120),
                         (0, 0, fondo_n.get_width(), fondo_n.get_height()), 1)
        pantalla.blit(fondo_n, (nx - 11, ny - 6))
        pantalla.blit(n_surf,  (nx,       ny))

    # Estado del habitante especial (para depuración)
    etiq = {
        Sprites.Aldeano.DEAMBULAR: 'DEAMBULANDO',
        Sprites.Aldeano.SALUDAR:   'SALUDANDO',
        Sprites.Aldeano.REGRESAR:  'REGRESANDO',
    }
    hab_txt = fuente_hud.render(
        f'Toni-mon: {etiq.get(habitante.estado, "?")}',
        True, (100, 220, 100)
    )
    pantalla.blit(hab_txt, (10, ALTO - 88))

# =======================================================
#  BUCLE PRINCIPAL
# =======================================================
ejecutar = True

while ejecutar:

    # --- lógica ---
    ejecutar = personaje.muevete(obstaculos=obstaculos)

    recogido = personaje.recoger_item(items)
    if recogido:
        notificacion        = f'+ {ICONOS.get(recogido, recogido).capitalize()} recogida!'
        tiempo_notificacion = 80

    if tiempo_notificacion > 0:
        tiempo_notificacion -= 1
    else:
        notificacion = ''

    for aldeano in aldeanos:
        aldeano.muevete(personaje, tileset_pueblo)

    habitante.muevete(personaje, tileset_pueblo)

    for item in items:
        item.actualizar()

    tiempo_dia = (tiempo_dia + 1) % MAX_TIEMPO

    # --- dibujo ---
    color_cielo = get_sky_color(tiempo_dia)
    pantalla.fill(color_cielo)

    tileset_pueblo.dibujate()

    for item in items:
        item.dibujate(pantalla, personaje.camara_x, personaje.camara_y)

    for aldeano in aldeanos:
        aldeano.dibujate(personaje)

    habitante.dibujate(personaje)

    personaje.dibujate()

    dibujar_hud()

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
