import pygame, math, random, heapq, csv, os

# Constantes de fase 
ITEMS_FASE   = {'dia':  ['manzana','naranja','flor','concha','estrella','sol_cristal','flor_dorada'],
                'noche':['manzana','flor','concha','luna_piedra','estrella_fugaz']}
ITEMS_VALOR  = {'sol_cristal','flor_dorada','luna_piedra','estrella_fugaz'}
OFERTAS_DIA  = [{'quiere':'flor','cantidad':2,'da':'sol_cristal'},
                {'quiere':'manzana','cantidad':3,'da':'flor_dorada'},
                {'quiere':'naranja','cantidad':2,'da':'sol_cristal'},
                {'quiere':'estrella','cantidad':1,'da':'flor_dorada'},
                {'quiere':'concha','cantidad':2,'da':'sol_cristal'}]
OFERTAS_NOCHE= [{'quiere':'flor','cantidad':2,'da':'luna_piedra'},
                {'quiere':'manzana','cantidad':2,'da':'luna_piedra'},
                {'quiere':'concha','cantidad':2,'da':'estrella_fugaz'},
                {'quiere':'naranja','cantidad':2,'da':'luna_piedra'},
                {'quiere':'estrella','cantidad':1,'da':'estrella_fugaz'}]

# Sprite base 
class Sprite():
    def __init__(self,x,y,w,h,archivo,pantalla):
        self.rect=pygame.Rect(x,y,w,h); self.pantalla=pantalla
        self.imagen=(pygame.image.load(archivo).convert_alpha()
                     if archivo and os.path.exists(str(archivo))
                     else pygame.Surface((w,h),pygame.SRCALPHA).convert_alpha())
    def dibujate(self): self.pantalla.blit(self.imagen,self.rect)
    def getImagen(self): return self.imagen
    def detectaColisiones(self,other): return self.rect.colliderect(other.rect)

# TileSet base 
class TileSet(Sprite):
    def __init__(self,x,y,w,h,archivo,pantalla,atw,ath,personaje):
        super().__init__(x,y,w,h,archivo,pantalla)
        self.anchura_tile=atw; self.altura_tile=ath
        self.num_frames     =int(self.imagen.get_width()/atw)  if atw else 1
        self.num_animaciones=int(self.imagen.get_height()/ath) if ath else 1
        self.ImagenesFuenteTile=[]; self.personaje=personaje
        self.tile_padre=self.mapa=None; self.evaluado=False
        for j in range(self.num_animaciones):
            row=[]
            for i in range(self.num_frames):
                s=pygame.Surface((atw,ath),pygame.SRCALPHA).convert_alpha()
                s.blit(self.imagen,(0,0),(i*atw,j*ath,atw,ath))
                row.append(pygame.transform.scale(s,(w,h)))
            self.ImagenesFuenteTile.append(row)

class Tile():
    def __init__(self,x,y,w,h,tipo,imagen):
        self.rect=pygame.Rect(x,y,w,h); self.tipo=tipo; self.imagen=imagen
        self.tile_x=x//w if w else 0; self.tile_y=y//h if h else 0
    @property
    def tile_actual(self): return (self.tile_x,self.tile_y)

# SpritesExterior 
class SpritesExterior:
    # Coordenadas de cada árbol en arboles.png (968x432, fondo negro)
    COORDS_ARBOLES = {
        'arbol_1': (0,   76,  250, 376),
        'arbol_2': (262, 63,  514, 382),
        'arbol_3': (547, 125, 758, 390),
        'arbol_4': (788, 68,  953, 368),
    }
    # Coordenadas de rocas grandes en piedras.png (478x188, fondo negro)
    COORDS_ROCAS = {
        'roca_1': (2,   4,  151, 177),
        'roca_2': (191, 4,  339, 167),
        'roca_3': (364, 49, 472, 173),
    }
    # Coordenadas de piedritas en piedritas.png (622x164, fondo negro)
    COORDS_PIEDRITAS = {
        'piedrita_1': (17,  17, 106, 102),
        'piedrita_2': (123,  1, 207, 163),
        'piedrita_3': (209, 12, 285, 155),
        'piedrita_4': (297, 17, 366, 149),
    }

    ARBOLES    = ['arbol_1', 'arbol_2', 'arbol_3', 'arbol_4']
    ROCAS      = ['roca_1',  'roca_2',  'roca_3']
    PIEDRITAS  = ['piedrita_1', 'piedrita_2', 'piedrita_3', 'piedrita_4']

    def __init__(self, archivo='exterior.png', pantalla=None,
                 archivo_arboles='arboles.png',
                 archivo_piedras='piedras.png',
                 archivo_piedritas='piedritas.png',
                 archivo_casa='casa.png',
                 archivo_puente='puente.png'):
        self.pantalla = pantalla
        self.cache    = {}
        self.sprites  = {}   # todos los sprites cargados

        def _cargar_png(ruta, nombre_log):
            """Carga PNG con fondo negro → transparente."""
            if not os.path.exists(ruta):
                print(f'[SpritesExterior] No encontrado: {ruta}')
                return None
            s = pygame.image.load(ruta).convert_alpha()
            s.set_colorkey((0, 0, 0))
            s = s.convert_alpha()
            print(f'[SpritesExterior] {nombre_log} {s.get_size()}')
            return s

        def _recortar(surf, x0, y0, x1, y1):
            w, h = x1-x0, y1-y0
            r = pygame.Surface((w, h), pygame.SRCALPHA)
            r.blit(surf, (0,0), (x0, y0, w, h))
            return r

        # Árboles
        src = _cargar_png(archivo_arboles, f'arboles.png')
        if src:
            for nombre, coords in self.COORDS_ARBOLES.items():
                self.sprites[nombre] = _recortar(src, *coords)

        # Rocas grandes
        src = _cargar_png(archivo_piedras, 'piedras.png')
        if src:
            for nombre, coords in self.COORDS_ROCAS.items():
                self.sprites[nombre] = _recortar(src, *coords)

        # Piedritas pequeñas
        src = _cargar_png(archivo_piedritas, 'piedritas.png')
        if src:
            for nombre, coords in self.COORDS_PIEDRITAS.items():
                self.sprites[nombre] = _recortar(src, *coords)

        # Casa 
        src = _cargar_png(archivo_casa, 'casa.png')
        if src:
            self.sprites['casa'] = src

        # Puente 
        src = _cargar_png(archivo_puente, 'puente.png')
        if src:
            self.sprites['puente'] = src

        print(f'[SpritesExterior] Total sprites: {list(self.sprites.keys())}')

    def get(self, nombre, tam_px):
        """Devuelve sprite escalado manteniendo proporción (alto=tam_px)."""
        clave = (nombre, tam_px)
        if clave in self.cache:
            return self.cache[clave]
        if nombre not in self.sprites:
            return pygame.Surface((tam_px, tam_px), pygame.SRCALPHA)
        src    = self.sprites[nombre]
        sw, sh = src.get_size()
        ratio  = tam_px / max(sh, 1)
        new_w  = max(1, int(sw * ratio))
        out    = pygame.transform.scale(src, (new_w, tam_px))
        self.cache[clave] = out
        return out

    def dibujar(self, nombre, pantalla, sx, sy, tam_px):
        pantalla.blit(self.get(nombre, tam_px), (sx, sy))

# TileSetPueblo 
# Tipos tile:
#   0=hierba  1=camino  2=árbol(obstáculo/talable)
#   3=agua    4=flores  5=roca grande(mucha piedra)
#   6=piedrita pequeña (poca piedra)
class TileSetPueblo(TileSet):
    def __init__(self,x,y,w,h,archivo,pantalla,atw,ath,personaje,
                 archivo_csv=None, gestor_spr=None):
        super().__init__(x,y,w,h,archivo,pantalla,atw,ath,personaje)
        self.Tiles=[]; self.obstaculos=[]; self.mapa_celdas={}
        self.water_positions=[]
        self.gestor_spr=gestor_spr
        self.sprites_mundo = {}   # (tx,ty) → nombre_sprite
        self.imagen_mapa = self._construir_mapa(archivo_csv)

    def dibujate(self):
        self.pantalla.blit(self.imagen_mapa,
                           (-int(self.personaje.camara_x),
                            -int(self.personaje.camara_y)))
    def getImagen(self): return self.imagen_mapa
    def get_obstaculos(self): return self.obstaculos
    def get_mapa_celdas(self): return self.mapa_celdas

    # Sprites grandes encima del mapa
    def dibujate_sprites_exteriores(self, pantalla, camara_x, camara_y):
        if not self.gestor_spr or not self.gestor_spr.sprites:
            return
        tw = self.rect.width
        TAM = tw * 2   # 64px — tamaño base de árbol/roca en pantalla
        sw, sh = pantalla.get_width(), pantalla.get_height()
        for (tx,ty), nombre in self.sprites_mundo.items():
            sx = tx*tw - int(camara_x)
            sy = ty*tw - int(camara_y)
            if sx > sw+TAM or sx < -TAM or sy > sh+TAM or sy < -TAM:
                continue
            pantalla.blit(self.gestor_spr.get(nombre, TAM), (sx, sy))

    # Agua animada 
    def dibujate_agua_dinamica(self, pantalla, camara_x, camara_y, tiempo_dia):
        """Overlay de color animado SOLO sobre tiles tipo 3 (agua real)."""
        c=self._get_agua_color(tiempo_dia)
        tw=self.rect.width; sw,sh=pantalla.get_width(),pantalla.get_height()
        surf=pygame.Surface((tw,tw),pygame.SRCALPHA); surf.fill((*c,115))
        for wx,wy in self.water_positions:
            sx=wx-int(camara_x); sy=wy-int(camara_y)
            if -tw<sx<sw+tw and -tw<sy<sh+tw:
                pantalla.blit(surf,(sx,sy))

    def _get_agua_color(self,t):
        fases=[(0,(12,38,90)),(500,(35,105,180)),(1200,(42,142,220)),
               (4500,(28,85,145)),(5200,(16,52,110)),(5600,(12,38,90))]
        for k in range(len(fases)-1):
            t0,c0=fases[k]; t1,c1=fases[k+1]
            if t0<=t<t1:
                a=(t-t0)/(t1-t0)
                return tuple(int(c0[i]+(c1[i]-c0[i])*a) for i in range(3))
        return fases[0][1]

    # Talar / minar
    def modificar_tile(self, tile_x, tile_y):
        tw = self.rect.width
        for dy in range(-1, 3):
            ny = tile_y + dy
            if 0<=ny<len(self.Tiles) and 0<=tile_x<len(self.Tiles[ny]):
                if self.mapa_celdas.get((tile_x, ny), 0) in (2, 5, 6):
                    self.imagen_mapa.blit(self._tile_hierba(), (tile_x*tw, ny*tw))
                    self.mapa_celdas[(tile_x, ny)] = 0
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                k = (tile_x+dx, tile_y+dy)
                if k in self.sprites_mundo:
                    del self.sprites_mundo[k]
        area = pygame.Rect(tile_x*tw - tw, tile_y*tw - tw, tw*3, tw*4)
        nuevos = [o for o in self.obstaculos if not area.colliderect(o)]
        self.obstaculos.clear()
        self.obstaculos.extend(nuevos)

    def tile_cercano_interactuable(self, personaje):
        mx,my=personaje.get_pos_mundo(); tw=self.rect.width
        btx,bty=int(mx/tw),int(my/tw)
        for dx in range(-2,3):
            for dy in range(-2,3):
                tx,ty=btx+dx,bty+dy
                tipo=self.mapa_celdas.get((tx,ty),0)
                if tipo in (2,5,6): return (tipo,tx,ty)
        return (None,None,None)

    def crecer_arbol_aleatorio(self):
        tw=self.rect.width; nc=5000//tw; nf=5000//tw
        for _ in range(40):
            i=random.randint(5,nc-6); j=random.randint(5,nf-6)
            if self.mapa_celdas.get((i,j),0)!=0: continue
            if j+1>=nf or self.mapa_celdas.get((i,j+1),0)!=0: continue
            if 2100<=i*tw<=2700 and 2100<=j*tw<=2700: continue
            self.Tiles[j][i].tipo=2; self.Tiles[j][i].imagen=self._tile_arbol_copa()
            self.Tiles[j+1][i].tipo=2; self.Tiles[j+1][i].imagen=self._tile_arbol_tronco()
            self.imagen_mapa.blit(self._tile_arbol_copa(), (i*tw,j*tw))
            self.imagen_mapa.blit(self._tile_arbol_tronco(),(i*tw,(j+1)*tw))
            self.mapa_celdas[(i,j)]=2; self.mapa_celdas[(i,j+1)]=2
            nombre=SpritesExterior.ARBOLES[(i*31+j*17)%4]
            self.sprites_mundo[(i,j)]=nombre
            self.obstaculos.append(pygame.Rect(i*tw,j*tw,tw,tw*2))
            return True
        return False

    # Tiles base 
    def _tile_hierba(self):
        s=pygame.Surface((self.rect.width,self.rect.width),pygame.SRCALPHA).convert_alpha()
        if self.num_animaciones>9:
            s.blit(self.ImagenesFuenteTile[random.randint(8,9)]
                   [random.randint(0,min(9,self.num_frames-1))],(0,0))
        else: s.fill((80,158,62))
        return s

    def _tile_camino(self):
        s=pygame.Surface((self.rect.width,self.rect.width),pygame.SRCALPHA).convert_alpha()
        if self.num_animaciones>13:
            s.blit(self.ImagenesFuenteTile[random.randint(13,min(16,self.num_animaciones-1))]
                   [random.randint(0,min(2,self.num_frames-1))],(0,0))
        else: s.fill((158,128,90))
        return s

    def _tile_flores(self):
        s=self._tile_hierba()
        for _ in range(random.randint(2,4)):
            pygame.draw.circle(s,random.choice([(255,80,140),(255,220,30),(200,90,255)]),
                               (random.randint(4,self.rect.width-4),
                                random.randint(4,self.rect.width-4)),3)
        return s

    def _tile_agua(self):
        tw=self.rect.width
        s=pygame.Surface((tw,tw),pygame.SRCALPHA).convert_alpha()
        s.fill((42,142,220))
        for i in range(0,tw,8):
            pygame.draw.line(s,(80,170,245),(i,tw//3),(i+4,tw//3),1)
        return s

    def _tile_arbol_copa(self):
        return self._tile_hierba()

    def _tile_arbol_tronco(self):
        return self._tile_hierba()

    def _tile_monte(self):
        return self._tile_hierba()

    def _leer_csv(self,f):
        if not os.path.exists(f): return []
        mapa=[]
        with open(f,newline='',encoding='utf-8') as fp:
            for fila in csv.reader(fp):
                vals=[int(v) for v in fila if v.strip()!='']
                if vals: mapa.append(vals)
        return mapa

    def _construir_mapa(self, archivo_csv=None):
        tw=self.rect.width; ANCHO=ALTO=5000
        nc=ANCHO//tw+1; nf=ALTO//tw+1
        sup=pygame.Surface((ANCHO,ALTO),pygame.SRCALPHA).convert_alpha()
        mapa_csv=self._leer_csv(archivo_csv) if archivo_csv else []
        for j in range(nf):
            fila=[]
            for i in range(nc):
                tipo=(mapa_csv[j][i] if mapa_csv and j<len(mapa_csv) and i<len(mapa_csv[j]) else 0)
                self.mapa_celdas[(i,j)]=tipo
                img=self._tile_hierba() if tipo==0 else self._tile_camino()
                fila.append(Tile(i*tw,j*tw,tw,tw,tipo,img))
            self.Tiles.append(fila)
        if not mapa_csv:
            self._generar_caminos(nc,nf,tw)
            self._generar_bosques(nc,nf,tw)
            self._generar_lago(nc,nf,tw)
            self._generar_flores(nc,nf)
            self._generar_montes(nc,nf,tw)
        for fila in self.Tiles:
            for tile in fila: sup.blit(tile.imagen,tile.rect)
        return sup

    def _generar_caminos(self,nc,nf,tw):
        # Camino horizontal y vertical — libres para caminar
        for i in range(nc):
            for dy in range(-1,2):
                j=nf//2+dy
                if 0<=j<nf:
                    self.Tiles[j][i].tipo=1; self.Tiles[j][i].imagen=self._tile_camino()
                    self.mapa_celdas[(i,j)]=1
        for j in range(nf):
            for dx in range(-1,2):
                i=nc//2+dx
                if 0<=i<nc:
                    self.Tiles[j][i].tipo=1; self.Tiles[j][i].imagen=self._tile_camino()
                    self.mapa_celdas[(i,j)]=1

    def _generar_bosques(self,nc,nf,tw):
        stx,sty=2400//tw,2400//tw; safe=12
        centros=[(nc//5,nf//5),(nc*4//5,nf//5),(nc//5,nf*4//5),
                 (nc*4//5,nf*4//5),(nc//3,nf//2+20),(nc*2//3,nf//3)]
        for bcx,bcy in centros:
            if abs(bcx-stx)<safe and abs(bcy-sty)<safe: continue
            r=random.randint(4,7)
            for dj in range(-r,r+1):
                for di in range(-r,r+1):
                    if di*di+dj*dj>r*r: continue
                    i,j=bcx+di,bcy+dj
                    if not(1<=i<nc-2 and 1<=j<nf-3): continue
                    if self.mapa_celdas.get((i,j),0) in(1,2): continue
                    self.Tiles[j][i].tipo=2; self.Tiles[j][i].imagen=self._tile_arbol_copa()
                    self.mapa_celdas[(i,j)]=2
                    if j+1<nf:
                        self.Tiles[j+1][i].tipo=2; self.Tiles[j+1][i].imagen=self._tile_arbol_tronco()
                        self.mapa_celdas[(i,j+1)]=2
                    # 1 sprite por árbol, en la celda de copa
                    nombre=SpritesExterior.ARBOLES[(i*31+j*17)%4]
                    self.sprites_mundo[(i,j)]=nombre
                    self.obstaculos.append(pygame.Rect(i*tw,j*tw,tw,tw*2))

    def _generar_lago(self,nc,nf,tw):
        pass  # Sin lago

    def abrir_paso_rio(self, mundo_x, mundo_y, ancho_px=128):
        """Elimina obstáculos de agua en la zona donde se colocó el puente."""
        tw = self.rect.width
        zona = pygame.Rect(int(mundo_x)-ancho_px//2, int(mundo_y)-ancho_px//2,
                           ancho_px, ancho_px)
        nuevos = []
        for o in self.obstaculos:
            tx,ty = o.x//tw, o.y//tw
            if self.mapa_celdas.get((tx,ty),0)==3 and zona.colliderect(o):
                continue   # tile de agua bajo el puente
            nuevos.append(o)
        self.obstaculos.clear()
        self.obstaculos.extend(nuevos)

    def _generar_flores(self,nc,nf):
        for _ in range(100):
            i,j=random.randint(2,nc-3),random.randint(2,nf-3)
            if self.mapa_celdas.get((i,j),0)==0:
                self.Tiles[j][i].tipo=4; self.Tiles[j][i].imagen=self._tile_flores()
                self.mapa_celdas[(i,j)]=4

    def _generar_montes(self,nc,nf,tw):
        # Tipo 5: rocas grandes — más difíciles
        for _ in range(25):
            i,j=random.randint(3,nc-4),random.randint(3,nf-4)
            if self.mapa_celdas.get((i,j),0)==0:
                self.Tiles[j][i].tipo=5; self.Tiles[j][i].imagen=self._tile_monte()
                self.mapa_celdas[(i,j)]=5
                nombre=SpritesExterior.ROCAS[(i*13+j*7)%len(SpritesExterior.ROCAS)]
                self.sprites_mundo[(i,j)]=nombre
        # Tipo 6: piedritas pequeñas — fáciles de minar
        for _ in range(35):
            i,j=random.randint(3,nc-4),random.randint(3,nf-4)
            if self.mapa_celdas.get((i,j),0)==0:
                self.Tiles[j][i].tipo=6; self.Tiles[j][i].imagen=self._tile_monte()
                self.mapa_celdas[(i,j)]=6
                nombre=SpritesExterior.PIEDRITAS[(i*17+j*11)%len(SpritesExterior.PIEDRITAS)]
                self.sprites_mundo[(i,j)]=nombre


# SpriteAnimado 
class SpriteAnimado(TileSet):
    def __init__(self,x,y,w,h,a,p,atw,ath,personaje):
        super().__init__(x,y,w,h,a,p,atw,ath,personaje)
        self.animacion=1;self.frame=0;self.cont_frames=0;self.max_cont_frames=25;self.estado=0
    def setMaxContFrames(self,vel):
        v=max(1,abs(vel));self.max_cont_frames=max(1,min(25,int(40/v)))


# Item 
class Item():
    COLORES={'manzana':(210,45,45),'naranja':(255,145,0),'flor':(255,80,175),
             'concha':(240,215,165),'estrella':(255,225,30),'sol_cristal':(255,200,0),
             'flor_dorada':(255,180,0),'luna_piedra':(200,210,255),'estrella_fugaz':(180,230,255)}
    def __init__(self,x,y,tipo='manzana',fase='ambas'):
        self.rect=pygame.Rect(x,y,26,26);self.tipo=tipo;self.fase=fase
        self.recogido=False;self._brillo=0;self._dir=1
    def actualizar(self):
        self._brillo+=self._dir*2
        if self._brillo>=50 or self._brillo<=0:self._dir*=-1
    def dibujate(self,pantalla,cx,cy,fase_actual='dia'):
        if self.recogido:return
        sx,sy=self.rect.x-int(cx),self.rect.y-int(cy)
        c=self.COLORES.get(self.tipo,(255,255,255))
        en_fase=(self.fase=='ambas' or self.fase==fase_actual)
        surf=pygame.Surface((26,26),pygame.SRCALPHA)
        self._draw(surf,13,13,c); surf.set_alpha(255 if en_fase else 80)
        pantalla.blit(surf,(sx,sy))
        if en_fase and self._brillo>12:
            g=pygame.Surface((26,26),pygame.SRCALPHA)
            pygame.draw.circle(g,(255,255,255,self._brillo),(13,13),12); pantalla.blit(g,(sx,sy))
    def _draw(self,s,cx,cy,c):
        t=self.tipo
        if t in('manzana','naranja'):
            pygame.draw.circle(s,c,(cx,cy),9)
            pygame.draw.circle(s,tuple(min(255,v+60)for v in c),(cx-3,cy-3),3)
            pygame.draw.line(s,(50,110,30),(cx,cy-4),(cx,cy-10),2)
        elif t=='flor':
            for a in range(0,360,72):
                r=math.radians(a);pygame.draw.circle(s,c,(cx+int(math.cos(r)*7),cy+int(math.sin(r)*7)),4)
            pygame.draw.circle(s,(255,240,100),(cx,cy),4)
        elif t=='concha':
            pygame.draw.ellipse(s,c,(cx-9,cy-5,18,11))
            for k in range(3):pygame.draw.arc(s,(200,180,130),(cx-9+k*3,cy-5,18-k*3,11),0,math.pi,1)
        elif t=='estrella':
            pts=[(cx+int(math.cos(math.radians(k*36-90))*(9 if k%2==0 else 4)),
                  cy+int(math.sin(math.radians(k*36-90))*(9 if k%2==0 else 4)))for k in range(10)]
            pygame.draw.polygon(s,c,pts)
        elif t=='sol_cristal':
            pygame.draw.polygon(s,c,[(cx,cy-10),(cx+8,cy),(cx,cy+10),(cx-8,cy)])
            pygame.draw.polygon(s,(255,240,150),[(cx,cy-6),(cx+4,cy),(cx,cy+6),(cx-4,cy)])
            for a in range(0,360,45):
                r=math.radians(a);pygame.draw.line(s,(255,255,200),(cx,cy),(cx+int(math.cos(r)*11),cy+int(math.sin(r)*11)),1)
        elif t=='flor_dorada':
            for a in range(0,360,72):
                r=math.radians(a);pygame.draw.circle(s,c,(cx+int(math.cos(r)*8),cy+int(math.sin(r)*8)),5)
            pygame.draw.circle(s,(255,240,80),(cx,cy),4)
        elif t=='luna_piedra':
            pygame.draw.ellipse(s,(170,175,195),(cx-9,cy-3,18,12))
            pygame.draw.circle(s,(210,220,255),(cx,cy-5),7)
            pygame.draw.circle(s,(90,90,130),(cx+4,cy-8),5)
        elif t=='estrella_fugaz':
            pts=[(cx+int(math.cos(math.radians(k*36-90))*(9 if k%2==0 else 4)),
                  cy+int(math.sin(math.radians(k*36-90))*(9 if k%2==0 else 4)))for k in range(10)]
            pygame.draw.polygon(s,c,pts)
            for idx,dx in enumerate([8,14,20]):
                a=140-idx*45
                if a>0:pygame.draw.line(s,(*c,a),(cx-dx,cy+2),(cx-dx-4,cy+2),2)


# __astar 
def _astar(inicio,destino,obstaculos,aw,ah,tam_celda=32,mapa_ancho=5000,mapa_alto=5000,mapa_celdas=None):
    def mc(wx,wy):return(int(wx)//tam_celda,int(wy)//tam_celda)
    def cm(cx,cy):return(cx*tam_celda,cy*tam_celda)
    def cost(c):return 2.0 if mapa_celdas and mapa_celdas.get(c,0)==1 else 1.0
    ex=max(0,(aw-1)//tam_celda);ey=max(0,(ah-1)//tam_celda)
    bloq=set()
    for o in obstaculos:
        for cy in range(o.top//tam_celda-ey,(o.bottom-1)//tam_celda+1):
            for cx in range(o.left//tam_celda-ex,(o.right-1)//tam_celda+1):bloq.add((cx,cy))
    mx,my=mapa_ancho//tam_celda,mapa_alto//tam_celda
    ic,dc=mc(*inicio),mc(*destino)
    if dc in bloq:
        best,bd=None,1e9
        for dy in range(-3,4):
            for dx in range(-3,4):
                nc=(dc[0]+dx,dc[1]+dy)
                if nc not in bloq and abs(dx)+abs(dy)<bd:bd,best=abs(dx)+abs(dy),nc
        if best:dc=best
        else:return[]
    if ic==dc:return[cm(*dc)]
    dirs=[(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    costs=[1,1,1,1,1.414,1.414,1.414,1.414]
    heap=[(0.0,ic)];g={ic:0.0};came={};vis=0
    while heap and vis<2000:
        _,cur=heapq.heappop(heap);vis+=1
        if cur==dc:
            path=[];n=cur
            while n in came:path.append(cm(*n));n=came[n]
            path.reverse();return path
        for k,(dx,dy) in enumerate(dirs):
            nb=(cur[0]+dx,cur[1]+dy)
            if nb in bloq or not(0<=nb[0]<mx and 0<=nb[1]<my):continue
            if dx and dy and((cur[0]+dx,cur[1])in bloq or(cur[0],cur[1]+dy)in bloq):continue
            ng=g[cur]+costs[k]*cost(nb)
            if ng<g.get(nb,1e9):
                g[nb]=ng;hdx,hdy=abs(nb[0]-dc[0]),abs(nb[1]-dc[1])
                heapq.heappush(heap,(ng+max(hdx,hdy)+0.414*min(hdx,hdy),nb));came[nb]=cur
    return[]


# Aldeano 
class Aldeano():
    DEAMBULAR=0;SALUDAR=1;REGRESAR=2
    PALETA=[((255,200,95),(180,120,55)),((95,195,255),(55,130,185)),
            ((200,110,255),(130,65,205)),((95,220,125),(55,160,80)),((255,125,95),(200,75,55))]
    def __init__(self,x,y,w,h,vel,zona_cx,zona_cy,zona_radio,pantalla,personaje,nombre='Aldeano',indice_color=0):
        self.rect=pygame.Rect(x,y,w,h);self.pantalla=pantalla;self.personaje=personaje
        self.nombre=nombre;self.vel=vel
        self.zona_cx=float(zona_cx);self.zona_cy=float(zona_cy);self.zona_radio=zona_radio
        self.pos_x_mundo=float(x);self.pos_y_mundo=float(y)
        self.pos_base_x=float(x);self.pos_base_y=float(y)
        self.vel_x=0.0;self.vel_y=0.0;self.estado=self.DEAMBULAR
        self.destino_x=float(x);self.destino_y=float(y)
        self.tiempo_espera=random.randint(30,120);self.frame=0;self.cont_frames=0
        self.dialogo='';self.tiempo_dialogo=0
        self.indice_trade=indice_color%len(OFERTAS_DIA)
        self.trade_offer=OFERTAS_DIA[self.indice_trade]
        idx=indice_color%len(self.PALETA)
        self.color_cuerpo=self.PALETA[idx][0];self.color_sombra=self.PALETA[idx][1]
        self._frames=self._gen_frames(w,h);self._fuente=None
    def actualizar_fase(self,fase):
        of=OFERTAS_DIA if fase=='dia' else OFERTAS_NOCHE
        self.trade_offer=of[self.indice_trade%len(of)]
    def puede_intercambiar(self,p):
        t=self.trade_offer;return p.inventario.count(t['quiere'])>=t['cantidad']
    def ejecutar_intercambio(self,p):
        t=self.trade_offer
        for _ in range(t['cantidad']):p.inventario.remove(t['quiere'])
        if len(p.inventario)<p.max_inventario:p.inventario.append(t['da'])
        p.trades_realizados+=1;self.dialogo=f"Aqui: {t['da']}!";self.tiempo_dialogo=0
    def _gen_frames(self,w,h):
        frames=[]
        for f in range(4):
            s=pygame.Surface((w,h),pygame.SRCALPHA).convert_alpha();cx,cy=w//2,h//2
            pygame.draw.ellipse(s,(0,0,0),(cx-12,h-10,24,7))
            off=[0,5,0,-5][f]
            pygame.draw.rect(s,self.color_sombra,(cx-9,cy+5,6,11+off))
            pygame.draw.rect(s,self.color_sombra,(cx+3,cy+5,6,11-off))
            pygame.draw.ellipse(s,self.color_cuerpo,(cx-13,cy-6,26,18))
            pygame.draw.circle(s,self.color_cuerpo,(cx,cy-11),12)
            pygame.draw.polygon(s,self.color_sombra,[(cx-10,cy-19),(cx-4,cy-30),(cx,cy-19)])
            pygame.draw.polygon(s,self.color_sombra,[(cx,cy-19),(cx+4,cy-30),(cx+10,cy-19)])
            oy=cy-13
            pygame.draw.circle(s,(30,30,30),(cx-4,oy),3);pygame.draw.circle(s,(30,30,30),(cx+4,oy),3)
            pygame.draw.circle(s,(255,255,255),(cx-3,oy-1),1);pygame.draw.circle(s,(255,255,255),(cx+5,oy-1),1)
            pygame.draw.ellipse(s,self.color_sombra,(cx-2,cy-8,4,3))
            frames.append(s)
        return frames
    def getImagen(self):
        self.cont_frames+=1;vm=math.hypot(self.vel_x,self.vel_y)
        if vm>0.1 and self.cont_frames>max(3,int(18/vm)):self.cont_frames=0;self.frame=(self.frame+1)%4
        elif vm<=0.1:self.frame=0
        img=self._frames[self.frame]
        return pygame.transform.flip(img,True,False) if self.vel_x<0 else img
    def dibujate(self,personaje=None):
        ref=personaje or self.personaje
        sx=int(self.pos_x_mundo-ref.camara_x);sy=int(self.pos_y_mundo-ref.camara_y)
        self.pantalla.blit(self.getImagen(),pygame.Rect(sx,sy,self.rect.width,self.rect.height))
        if not self._fuente:self._fuente=pygame.font.SysFont(None,16)
        nom=self._fuente.render(self.nombre,True,(255,255,255))
        self.pantalla.blit(nom,(sx+self.rect.width//2-nom.get_width()//2,sy-16))
        if self.estado==self.SALUDAR and self.dialogo:
            f2=pygame.font.SysFont(None,19)
            t=self.trade_offer
            linea1=f"Ofrece: {t['cantidad']} {t['quiere']}"
            linea2=f"A cambio: {t['da']}"
            linea3=f"Presiona E para canjear"
            txts=[f2.render(l,True,c) for l,c in
                  [(linea1,(20,20,140)),(linea2,(20,120,20)),(linea3,(100,60,0))]]
            bw=max(t.get_width() for t in txts)+16
            bh=sum(t.get_height() for t in txts)+14
            bx=sx+self.rect.width//2-bw//2; by=sy-bh-8
            fd=pygame.Surface((bw,bh),pygame.SRCALPHA)
            fd.fill((255,252,215,235))
            pygame.draw.rect(fd,(160,140,60),(0,0,bw,bh),2)
            self.pantalla.blit(fd,(bx,by))
            cy=by+4
            for txt in txts:
                self.pantalla.blit(txt,(bx+8,cy)); cy+=txt.get_height()+2
    def muevete(self,personaje,obstaculos=None):
        match self.estado:
            case 0:self._deambular(personaje)
            case 1:self._saludar(personaje)
            case 2:self._regresar(personaje)
        bl=(obstaculos.get_obstaculos() if hasattr(obstaculos,'get_obstaculos')
            else obstaculos if isinstance(obstaculos,list) else[])
        self.pos_x_mundo+=self.vel_x
        mi=pygame.Rect(int(self.pos_x_mundo),int(self.pos_y_mundo),self.rect.width,self.rect.height)
        for o in bl:
            if mi.colliderect(o):
                self.pos_x_mundo=float(o.left-self.rect.width) if self.vel_x>0 else float(o.right)
                mi.x=int(self.pos_x_mundo);self.vel_x=0
        self.pos_y_mundo+=self.vel_y
        mi=pygame.Rect(int(self.pos_x_mundo),int(self.pos_y_mundo),self.rect.width,self.rect.height)
        for o in bl:
            if mi.colliderect(o):
                self.pos_y_mundo=float(o.top-self.rect.height) if self.vel_y>0 else float(o.bottom)
                mi.y=int(self.pos_y_mundo);self.vel_y=0
        self.pos_x_mundo=max(0.0,min(self.pos_x_mundo,4960.0))
        self.pos_y_mundo=max(0.0,min(self.pos_y_mundo,4960.0))
    def _deambular(self,p):
        if self.tiempo_espera>0:
            self.vel_x=self.vel_y=0;self.tiempo_espera-=1
            if self._ver(p):self.estado=self.SALUDAR;self._oferta()
            return
        dx=self.destino_x-self.pos_x_mundo;dy=self.destino_y-self.pos_y_mundo;dist=math.hypot(dx,dy)
        if dist<abs(self.vel)*2 or dist==0:
            self.vel_x=self.vel_y=0;self.tiempo_espera=random.randint(60,200)
            a=random.uniform(0,2*math.pi);r=random.uniform(0,self.zona_radio)
            self.destino_x=max(50,min(4900,self.zona_cx+math.cos(a)*r))
            self.destino_y=max(50,min(4900,self.zona_cy+math.sin(a)*r))
        else:self.vel_x=(dx/dist)*abs(self.vel);self.vel_y=(dy/dist)*abs(self.vel)
        if self._ver(p):self.estado=self.SALUDAR;self._oferta()
    def _saludar(self,p):
        px,py=p.get_pos_mundo();dx=px-self.pos_x_mundo;dy=py-self.pos_y_mundo;dist=math.hypot(dx,dy)
        if dist>85:spd=abs(self.vel)*0.6;self.vel_x=(dx/dist)*spd;self.vel_y=(dy/dist)*spd
        else:
            self.vel_x=self.vel_y=0;self.tiempo_dialogo+=1
            if self.tiempo_dialogo>180:self.tiempo_dialogo=0;self.dialogo='';self.estado=self.REGRESAR
        if not self._ver(p,380):self.dialogo='';self.estado=self.REGRESAR
    def _regresar(self,p=None):
        dx=self.pos_base_x-self.pos_x_mundo;dy=self.pos_base_y-self.pos_y_mundo;dist=math.hypot(dx,dy)
        if dist<abs(self.vel)*2:
            self.pos_x_mundo=self.pos_base_x;self.pos_y_mundo=self.pos_base_y
            self.vel_x=self.vel_y=0;self.estado=self.DEAMBULAR;self.tiempo_espera=60
        else:self.vel_x=(dx/dist)*abs(self.vel);self.vel_y=(dy/dist)*abs(self.vel)
        if p and self._ver(p):self.estado=self.SALUDAR;self._oferta()
    def _oferta(self):
        t=self.trade_offer
        self.dialogo=f"Da: {t['cantidad']} {t['quiere']} | Recibe: {t['da']} | Presiona E"
        self.tiempo_dialogo=0
    def _ver(self,p,radio=220):
        px,py=p.get_pos_mundo();return math.hypot(px-self.pos_x_mundo,py-self.pos_y_mundo)<radio


# Habitante (Aldeano con A*)
class Habitante(Aldeano):
    def __init__(self,x,y,w,h,vel,zona_cx,zona_cy,zona_radio,pantalla,personaje,
                 nombre='Habitante',indice_color=0,mapa_celdas=None):
        super().__init__(x,y,w,h,vel,zona_cx,zona_cy,zona_radio,pantalla,personaje,nombre,indice_color)
        self.mapa_celdas=mapa_celdas or{};self._camino=[];self._idx=0;self._recalc=0;self._irec=20;self._obs=[]
    def muevete(self,p,obstaculos=None):
        self._obs=(obstaculos.get_obstaculos() if hasattr(obstaculos,'get_obstaculos')
                   else obstaculos if isinstance(obstaculos,list) else[])
        super().muevete(p,obstaculos)
    def _saludar(self,p):
        px,py=p.get_pos_mundo();dist=math.hypot(px-self.pos_x_mundo,py-self.pos_y_mundo)
        if dist<=85:
            self.vel_x=self.vel_y=0;self.tiempo_dialogo+=1
            if self.tiempo_dialogo>220:self.tiempo_dialogo=0;self.dialogo='';self.estado=self.REGRESAR;self._camino=[]
            return
        self._recalc+=1
        if self._recalc>=self._irec or not self._camino:
            self._recalc=0
            self._camino=_astar((self.pos_x_mundo,self.pos_y_mundo),(px,py),self._obs,
                                 self.rect.width,self.rect.height,mapa_celdas=self.mapa_celdas);self._idx=0
        self._seguir()
        if not self._ver(p,450):self.dialogo='';self.estado=self.REGRESAR;self._camino=[]
    def _regresar(self,p=None):
        dx=self.pos_base_x-self.pos_x_mundo;dy=self.pos_base_y-self.pos_y_mundo;dist=math.hypot(dx,dy)
        if dist<=abs(self.vel)*2:
            self.pos_x_mundo=self.pos_base_x;self.pos_y_mundo=self.pos_base_y
            self.vel_x=self.vel_y=0;self.estado=self.DEAMBULAR;self._camino=[];return
        self._recalc+=1
        if self._recalc>=self._irec or not self._camino:
            self._recalc=0
            self._camino=_astar((self.pos_x_mundo,self.pos_y_mundo),(self.pos_base_x,self.pos_base_y),
                                 self._obs,self.rect.width,self.rect.height,mapa_celdas=self.mapa_celdas);self._idx=0
        self._seguir()
        if p and self._ver(p,260):self.estado=self.SALUDAR;self._oferta();self._camino=[]
    def _seguir(self):
        if not(self._camino and self._idx<len(self._camino)):self.vel_x=self.vel_y=0;return
        ox,oy=self._camino[self._idx];dx,dy=ox-self.pos_x_mundo,oy-self.pos_y_mundo;d=math.hypot(dx,dy)
        if d<abs(self.vel)*2:
            self._idx+=1
            if self._idx<len(self._camino):ox,oy=self._camino[self._idx];dx,dy=ox-self.pos_x_mundo,oy-self.pos_y_mundo;d=math.hypot(dx,dy)
        if d>0.5:self.vel_x=(dx/d)*abs(self.vel);self.vel_y=(dy/d)*abs(self.vel)
        else:self.vel_x=self.vel_y=0


# Construccion 
class Construccion():
    RECETAS={'casa':{'madera':5,'piedra':3},'puente':{'madera':4,'piedra':0}}
    def __init__(self,x,y,tipo,pantalla,gestor_spr=None):
        self.rect=pygame.Rect(x,y,128,128);self.tipo=tipo
        self.pantalla=pantalla;self.gestor_spr=gestor_spr
    def dibujate(self,camara_x,camara_y):
        sx=int(self.rect.x-camara_x);sy=int(self.rect.y-camara_y)
        if self.gestor_spr and self.gestor_spr.sprites:
            if self.tipo=='casa' and 'casa' in self.gestor_spr.sprites:
                self.pantalla.blit(self.gestor_spr.get('casa',128),(sx,sy))
                return
            if self.tipo=='puente' and 'puente' in self.gestor_spr.sprites:
                self.pantalla.blit(self.gestor_spr.get('puente',96),(sx,sy))
                return
        # fallback procedural
        if self.tipo=='casa':self._dibujar_casa(sx,sy)
        else:self._dibujar_puente(sx,sy)
    def _dibujar_casa(self,sx,sy):
        pygame.draw.rect(self.pantalla,(195,140,80),(sx+2,sy+28,60,34))
        pygame.draw.polygon(self.pantalla,(178,52,42),[(sx+2,sy+28),(sx+32,sy+5),(sx+62,sy+28)])
        pygame.draw.rect(self.pantalla,(110,70,35),(sx+24,sy+46,16,16))
        pygame.draw.rect(self.pantalla,(175,228,255),(sx+6,sy+34,14,12))
    def _dibujar_puente(self,sx,sy):
        for ry in[sy+28,sy+38]:pygame.draw.rect(self.pantalla,(158,108,48),(sx,ry,64,7))
        for px in[sx+6,sx+28,sx+52]:pygame.draw.rect(self.pantalla,(118,78,28),(px,sy+18,8,26))



# Objetivo diario
class Objetivo():
    _DATOS={'dia':[
        {'desc':'Obtén 1 sol_cristal y construye 1 casa','items':{'sol_cristal':1},'const':{'casa':1},'trades':0},
        {'desc':'Comercia con 2 aldeanos de día','items':{},'const':{},'trades':2},
        {'desc':'Obtén 1 flor_dorada y 1 sol_cristal','items':{'flor_dorada':1,'sol_cristal':1},'const':{},'trades':0}],
    'noche':[
        {'desc':'Obtén 1 luna_piedra y 1 estrella_fugaz','items':{'luna_piedra':1,'estrella_fugaz':1},'const':{},'trades':0},
        {'desc':'Construye un puente y comercia con 1 aldeano','items':{},'const':{'puente':1},'trades':1},
        {'desc':'Obtén 2 luna_piedra','items':{'luna_piedra':2},'const':{},'trades':0}]}
    def __init__(self,fase='dia',indice=0):
        self.fase=fase;self.indice=indice%len(self._DATOS[fase])
        d=self._DATOS[fase][self.indice]
        self.desc=d['desc'];self.items_req=d['items'].copy();self.const_req=d['const'].copy()
        self.trades_req=d['trades'];self.completado=False
    def verificar(self,p):
        if self.completado:return True
        for t,n in self.items_req.items():
            if p.inventario.count(t)<n:return False
        for t,n in self.const_req.items():
            if p.construcciones.get(t,0)<n:return False
        if p.trades_realizados<self.trades_req:return False
        self.completado=True;return True
    def siguiente(self,fase=None):return Objetivo(fase or self.fase,self.indice+1)


# Personaje 
class Personaje(Sprite):
    def __init__(self,x,y,w,h,archivo,pantalla):
        super().__init__(x,y,w,h,archivo,pantalla)
        self.vel=5;self.vel_x=0;self.vel_y=0;self.cuadro=0;self.aux_cuadro=0
        self.corriendo=False;self.estado=0
        self._cx=pantalla.get_width()//2-w//2;self._cy=pantalla.get_height()//2-h//2
        self.camara_x=float(x)-self._cx;self.camara_y=float(y)-self._cy
        self.pos_x_absoluta=self.camara_x;self.pos_y_absoluta=self.camara_y
        self.inventario=[];self.max_inventario=12
        self.recoger_activo=False;self.interactuar_activo=False;self.construir_activo=False
        self.modo_construccion='casa'
        self.recursos={'madera':0,'piedra':0};self.construcciones={'casa':0,'puente':0}
        self.trades_realizados=0
    def get_pos_mundo(self):return(self.camara_x+self._cx,self.camara_y+self._cy)
    def dibujate(self):
        pygame.draw.rect(self.pantalla,(255,255,0),(self._cx,self._cy,self.rect.width,self.rect.height),1)
        self.pantalla.blit(self.getImagen(),(self._cx,self._cy))
    def getImagen(self):
        img=pygame.Surface((32,32),pygame.SRCALPHA).convert_alpha()
        match self.estado:
            case 0:an,mq,ma=0,12,10
            case 1:an,mq,ma=1,7,10
            case 2:an,mq,ma=1,7,5
            case _:an,mq,ma=0,12,10
        img.blit(self.imagen,(0,0),(self.cuadro*32,an*32,32,32))
        img=pygame.transform.scale(img,(self.rect.width,self.rect.height))
        if self.vel_x<0:img=pygame.transform.flip(img,True,False)
        self.aux_cuadro+=1
        if self.aux_cuadro>ma:self.aux_cuadro=0;self.cuadro+=1
        if self.cuadro>mq:self.cuadro=0
        return img
    def recoger_item(self,items,fase_actual='dia'):
        if not self.recoger_activo:return None
        self.recoger_activo=False
        mx,my=self.get_pos_mundo()
        zona=pygame.Rect(int(mx)-24,int(my)-24,self.rect.width+48,self.rect.height+48)
        for item in items:
            if not item.recogido and zona.colliderect(item.rect):
                if item.tipo in ITEMS_VALOR and item.fase!='ambas' and item.fase!=fase_actual:continue
                if len(self.inventario)<self.max_inventario:
                    item.recogido=True;self.inventario.append(item.tipo);return item.tipo
        return None
    def muevete(self,obstaculos=None):
        self.recoger_activo=self.interactuar_activo=self.construir_activo=False
        for ev in pygame.event.get():
            if ev.type==pygame.KEYUP:
                if ev.key==pygame.K_LEFT:self.vel_x=0
                if ev.key==pygame.K_RIGHT:self.vel_x=0
                if ev.key==pygame.K_UP:self.vel_y=0
                if ev.key==pygame.K_DOWN:self.vel_y=0
                if ev.key==pygame.K_LSHIFT:self.vel_x/=2;self.corriendo=False
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_LEFT:self.vel_x=-self.vel
                if ev.key==pygame.K_RIGHT:self.vel_x=self.vel
                if ev.key==pygame.K_UP:self.vel_y=-self.vel
                if ev.key==pygame.K_DOWN:self.vel_y=self.vel
                if ev.key==pygame.K_ESCAPE:return False
                if ev.key==pygame.K_LSHIFT:self.vel_x*=2;self.corriendo=True
                if ev.key==pygame.K_SPACE:self.recoger_activo=True
                if ev.key==pygame.K_e:self.interactuar_activo=True
                if ev.key==pygame.K_b:self.construir_activo=True
                if ev.key==pygame.K_n:
                    t=list(Construccion.RECETAS.keys())
                    self.modo_construccion=t[(t.index(self.modo_construccion)+1)%len(t)]
            if ev.type==pygame.QUIT:return False
        self.actualizarEstado()
        bl=(obstaculos.get_obstaculos() if hasattr(obstaculos,'get_obstaculos')
            else obstaculos if isinstance(obstaculos,list) else[])
        wx,wy=self.get_pos_mundo()
        wx+=self.vel_x
        jr=pygame.Rect(int(wx),int(wy),self.rect.width,self.rect.height)
        for o in bl:
            if jr.colliderect(o):wx=float(o.left-self.rect.width) if self.vel_x>0 else float(o.right);jr.x=int(wx)
        wy+=self.vel_y
        jr=pygame.Rect(int(wx),int(wy),self.rect.width,self.rect.height)
        for o in bl:
            if jr.colliderect(o):wy=float(o.top-self.rect.height) if self.vel_y>0 else float(o.bottom);jr.y=int(wy)
        wx=max(0.0,min(wx,5000.0-self.rect.width))
        wy=max(0.0,min(wy,5000.0-self.rect.height))
        self.camara_x=wx-self._cx; self.camara_y=wy-self._cy
        self.pos_x_absoluta=self.camara_x; self.pos_y_absoluta=self.camara_y
        return True
    def actualizarEstado(self):
        if self.vel_x==0 and self.vel_y==0:self.estado=0
        elif self.corriendo:self.estado=1
        else:self.estado=2