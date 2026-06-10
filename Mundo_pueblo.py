import pygame, random, math
import Sprites_pueblo as Sprites

pygame.init()
ANCHO, ALTO = 1000, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("  M I   A L D E A  ")
reloj = pygame.time.Clock(); FPS = 50

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

# Inicializar entidades 
personaje = Sprites.Personaje(2450, 1450, 64, 64, 'monitoB.png', pantalla)

# TileSetPueblo 
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

# Construcciones 
construcciones = []

# Objetivo inicial
fase_actual = get_fase(tiempo_dia)
objetivo    = Sprites.Objetivo(fase_actual, 0)

# Fuentes HUD (negrita para mayor legibilidad)
fuente   = pygame.font.SysFont('arial', 16, bold=True)
fuente_n = pygame.font.SysFont('arial', 20, bold=True)
notificacion        = ''
tiempo_notificacion = 0

# Texto con contorno: máximo contraste sobre cualquier fondo 
def texto_contraste(texto, fuente_obj, color=(255,255,255), color_borde=(0,0,0)):
    """Renderiza texto con contorno negro de 2px para que siempre
    sea legible sobre cualquier fondo."""
    base = fuente_obj.render(texto, True, color)
    borde = fuente_obj.render(texto, True, color_borde)
    w, h = base.get_size()
    surf = pygame.Surface((w+4, h+4), pygame.SRCALPHA)
    for dx in (-2,-1,0,1,2):
        for dy in (-2,-1,0,1,2):
            if dx or dy:
                surf.blit(borde, (dx+2, dy+2))
    surf.blit(base, (2, 2))
    return surf

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
                personaje.recaudado_total['trades'] += 1   # total histórico
                notificacion = f'+1 {npc.trade_offer["da"]}!'
                tiempo_notificacion = 90; return
            elif dist < 110:
                t = npc.trade_offer
                notificacion = f'Necesitas {t["cantidad"]} {t["quiere"]}'
                tiempo_notificacion = 70; return

def intentar_interaccion_entorno():
    global notificacion, tiempo_notificacion
    tipo_tile, tx, ty = tileset_pueblo.tile_cercano_interactuable(personaje)
    if tipo_tile == 2:        # madera
        tileset_pueblo.modificar_tile(tx, ty)
        ganado = random.randint(2, 4)
        personaje.recursos['madera'] = personaje.recursos.get('madera',0) + ganado
        personaje.recaudado_total['madera'] += ganado
        notificacion = f'+{ganado} madera'; tiempo_notificacion = 70
    elif tipo_tile == 5:      # roca GRANDE
        tileset_pueblo.modificar_tile(tx, ty)
        ganado = random.randint(5, 8)
        personaje.recursos['piedra'] = personaje.recursos.get('piedra',0) + ganado
        personaje.recaudado_total['piedra'] += ganado
        notificacion = f'+{ganado} piedra (roca grande)'; tiempo_notificacion = 70
    elif tipo_tile == 6:      # piedrita pequeña 
        tileset_pueblo.modificar_tile(tx, ty)
        ganado = random.randint(1, 2)
        personaje.recursos['piedra'] = personaje.recursos.get('piedra',0) + ganado
        personaje.recaudado_total['piedra'] += ganado
        notificacion = f'+{ganado} piedra (piedrita)'; tiempo_notificacion = 70
    else:
        intentar_intercambio_con_npcs()

def hay_agua_cerca(mundo_x, mundo_y, radio_tiles=2):
    tw = tileset_pueblo.rect.width
    btx, bty = int(mundo_x // tw), int(mundo_y // tw)
    mejor = None; mejor_d = 1e9
    for dx in range(-radio_tiles, radio_tiles + 1):
        for dy in range(-radio_tiles, radio_tiles + 1):
            tx, ty = btx + dx, bty + dy
            if mapa_celdas.get((tx, ty), 0) == 3:
                cx = tx * tw + tw // 2
                cy = ty * tw + tw // 2
                d = (cx - mundo_x) ** 2 + (cy - mundo_y) ** 2
                if d < mejor_d:
                    mejor_d = d; mejor = (cx, cy)
    return mejor

def intentar_construccion():
    global notificacion, tiempo_notificacion
    tipo = personaje.modo_construccion
    rec  = Sprites.Construccion.RECETAS[tipo]
    faltan = {r:n for r,n in rec.items() if personaje.recursos.get(r,0)<n}
    if faltan:
        partes = [f'{n} {r}' for r,n in faltan.items()]
        notificacion = f'Faltan: {", ".join(partes)}'; tiempo_notificacion = 80; return

    mx,my = personaje.get_pos_mundo()

    # El puente solo se puede construir junto al agua
    if tipo == 'puente':
        centro_agua = hay_agua_cerca(mx, my, radio_tiles=2)
        if centro_agua is None:
            notificacion = 'Acercate al agua para construir el puente'
            tiempo_notificacion = 90; return
        # cobrar recursos
        for r,n in rec.items():
            personaje.recursos[r] -= n
        bx, by = centro_agua
        # colocar el sprite centrado sobre el agua
        nueva = Sprites.Construccion(bx - 85, by - 71, tipo, pantalla, gestor_spr)
        construcciones.append(nueva)
        personaje.construcciones[tipo] = personaje.construcciones.get(tipo,0) + 1
        personaje.recaudado_total['construcciones'] += 1
        # abrir paso transitable sobre la franja
        tileset_pueblo.abrir_paso_rio(bx, by, ancho_px=100)
        notificacion = 'Puedes cruzar el rio'
        tiempo_notificacion = 120
        return

    # Casa 
    for r,n in rec.items():
        personaje.recursos[r] -= n
    nueva = Sprites.Construccion(mx+72, my-20, tipo, pantalla, gestor_spr)
    construcciones.append(nueva)
    personaje.construcciones[tipo] = personaje.construcciones.get(tipo,0) + 1
    personaje.recaudado_total['construcciones'] += 1
    notificacion = f'Construiste: {tipo}!'
    tiempo_notificacion = 120

def intentar_demolicion():
    global notificacion, tiempo_notificacion
    if not construcciones:
        notificacion = 'No hay nada que demoler cerca'
        tiempo_notificacion = 70; return
    mx, my = personaje.get_pos_mundo()
    # construcción más cercana dentro de un radio
    mejor = None; mejor_d = 1e9
    for c in construcciones:
        cx = c.rect.x + c.rect.width // 2
        cy = c.rect.y + c.rect.height // 2
        d = (cx - mx) ** 2 + (cy - my) ** 2
        if d < mejor_d:
            mejor_d = d; mejor = c
    if mejor is None or mejor_d > 160 ** 2:  
        notificacion = 'Acercate a una construccion para demoler'
        tiempo_notificacion = 80; return
    # devolver la mitad de los materiales
    rec = Sprites.Construccion.RECETAS[mejor.tipo]
    for r, n in rec.items():
        personaje.recursos[r] = personaje.recursos.get(r, 0) + n // 2
    # si era puente, cerrar el paso con agua otra vez
    if mejor.tipo == 'puente':
        cx = mejor.rect.x + mejor.rect.width // 2
        cy = mejor.rect.y + mejor.rect.height // 2
        tileset_pueblo.cerrar_paso_rio(cx, cy, ancho_px=100) 
    construcciones.remove(mejor)
    personaje.construcciones[mejor.tipo] = max(0, personaje.construcciones.get(mejor.tipo, 0) - 1)
    notificacion = f'Demoliste: {mejor.tipo} (recuperaste materiales)'
    tiempo_notificacion = 100

def dibujar_hud():
    # Inventario
    bx,by = 10, ALTO-55
    fondo_inv = pygame.Surface((personaje.max_inventario*34+12,44),pygame.SRCALPHA)
    fondo_inv.fill((0,0,0,160)); pantalla.blit(fondo_inv,(bx-6,by-6))
    for k in range(personaje.max_inventario):
        sx=bx+k*34; pygame.draw.rect(pantalla,(160,160,160),(sx,by,30,30),1)
        if k<len(personaje.inventario):
            c=Sprites.Item.COLORES.get(personaje.inventario[k],(255,255,255))
            pygame.draw.circle(pantalla,c,(sx+15,by+15),8)

    # Recursos actuales + controles
    rec_txt = texto_contraste(
        f'Madera:{personaje.recursos.get("madera",0)}  '
        f'Piedra:{personaje.recursos.get("piedra",0)}  '
        f'[E]=talar/minar/canjear  [B]=construir({personaje.modo_construccion})  [N]=cambiar',
        fuente,(255,255,100))

    # Posición y conteo de ítems
    mx,my=personaje.get_pos_mundo()
    pos_txt = texto_contraste(
        f'Pos:({int(mx)},{int(my)})  Items:{len(personaje.inventario)}/{personaje.max_inventario}',
        fuente,(255,255,255))

    # Fondo oscuro ajustado al ancho del texto más largo (no toda la pantalla)
    ancho_banda = max(rec_txt.get_width(), pos_txt.get_width()) + 16
    fondo_rec = pygame.Surface((ancho_banda,46),pygame.SRCALPHA)
    fondo_rec.fill((0,0,0,215)); pantalla.blit(fondo_rec,(4,ALTO-104))

    pantalla.blit(pos_txt,(10,ALTO-102))
    pantalla.blit(rec_txt,(10,ALTO-82))

    # Controles básicos (esquina superior izquierda) con fondo casi opaco
    controles = [
        'Flechas: mover',
        'Shift: correr',
        'Espacio: recoger item',
        'E: talar arbol / minar roca / canjear',
        'B: construir  |  N: cambiar (casa/puente)',
        'X: demoler construccion cercana',
        'Esc: salir',
    ]
    fondo_ctrl = pygame.Surface((330, len(controles)*20+12),pygame.SRCALPHA)
    fondo_ctrl.fill((0,0,0,215))
    pygame.draw.rect(fondo_ctrl,(255,255,255),(0,0,330,fondo_ctrl.get_height()),1)
    pantalla.blit(fondo_ctrl,(6,6))
    for k,txt in enumerate(controles):
        pantalla.blit(texto_contraste(txt,fuente,(255,255,255)),(12,12+k*20))

    # Fase del día (esquina superior derecha) con fondo
    fase_surf=texto_contraste(f'{nombre_fase(tiempo_dia)} — {fase_actual.upper()}',fuente,(255,235,80))
    fondo_fase=pygame.Surface((fase_surf.get_width()+12,fase_surf.get_height()+6),pygame.SRCALPHA)
    fondo_fase.fill((0,0,0,215))
    pantalla.blit(fondo_fase,(ANCHO-fase_surf.get_width()-20,7))
    pantalla.blit(fase_surf,(ANCHO-fase_surf.get_width()-14,10))

    # Panel TOTAL RECAUDADO (esquina derecha, debajo de la fase)
    rt = personaje.recaudado_total
    lineas_tot = [
        'TOTAL RECAUDADO',
        f'Madera: {rt["madera"]}',
        f'Piedra: {rt["piedra"]}',
        f'Items recogidos: {rt["items"]}',
        f'Trades: {rt["trades"]}',
        f'Construcciones: {rt["construcciones"]}',
    ]
    ancho_panel = 200
    fondo_tot = pygame.Surface((ancho_panel, len(lineas_tot)*20+14),pygame.SRCALPHA)
    fondo_tot.fill((0,0,0,220))
    pygame.draw.rect(fondo_tot,(255,220,80),(0,0,ancho_panel,fondo_tot.get_height()),2)
    px = ANCHO-ancho_panel-14; py = 36
    pantalla.blit(fondo_tot,(px,py))
    for k,txt in enumerate(lineas_tot):
        color = (255,220,80) if k==0 else (255,255,255)
        pantalla.blit(texto_contraste(txt,fuente,color),(px+8,py+7+k*20))

    # Objetivo (centro superior) con fondo casi opaco
    color_obj = (110,255,110) if objetivo.completado else (255,240,60)
    check = 'OK' if objetivo.completado else '>'
    obj_surf = texto_contraste(f'{check} OBJETIVO: {objetivo.desc}',fuente,color_obj)
    fondo_obj = pygame.Surface((obj_surf.get_width()+16, 48),pygame.SRCALPHA)
    fondo_obj.fill((0,0,0,215))
    pantalla.blit(fondo_obj,(ANCHO//2-obj_surf.get_width()//2-8,6))
    pantalla.blit(obj_surf,(ANCHO//2-obj_surf.get_width()//2,10))
    trades_surf = texto_contraste(
        f'Trades:{personaje.trades_realizados}/{objetivo.trades_req}',
        fuente,(255,255,255))
    pantalla.blit(trades_surf,(ANCHO//2-trades_surf.get_width()//2,30))

    # Notificación central flotante
    if notificacion:
        n_surf=texto_contraste(notificacion,fuente_n,(255,255,255))
        nx=ANCHO//2-n_surf.get_width()//2; ny=ALTO//2-60
        fd=pygame.Surface((n_surf.get_width()+20,n_surf.get_height()+10),pygame.SRCALPHA)
        fd.fill((20,20,20,210))
        pygame.draw.rect(fd,(255,220,120),(0,0,fd.get_width(),fd.get_height()),1)
        pantalla.blit(fd,(nx-10,ny-5)); pantalla.blit(n_surf,(nx,ny))

    # Estado de Toni (caja ajustada al texto)
    etiq={0:'DEAMBULANDO',1:'SALUDANDO',2:'REGRESANDO'}
    toni_txt = texto_contraste(f'Toni:{etiq.get(habitante.estado,"?")}',fuente,(140,255,140))
    fondo_toni = pygame.Surface((toni_txt.get_width()+12,toni_txt.get_height()+4),pygame.SRCALPHA)
    fondo_toni.fill((0,0,0,215))
    pantalla.blit(fondo_toni,(4,ALTO-126))
    pantalla.blit(toni_txt,(10,ALTO-124))

# Bucle principal 
fase_anterior = fase_actual
spawn_items_de_fase(fase_actual, n=6)   

# Árbol nuevo cada 8 segundos
tiempo_crecimiento    = 0
INTERVALO_CRECIMIENTO = 400

ejecutar = True
while ejecutar:

    # 1. Mover personaje + leer teclado
    ejecutar = personaje.muevete(obstaculos=obstaculos)

    # 2. Tecla E = talar / minar / intercambiar
    if personaje.interactuar_activo:
        intentar_interaccion_entorno()

    # 3. Tecla B = construir casa o puente
    if personaje.construir_activo:
        intentar_construccion()

    # Tecla X = demoler construcción cercana
    if personaje.demoler_activo:
        intentar_demolicion()

    # 4. Tecla ESPACIO = recoger ítem
    recogido = personaje.recoger_item(items, fase_actual)
    if recogido:
        personaje.recaudado_total['items'] += 1   # total histórico
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

    # 9. FIN DE CICLO DE FASE
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
        personaje.recaudado_total['madera'] += 10   # también cuenta al total
        personaje.recaudado_total['piedra'] += 5
        objetivo = objetivo.siguiente()

    # Timer notificación
    if tiempo_notificacion > 0: tiempo_notificacion -= 1
    else: notificacion = ''

    # Dibujar Océano 
    pantalla.fill(get_ocean_color(tiempo_dia))

    # Mapa del pueblo 
    tileset_pueblo.dibujate()
    tileset_pueblo.dibujate_sprites_exteriores(
        pantalla, personaje.camara_x, personaje.camara_y)

    # Overlay animado del lago 
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