import pygame, random, math
import Sprites_pueblo as Sprites

pygame.init()
ANCHO, ALTO = 1000, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("  M I   A L D E A  ")
reloj = pygame.time.Clock(); FPS = 50

# Gestor de sprites del tileset exterior.png 
gestor_spr = Sprites.SpritesExterior(
    archivo='exterior.png', pantalla=pantalla,
    archivo_arboles='arboles.png',
    archivo_piedras='piedras.png',
    archivo_piedritas='piedritas.png',
    archivo_casa='casa.png',
    archivo_puente='puente.png'
)

# Ciclo día/noche 
tiempo_dia = 1200          # arranca en "día"
MAX_TIEMPO = 6000

def get_ocean_color(t):
    """Color del océano/fondo exterior al mapa según la hora."""
    fases = [(0,(8,28,72)),(500,(30,90,160)),(1200,(50,140,210)),
             (4500,(25,80,140)),(5200,(15,50,110)),(5600,(8,28,72))]
    for k in range(len(fases)-1):
        t0,c0=fases[k]; t1,c1=fases[k+1]
        if t0<=t<t1:
            a=(t-t0)/(t1-t0); return tuple(int(c0[i]+(c1[i]-c0[i])*a) for i in range(3))
    return fases[0][1]

def nombre_fase(t):
    if   t<500:  return 'Noche'
    elif t<1200: return 'Amanecer'
    elif t<4500: return 'Dia'
    elif t<5200: return 'Atardecer'
    elif t<5600: return 'Crepusculo'
    else:        return 'Noche'

def get_fase(t): return 'dia' if 1200<=t<4500 else 'noche'

# ── Inicializar entidades ─────────────────────────────────────
personaje = Sprites.Personaje(2450, 2450, 64, 64, 'monitoB.png', pantalla)

# TileSetPueblo recibe el gestor_spr para usar árboles y rocas del tileset
tileset_pueblo = Sprites.TileSetPueblo(
    0,0,32,32,'Arena_Tileset.png',pantalla,32,32,
    personaje=personaje, archivo_csv=None,
    gestor_spr=gestor_spr
)
obstaculos  = tileset_pueblo.get_obstaculos()
mapa_celdas = tileset_pueblo.get_mapa_celdas()
print(f'[DEBUG] Obstáculos: {len(obstaculos)}')

# Aldeanos
NOMBRES = ['Pico','Luna','Mochi','Dali','Benji']
ZONAS   = [(1200,1200,350),(3800,1200,300),(1200,3800,300),(3500,3500,380),(2500,900,270)]
aldeanos = [
    Sprites.Aldeano(zx,zy,48,48,1.4+(i%3)*0.3,zx,zy,zr,pantalla,personaje,NOMBRES[i],i)
    for i,(zx,zy,zr) in enumerate(ZONAS)
]

# Habitante con A*
habitante = Sprites.Habitante(2800,2350,56,56,2,2800,2350,220,pantalla,personaje,
                               'Toni',3,mapa_celdas)

# Ítems normales al inicio
TIPOS_NORMALES = ['manzana','naranja','flor','concha','estrella']
items = []
for _ in range(35):
    for _ in range(50):
        ix,iy = random.randint(200,4700), random.randint(200,4700)
        if mapa_celdas.get((ix//32,iy//32),0) in (0,1,4):
            items.append(Sprites.Item(ix,iy,random.choice(TIPOS_NORMALES),'ambas')); break

# Construcciones colocadas por el jugador
construcciones = []

# Objetivo inicial
fase_actual = get_fase(tiempo_dia)
objetivo    = Sprites.Objetivo(fase_actual, 0)

# Fuentes HUD 
fuente   = pygame.font.SysFont(None, 20)
fuente_n = pygame.font.SysFont(None, 24)
notificacion        = ''
tiempo_notificacion = 0

# Funciones del juego 
def spawn_items_de_fase(fase, n=5):
    tipos_v = ['sol_cristal','flor_dorada'] if fase=='dia' else ['luna_piedra','estrella_fugaz']
    spawnados = 0; intentos = 0
    while spawnados < n and intentos < 200:
        intentos += 1
        ix,iy = random.randint(200,4700), random.randint(200,4700)
        if mapa_celdas.get((ix//32,iy//32),0) in (0,1,4):
            items.append(Sprites.Item(ix,iy,random.choice(tipos_v),fase))
            spawnados += 1

def intentar_intercambio_con_npcs():
    global notificacion, tiempo_notificacion
    mx,my = personaje.get_pos_mundo()
    for npc in aldeanos + [habitante]:
        if npc.estado == Sprites.Aldeano.SALUDAR:
            dist = math.hypot(mx-npc.pos_x_mundo, my-npc.pos_y_mundo)
            if dist < 110 and npc.puede_intercambiar(personaje):
                npc.ejecutar_intercambio(personaje)
                notificacion = f'+1 {npc.trade_offer["da"]}!'
                tiempo_notificacion = 90; return
            elif dist < 110:
                t = npc.trade_offer
                notificacion = f'Necesitas {t["cantidad"]} {t["quiere"]}'
                tiempo_notificacion = 70; return

def intentar_interaccion_entorno():
    global notificacion, tiempo_notificacion
    tipo_tile, tx, ty = tileset_pueblo.tile_cercano_interactuable(personaje)
    if tipo_tile == 2:        # árbol → madera
        tileset_pueblo.modificar_tile(tx, ty)
        ganado = random.randint(2, 4)
        personaje.recursos['madera'] = personaje.recursos.get('madera',0) + ganado
        notificacion = f'+{ganado} madera 🪵'; tiempo_notificacion = 70
    elif tipo_tile == 5:      # roca GRANDE → mucha piedra (5-8)
        tileset_pueblo.modificar_tile(tx, ty)
        ganado = random.randint(5, 8)
        personaje.recursos['piedra'] = personaje.recursos.get('piedra',0) + ganado
        notificacion = f'+{ganado} piedra ⛏ (roca grande)'; tiempo_notificacion = 70
    elif tipo_tile == 6:      # piedrita pequeña → poca piedra (1-2)
        tileset_pueblo.modificar_tile(tx, ty)
        ganado = random.randint(1, 2)
        personaje.recursos['piedra'] = personaje.recursos.get('piedra',0) + ganado
        notificacion = f'+{ganado} piedra (piedrita)'; tiempo_notificacion = 70
    else:
        intentar_intercambio_con_npcs()

def intentar_construccion():
    global notificacion, tiempo_notificacion
    tipo = personaje.modo_construccion
    rec  = Sprites.Construccion.RECETAS[tipo]
    faltan = {r:n for r,n in rec.items() if personaje.recursos.get(r,0)<n}
    if faltan:
        partes = [f'{n} {r}' for r,n in faltan.items()]
        notificacion = f'Faltan: {", ".join(partes)}'; tiempo_notificacion = 80; return
    for r,n in rec.items():
        personaje.recursos[r] -= n
    mx,my = personaje.get_pos_mundo()
    nueva = Sprites.Construccion(mx+72, my-20, tipo, pantalla, gestor_spr)
    construcciones.append(nueva)
    personaje.construcciones[tipo] = personaje.construcciones.get(tipo,0) + 1
    # Si es puente → abrir paso en el río donde se colocó
    if tipo == 'puente':
        tileset_pueblo.abrir_paso_rio(mx+72, my-20, ancho_px=96)
        notificacion = 'Puente construido! Puedes cruzar el rio'
    else:
        notificacion = f'Construiste: {tipo}!'
    tiempo_notificacion = 120

def dibujar_hud():
    # Inventario
    bx,by = 10, ALTO-55
    fondo_inv = pygame.Surface((personaje.max_inventario*34+12,44),pygame.SRCALPHA)
    fondo_inv.fill((0,0,0,130)); pantalla.blit(fondo_inv,(bx-6,by-6))
    for k in range(personaje.max_inventario):
        sx=bx+k*34; pygame.draw.rect(pantalla,(90,90,90),(sx,by,30,30),1)
        if k<len(personaje.inventario):
            c=Sprites.Item.COLORES.get(personaje.inventario[k],(255,255,255))
            pygame.draw.circle(pantalla,c,(sx+15,by+15),8)

    # Recursos, controles, modo construcción
    rec_txt = fuente.render(
        f'Madera:{personaje.recursos.get("madera",0)}  '
        f'Piedra:{personaje.recursos.get("piedra",0)}  '
        f'[E]=talar/minar/canjear  [B]=construir({personaje.modo_construccion})  [N]=cambiar',
        True,(220,220,200))
    pantalla.blit(rec_txt,(10,ALTO-80))

    # Posición y conteo de ítems
    mx,my=personaje.get_pos_mundo()
    pantalla.blit(fuente.render(
        f'Pos:({int(mx)},{int(my)})  Items:{len(personaje.inventario)}/{personaje.max_inventario}',
        True,(255,255,200)),(10,ALTO-97))

    # Controles básicos (esquina superior izquierda)
    for k,txt in enumerate([
        'Flechas: mover',
        'Shift: correr',
        'Espacio: recoger item',
        'E: talar arbol / minar roca / canjear con aldeano',
        'B: construir  |  N: cambiar (casa/puente)',
        'Esc: salir',
    ]):
        pantalla.blit(fuente.render(txt,True,(220,220,220)),(10,10+k*18))

    # Fase del día (esquina superior derecha)
    fase_surf=fuente.render(f'{nombre_fase(tiempo_dia)} — {fase_actual.upper()}',True,(255,230,100))
    pantalla.blit(fase_surf,(ANCHO-fase_surf.get_width()-14,10))

    # Objetivo (centro superior)
    color_obj = (120,255,120) if objetivo.completado else (255,240,80)
    check = '✓' if objetivo.completado else '►'
    obj_surf = fuente.render(f'{check} OBJETIVO: {objetivo.desc}',True,color_obj)
    pantalla.blit(obj_surf,(ANCHO//2-obj_surf.get_width()//2,10))
    trades_surf = fuente.render(
        f'Trades:{personaje.trades_realizados}/{objetivo.trades_req}',
        True,(200,200,200))
    pantalla.blit(trades_surf,(ANCHO//2-trades_surf.get_width()//2,28))

    # Notificación central flotante
    if notificacion:
        n_surf=fuente_n.render(notificacion,True,(30,30,30))
        nx=ANCHO//2-n_surf.get_width()//2; ny=ALTO//2-60
        fd=pygame.Surface((n_surf.get_width()+20,n_surf.get_height()+10),pygame.SRCALPHA)
        fd.fill((255,245,190,220))
        pygame.draw.rect(fd,(195,175,120),(0,0,fd.get_width(),fd.get_height()),1)
        pantalla.blit(fd,(nx-10,ny-5)); pantalla.blit(n_surf,(nx,ny))

    # Estado de Toni
    etiq={0:'DEAMBULANDO',1:'SALUDANDO',2:'REGRESANDO'}
    pantalla.blit(fuente.render(f'Toni:{etiq.get(habitante.estado,"?")}',True,(100,220,100)),(10,ALTO-113))

# Bucle principal 
fase_anterior = fase_actual
spawn_items_de_fase(fase_actual, n=6)   # ítems de valor iniciales

# Árbol nuevo cada ~8 segundos (400 frames a 50fps)
tiempo_crecimiento    = 0
INTERVALO_CRECIMIENTO = 400

ejecutar = True
while ejecutar:

    # 1. Mover personaje + leer teclado
    ejecutar = personaje.muevete(obstaculos=obstaculos)

    # 2. Tecla E → talar / minar / intercambiar
    if personaje.interactuar_activo:
        intentar_interaccion_entorno()

    # 3. Tecla B → construir casa o puente
    if personaje.construir_activo:
        intentar_construccion()

    # 4. Tecla ESPACIO → recoger ítem
    recogido = personaje.recoger_item(items, fase_actual)
    if recogido:
        notificacion = f'+{recogido}'; tiempo_notificacion = 70

    # 5. Mover NPCs
    for ald in aldeanos:
        ald.muevete(personaje, tileset_pueblo)
    habitante.muevete(personaje, tileset_pueblo)

    # 6. Actualizar brillo de ítems
    for item in items:
        item.actualizar()

    # 7. Crecer árbol nuevo periódicamente
    tiempo_crecimiento += 1
    if tiempo_crecimiento >= INTERVALO_CRECIMIENTO:
        tiempo_crecimiento = 0
        tileset_pueblo.crecer_arbol_aleatorio()

    # 8. Avanzar ciclo día/noche
    tiempo_dia = (tiempo_dia + 1) % MAX_TIEMPO
    fase_actual = get_fase(tiempo_dia)

    # 9. ¿Cambió la fase? → FIN DE CICLO DE FASE
    if fase_actual != fase_anterior:
        fase_anterior = fase_actual
        spawn_items_de_fase(fase_actual, n=6)
        personaje.trades_realizados = 0
        for ald in aldeanos + [habitante]:
            ald.actualizar_fase(fase_actual)
        objetivo = Sprites.Objetivo(fase_actual, 0)
        notificacion = f'¡Nueva fase: {fase_actual.upper()}! Objetivo actualizado'
        tiempo_notificacion = 130

    # 10. FIN DE CICLO DIARIO
    if objetivo.verificar(personaje) and tiempo_notificacion == 0:
        notificacion = '¡Objetivo completado! +10 madera +5 piedra'
        tiempo_notificacion = 150
        personaje.recursos['madera'] = personaje.recursos.get('madera',0) + 10
        personaje.recursos['piedra'] = personaje.recursos.get('piedra',0) + 5
        objetivo = objetivo.siguiente()

    # Timer notificación
    if tiempo_notificacion > 0: tiempo_notificacion -= 1
    else: notificacion = ''

    # Dibujar Océano 
    pantalla.fill(get_ocean_color(tiempo_dia))

    # Mapa del pueblo (encima del océano)
    tileset_pueblo.dibujate()

    # (árboles y rocas reales, uno por tile, sin repetición)
    tileset_pueblo.dibujate_sprites_exteriores(
        pantalla, personaje.camara_x, personaje.camara_y)

    # Overlay animado del lago (color varía con la hora)
    tileset_pueblo.dibujate_agua_dinamica(
        pantalla, personaje.camara_x, personaje.camara_y, tiempo_dia)

    # Ítems coleccionables
    for item in items:
        item.dibujate(pantalla, personaje.camara_x, personaje.camara_y, fase_actual)

    # Construcciones 
    for const in construcciones:
        const.dibujate(personaje.camara_x, personaje.camara_y)

    # NPCs
    for ald in aldeanos:
        ald.dibujate(personaje)
    habitante.dibujate(personaje)

    # Personaje
    personaje.dibujate()

    # HUD
    dibujar_hud()

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()