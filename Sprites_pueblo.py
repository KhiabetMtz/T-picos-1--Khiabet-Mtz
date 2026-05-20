import pygame
import math
import random
import heapq
import csv
import os


# ==============================================================
#  Sprite base
# ==============================================================
class Sprite():
    def __init__(self, x, y, w, h, archivo_imagen, pantalla):
        self.rect     = pygame.Rect(x, y, w, h)
        self.pantalla = pantalla
        if archivo_imagen and os.path.exists(str(archivo_imagen)):
            self.imagen = pygame.image.load(archivo_imagen).convert_alpha()
        else:
            self.imagen = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()

    def dibujate(self):
        pygame.draw.rect(self.pantalla, (255, 0, 0), self.rect, 1)
        self.pantalla.blit(self.getImagen(), self.rect)

    def getImagen(self):
        return self.imagen

    def detectaColisiones(self, other):
        return self.rect.colliderect(other.rect)


# ==============================================================
#  TileSet base 
# ==============================================================
class TileSet(Sprite):
    def __init__(self, x, y, w, h, archivo_imagen, pantalla,
                 anchura_tile, altura_tile, personaje):
        super().__init__(x, y, w, h, archivo_imagen, pantalla)
        self.anchura_tile    = anchura_tile
        self.altura_tile     = altura_tile
        self.num_frames      = int(self.imagen.get_width()  / self.anchura_tile) if self.anchura_tile else 1
        self.num_animaciones = int(self.imagen.get_height() / self.altura_tile)  if self.altura_tile  else 1
        self.ImagenesFuenteTile = []
        self.personaje  = personaje
        self.tile_padre = None
        self.mapa       = None
        self.evaluado   = False

        for j in range(self.num_animaciones):
            frames_fila = []
            for i in range(self.num_frames):
                s = pygame.Surface(
                    (self.anchura_tile, self.altura_tile), pygame.SRCALPHA
                ).convert_alpha()
                s.blit(self.imagen, (0, 0),
                       (i * self.anchura_tile, j * self.altura_tile,
                        self.anchura_tile, self.altura_tile))
                s = pygame.transform.scale(s, (self.rect.width, self.rect.height))
                frames_fila.append(s)
            self.ImagenesFuenteTile.append(frames_fila)

    def getTileXDePosicion(self, pos_x):
        return int(pos_x / self.rect.width)

    def getTileYDePosicion(self, pos_y):
        return int(pos_y / self.rect.height)

    def getDistanciaH(self, tile_x, tile_y, tile_destino_x, tile_destino_y):
        return (abs(tile_x - tile_destino_x) + abs(tile_y - tile_destino_y)) * 10

    def getDistanciaG(self, tile_destino_x, tile_destino_y):
        return 0

    def getDistanciaF(self, tile_x, tile_y, tile_destino_x, tile_destino_y):
        self.evaluado = True
        return (self.getDistanciaG(tile_destino_x, tile_destino_y) +
                self.getDistanciaH(tile_x, tile_y, tile_destino_x, tile_destino_y))


# ==============================================================
#  Tile
# ==============================================================
class Tile():
    def __init__(self, x, y, w, h, tipo, imagen, mapa=None):
        self.rect   = pygame.Rect(x, y, w, h)
        self.tipo   = tipo
        self.imagen = imagen
        self.mapa   = mapa
        self.tile_x = int(x / w) if w else 0
        self.tile_y = int(y / h) if h else 0

    def distanciaA(self, tile_destino_x, tile_destino_y):
        return math.hypot(self.tile_x - tile_destino_x,
                          self.tile_y - tile_destino_y)

    def distanciaG(self, tile_destino_x, tile_destino_y):
        dx = abs(self.tile_x - tile_destino_x)
        dy = abs(self.tile_y - tile_destino_y)
        if dx == 1 and dy == 1:
            return 14
        if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
            return 10
        return 0

    def distanciaF(self, tile_destino_x, tile_destino_y):
        return (math.hypot(self.tile_x - tile_destino_x,
                           self.tile_y - tile_destino_y) +
                (abs(self.tile_x - tile_destino_x) +
                 abs(self.tile_y - tile_destino_y)) * 10)

    @property
    def tile_actual(self):
        return (self.tile_x, self.tile_y)


# ==============================================================
#  TileSetPueblo
#  Tipos de tile:
#    0 = hierba   (libre)
#    1 = camino   (costo x2 en A*, más lento)
#    2 = árbol    (obstáculo sólido)
#    3 = agua     (obstáculo sólido)
#    4 = flores   (libre, decorativo)
# ==============================================================
class TileSetPueblo(TileSet):
    def __init__(self, x, y, w, h, archivo_imagen, pantalla,
                 anchura_tile, altura_tile, personaje,
                 archivo_csv=None):
        super().__init__(x, y, w, h, archivo_imagen, pantalla,
                         anchura_tile, altura_tile, personaje)
        self.Tiles       = []
        self.obstaculos  = []
        self.mapa_celdas = {}
        self.imagen_mapa = self._construir_mapa(archivo_csv)

    # ----------------------------------------------------------
    def dibujate(self):
        self.pantalla.blit(
            self.getImagen(),
            (-int(self.personaje.camara_x), -int(self.personaje.camara_y))
        )

    def getImagen(self):
        return self.imagen_mapa

    def get_obstaculos(self):
        return self.obstaculos

    def get_mapa_celdas(self):
        return self.mapa_celdas

    #  helpers visuales 

    def _tile_hierba(self):
        """Tile de hierba reutilizando filas 8-9 del Arena_Tileset."""
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA).convert_alpha()
        if self.num_animaciones > 9:
            fila    = random.randint(8, 9)
            columna = random.randint(0, min(9, self.num_frames - 1))
            s.blit(self.ImagenesFuenteTile[fila][columna], (0, 0))
        else:
            s.fill((80, 160, 60))
            for _ in range(4):
                gx = random.randint(0, self.rect.width  - 2)
                gy = random.randint(0, self.rect.height - 2)
                pygame.draw.line(s, (60, 140, 45), (gx, gy), (gx, gy - 4), 1)
        return s

    def _tile_camino(self):
        """Camino de tierra usando filas 13-16 o generado con código."""
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA).convert_alpha()
        if self.num_animaciones > 13:
            fila    = random.randint(13, min(16, self.num_animaciones - 1))
            columna = random.randint(0, min(2, self.num_frames - 1))
            s.blit(self.ImagenesFuenteTile[fila][columna], (0, 0))
        else:
            s.fill((160, 128, 90))
            for _ in range(5):
                px = random.randint(0, self.rect.width  - 3)
                py = random.randint(0, self.rect.height - 3)
                pygame.draw.rect(s, (140, 110, 78), (px, py, 3, 3))
        return s

    def _tile_flores(self):
        """Hierba con manchas de flores de colores."""
        s = self._tile_hierba()
        colores = [(255, 80, 140), (255, 220, 30), (200, 90, 255), (255, 140, 40)]
        for _ in range(random.randint(2, 4)):
            fx = random.randint(5, self.rect.width  - 5)
            fy = random.randint(5, self.rect.height - 5)
            c  = random.choice(colores)
            pygame.draw.circle(s, c,             (fx, fy), 3)
            pygame.draw.circle(s, (255, 255, 200), (fx, fy), 1)
        return s

    def _tile_arbol_copa(self):
        """Parte superior del árbol"""
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA).convert_alpha()
        s.blit(self._tile_hierba(), (0, 0))
        cx, cy = self.rect.width // 2, self.rect.height // 2
        for radio, color in [(14, (25, 120, 30)), (11, (35, 150, 40)), (8, (50, 170, 55))]:
            pygame.draw.circle(s, color, (cx, cy), radio)
        return s

    def _tile_arbol_tronco(self):
        """Parte inferior del árbol — tronco marrón."""
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA).convert_alpha()
        s.blit(self._tile_hierba(), (0, 0))
        cx     = self.rect.width // 2
        tw, th = max(6, self.rect.width // 5), self.rect.height // 2
        pygame.draw.rect(s, (100, 65, 30), (cx - tw // 2, 0, tw, th))
        pygame.draw.rect(s, (125, 82, 42), (cx - tw // 2 + 2, 0, 3, th))
        return s

    def _tile_agua(self):
        """Tile de lago azul con líneas de onda."""
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA).convert_alpha()
        s.fill((55, 155, 220))
        for i in range(0, self.rect.width, 8):
            pygame.draw.line(s, (90, 185, 245),
                             (i,     self.rect.height // 3),
                             (i + 4, self.rect.height // 3), 1)
            pygame.draw.line(s, (90, 185, 245),
                             (i + 2, self.rect.height * 2 // 3),
                             (i + 6, self.rect.height * 2 // 3), 1)
        return s

    # CSV 
    def _leer_csv(self, archivo_csv):
        if not os.path.exists(archivo_csv):
            print(f"[AVISO] '{archivo_csv}' no encontrado — generando mapa procedural.")
            return []
        mapa = []
        with open(archivo_csv, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for fila in reader:
                vals = [int(v) for v in fila if v.strip() != '']
                if vals:
                    mapa.append(vals)
        print(f"[CSV] Mapa cargado: {len(mapa)} filas x {len(mapa[0]) if mapa else 0} cols")
        return mapa

    # construcción principal
    def _construir_mapa(self, archivo_csv=None):
        tw = self.rect.width
        th = self.rect.height
        ANCHO_MAPA = 5000
        ALTO_MAPA  = 5000
        num_col    = ANCHO_MAPA // tw + 1
        num_fil    = ALTO_MAPA  // th + 1

        superficie = pygame.Surface(
            (ANCHO_MAPA, ALTO_MAPA), pygame.SRCALPHA
        ).convert_alpha()

        mapa_csv = []
        if archivo_csv:
            mapa_csv = self._leer_csv(archivo_csv)

        # Paso 1: llenar toda la cuadrícula con hierba base
        for j in range(num_fil):
            fila_tiles = []
            for i in range(num_col):
                if mapa_csv and j < len(mapa_csv) and i < len(mapa_csv[j]):
                    tipo = mapa_csv[j][i]
                else:
                    tipo = 0
                self.mapa_celdas[(i, j)] = tipo
                img = self._tile_hierba() if tipo == 0 else self._tile_camino()
                fila_tiles.append(Tile(i * tw, j * th, tw, th, tipo, img))
            self.Tiles.append(fila_tiles)

        # Paso 2: si no hay CSV, generar elementos del pueblo
        if not mapa_csv:
            self._generar_caminos(num_col, num_fil)
            self._generar_bosques(num_col, num_fil, tw, th)
            self._generar_lago(num_col, num_fil, tw, th)
            self._generar_flores(num_col, num_fil)

        # Paso 3: blit final al surface del mapa
        for fila in self.Tiles:
            for tile in fila:
                superficie.blit(tile.imagen, tile.rect)

        return superficie

    def _generar_caminos(self, num_col, num_fil):
        """Cruz central de caminos de tierra."""
        cy = num_fil // 2
        cx = num_col // 2
        for i in range(num_col):
            for dy in range(-1, 2):
                j = cy + dy
                if 0 <= j < num_fil:
                    self.Tiles[j][i].tipo    = 1
                    self.Tiles[j][i].imagen  = self._tile_camino()
                    self.mapa_celdas[(i, j)] = 1
        for j in range(num_fil):
            for dx in range(-1, 2):
                i = cx + dx
                if 0 <= i < num_col:
                    self.Tiles[j][i].tipo    = 1
                    self.Tiles[j][i].imagen  = self._tile_camino()
                    self.mapa_celdas[(i, j)] = 1

    def _generar_bosques(self, num_col, num_fil, tw, th):
        """Grupos de árboles en las esquinas y lados del mapa."""
        spawn_tx  = 2400 // tw
        spawn_ty  = 2400 // th
        zona_safe = 12

        centros = [
            (num_col // 5,         num_fil // 5),
            (num_col * 4 // 5,     num_fil // 5),
            (num_col // 5,         num_fil * 4 // 5),
            (num_col * 4 // 5,     num_fil * 4 // 5),
            (num_col // 3,         num_fil // 2 + 20),
            (num_col * 2 // 3,     num_fil // 3),
        ]

        for (bcx, bcy) in centros:
            if abs(bcx - spawn_tx) < zona_safe and abs(bcy - spawn_ty) < zona_safe:
                continue
            radio = random.randint(4, 7)
            for dj in range(-radio, radio + 1):
                for di in range(-radio, radio + 1):
                    if di * di + dj * dj > radio * radio:
                        continue
                    i, j = bcx + di, bcy + dj
                    if not (1 <= i < num_col - 1 and 1 <= j < num_fil - 2):
                        continue
                    if self.mapa_celdas.get((i, j), 0) == 1:
                        continue

                    self.Tiles[j][i].tipo    = 2
                    self.Tiles[j][i].imagen  = self._tile_arbol_copa()
                    self.mapa_celdas[(i, j)] = 2
                    if j + 1 < num_fil:
                        self.Tiles[j+1][i].tipo    = 2
                        self.Tiles[j+1][i].imagen  = self._tile_arbol_tronco()
                        self.mapa_celdas[(i, j+1)] = 2
                    self.obstaculos.append(
                        pygame.Rect(i * tw, j * th, tw, th * 2)
                    )

    def _generar_lago(self, num_col, num_fil, tw, th):
        """Lago elíptico en el cuadrante noreste."""
        lago_cx = num_col * 3 // 4
        lago_cy = num_fil // 4
        rx, ry  = 9, 7

        for dj in range(-ry, ry + 1):
            for di in range(-rx, rx + 1):
                if (di / rx) ** 2 + (dj / ry) ** 2 > 1.0:
                    continue
                i, j = lago_cx + di, lago_cy + dj
                if not (0 <= i < num_col and 0 <= j < num_fil):
                    continue
                self.Tiles[j][i].tipo    = 3
                self.Tiles[j][i].imagen  = self._tile_agua()
                self.mapa_celdas[(i, j)] = 3

        self.obstaculos.append(
            pygame.Rect((lago_cx - rx) * tw, (lago_cy - ry) * th,
                        rx * 2 * tw,          ry * 2 * th)
        )

    def _generar_flores(self, num_col, num_fil):
        """Parches de flores dispersos por el mapa (tipo 4, pisables)."""
        for _ in range(100):
            i = random.randint(2, num_col - 3)
            j = random.randint(2, num_fil - 3)
            if self.mapa_celdas.get((i, j), 0) == 0:
                self.Tiles[j][i].tipo    = 4
                self.Tiles[j][i].imagen  = self._tile_flores()
                self.mapa_celdas[(i, j)] = 4

    def getTileActual(self):
        px, py = self.personaje.get_pos_mundo()
        x = max(0, min(int(px / self.rect.width),  len(self.Tiles[0]) - 1))
        y = max(0, min(int(py / self.rect.height), len(self.Tiles)    - 1))
        return self.Tiles[y][x]


# ==============================================================
#  Sprite Animado 
# ==============================================================
class SpriteAnimado(TileSet):
    def __init__(self, x, y, w, h, archivo_imagen, pantalla,
                 anchura_tile, altura_tile, personaje):
        super().__init__(x, y, w, h, archivo_imagen, pantalla,
                         anchura_tile, altura_tile, personaje)
        self.animacion       = 1
        self.frame           = 0
        self.cont_frames     = 0
        self.max_cont_frames = 25
        self.estado          = 0

    def setMaxContFrames(self, vel):
        v = max(1, abs(vel))
        self.max_cont_frames = max(1, min(25, int(40 / v)))


# ==============================================================
#  Item  —  (manzanas, flores, conchas, estrellas de mar, naranjas)
# ==============================================================
class Item():
    COLORES = {
        'manzana':  (210,  45,  45),
        'naranja':  (255, 145,   0),
        'flor':     (255,  80, 175),
        'concha':   (240, 215, 165),
        'estrella': (255, 225,  30),
    }

    def __init__(self, x, y, tipo='manzana'):
        self.rect     = pygame.Rect(x, y, 24, 24)
        self.tipo     = tipo
        self.recogido = False
        self._brillo      = 0
        self._dir_brillo  = 1

    def actualizar(self):
        """Pequeña animación de brillo para llamar la atención"""
        self._brillo += self._dir_brillo * 2
        if self._brillo >= 40 or self._brillo <= 0:
            self._dir_brillo *= -1

    def dibujate(self, pantalla, camara_x, camara_y):
        if self.recogido:
            return
        sx = self.rect.x - int(camara_x)
        sy = self.rect.y - int(camara_y)

        # Sombra
        pygame.draw.ellipse(pantalla, (0, 0, 0),
                            (sx + 4, sy + 19, 16, 5))

        c = self.COLORES.get(self.tipo, (255, 255, 255))

        if self.tipo in ('manzana', 'naranja'):
            pygame.draw.circle(pantalla, c,                    (sx + 12, sy + 12), 8)
            pygame.draw.circle(pantalla, tuple(min(255, v+60) for v in c), (sx + 9, sy + 9), 3)
            pygame.draw.line(pantalla, (50, 110, 30), (sx + 12, sy + 4), (sx + 12, sy), 2)

        elif self.tipo == 'flor':
            for ang in range(0, 360, 72):
                r  = math.radians(ang)
                px = sx + 12 + int(math.cos(r) * 6)
                py = sy + 12 + int(math.sin(r) * 6)
                pygame.draw.circle(pantalla, c, (px, py), 4)
            pygame.draw.circle(pantalla, (255, 240, 100), (sx + 12, sy + 12), 4)

        elif self.tipo == 'concha':
            pygame.draw.ellipse(pantalla, c, (sx + 2, sy + 6, 20, 12))
            for k in range(3):
                pygame.draw.arc(pantalla, (200, 180, 130),
                                (sx + 2 + k*4, sy + 6, 20 - k*4, 12),
                                0, math.pi, 1)

        elif self.tipo == 'estrella':
            pts = []
            for k in range(10):
                ang = math.radians(k * 36 - 90)
                r   = 9 if k % 2 == 0 else 4
                pts.append((sx + 12 + int(math.cos(ang) * r),
                             sy + 12 + int(math.sin(ang) * r)))
            pygame.draw.polygon(pantalla, c, pts)

        # Halo de brillo
        if self._brillo > 8:
            glow = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 255, self._brillo),
                               (12, 12), 11)
            pantalla.blit(glow, (sx, sy))


# ==============================================================
#  A*  —  algoritmo de pathfinding para que los aldeanos encuentren su camino
#  tipo 0 → costo x1  (hierba normal)
#  tipo 1 → costo x2  (camino de tierra)
#  tipo 2/3 → bloqueado
# ==============================================================
def _astar(inicio, destino, obstaculos, ancho_ente, alto_ente,
           tam_celda=32, mapa_ancho=5000, mapa_alto=5000,
           mapa_celdas=None):

    def mundo_a_celda(wx, wy):
        return (int(wx) // tam_celda, int(wy) // tam_celda)

    def celda_a_mundo(cx, cy):
        return (cx * tam_celda, cy * tam_celda)

    def costo_celda(celda):
        if not mapa_celdas:
            return 1.0
        return 2.0 if mapa_celdas.get(celda, 0) == 1 else 1.0

    celdas_extra_x = max(0, (ancho_ente - 1) // tam_celda)
    celdas_extra_y = max(0, (alto_ente  - 1) // tam_celda)

    celdas_bloqueadas = set()
    for obs in obstaculos:
        cx0 = obs.left   // tam_celda
        cy0 = obs.top    // tam_celda
        cx1 = (obs.right  - 1) // tam_celda
        cy1 = (obs.bottom - 1) // tam_celda
        for cy in range(cy0 - celdas_extra_y, cy1 + 1):
            for cx in range(cx0 - celdas_extra_x, cx1 + 1):
                celdas_bloqueadas.add((cx, cy))

    max_cx = mapa_ancho // tam_celda
    max_cy = mapa_alto  // tam_celda

    inicio_c  = mundo_a_celda(*inicio)
    destino_c = mundo_a_celda(*destino)

    if destino_c in celdas_bloqueadas:
        mejor, mejor_dist = None, float('inf')
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                nc = (destino_c[0] + dx, destino_c[1] + dy)
                if nc not in celdas_bloqueadas:
                    d = abs(dx) + abs(dy)
                    if d < mejor_dist:
                        mejor_dist, mejor = d, nc
        if mejor:
            destino_c = mejor
        else:
            return []

    if inicio_c == destino_c:
        return [celda_a_mundo(*destino_c)]

    vecinos = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    costos  = [1.0, 1.0, 1.0, 1.0, 1.414, 1.414, 1.414, 1.414]

    abierta  = []
    heapq.heappush(abierta, (0.0, inicio_c))
    g_score  = {inicio_c: 0.0}
    vinieron = {}
    max_nodos, visitados = 2000, 0

    while abierta and visitados < max_nodos:
        _, actual = heapq.heappop(abierta)
        visitados += 1

        if actual == destino_c:
            camino, nodo = [], actual
            while nodo in vinieron:
                camino.append(celda_a_mundo(*nodo))
                nodo = vinieron[nodo]
            camino.reverse()
            return camino

        for k, (dx, dy) in enumerate(vecinos):
            vecino = (actual[0] + dx, actual[1] + dy)
            if vecino in celdas_bloqueadas:
                continue
            if not (0 <= vecino[0] < max_cx and 0 <= vecino[1] < max_cy):
                continue
            if dx != 0 and dy != 0:
                if (actual[0]+dx, actual[1]) in celdas_bloqueadas:
                    continue
                if (actual[0], actual[1]+dy) in celdas_bloqueadas:
                    continue

            nuevo_g = g_score[actual] + costos[k] * costo_celda(vecino)
            if nuevo_g < g_score.get(vecino, float('inf')):
                g_score[vecino] = nuevo_g
                hdx = abs(vecino[0] - destino_c[0])
                hdy = abs(vecino[1] - destino_c[1])
                h   = max(hdx, hdy) + 0.414 * min(hdx, hdy)
                heapq.heappush(abierta, (nuevo_g + h, vecino))
                vinieron[vecino] = actual

    return []


# ==============================================================
#  Aldeano
#  NPC amigable que deambula por su zona.
#  Máquina de estados:
#    DEAMBULAR (0) → camina a destinos aleatorios dentro de su zona
#    SALUDAR   (1) → se acerca al jugador y muestra un diálogo
#    REGRESAR  (2) → vuelve a su posición base
# ==============================================================
class Aldeano():
    DEAMBULAR = 0
    SALUDAR   = 1
    REGRESAR  = 2

    PALETA = [
        ((255, 200,  95), (180, 120,  55)),
        (( 95, 195, 255), ( 55, 130, 185)),
        ((200, 110, 255), (130,  65, 205)),
        (( 95, 220, 125), ( 55, 160,  80)),
        ((255, 125,  95), (200,  75,  55)),
        ((255, 255, 155), (200, 200,  80)),
    ]

    def __init__(self, x, y, w, h, vel,
                 zona_cx, zona_cy, zona_radio,
                 pantalla, personaje,
                 nombre='Aldeano', indice_color=0):
        self.rect         = pygame.Rect(x, y, w, h)
        self.pantalla     = pantalla
        self.personaje    = personaje
        self.nombre       = nombre
        self.vel          = vel

        self.zona_cx      = float(zona_cx)
        self.zona_cy      = float(zona_cy)
        self.zona_radio   = zona_radio

        self.pos_x_mundo  = float(x)
        self.pos_y_mundo  = float(y)
        self.pos_base_x   = float(x)
        self.pos_base_y   = float(y)

        self.vel_x = 0.0
        self.vel_y = 0.0

        self.estado = self.DEAMBULAR

        self.destino_x    = float(x)
        self.destino_y    = float(y)

        self.tiempo_espera  = random.randint(30, 120)
        self.frame          = 0
        self.cont_frames    = 0

        self.dialogo        = ''
        self.tiempo_dialogo = 0

        idx = indice_color % len(self.PALETA)
        self.color_cuerpo  = self.PALETA[idx][0]
        self.color_sombra  = self.PALETA[idx][1]

        self._frames = self._generar_frames(w, h)
        self._fuente = None   

    def _generar_frames(self, w, h):
        """Genera 4 fotogramas de animación"""
        frames = []
        for f in range(4):
            s = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
            cx, cy = w // 2, h // 2

            # Sombra elíptica en el suelo
            pygame.draw.ellipse(s, (0, 0, 0), (cx - 12, h - 10, 24, 7))

            # Piernas alternadas para simular caminar
            offset = [0, 5, 0, -5][f]
            pygame.draw.rect(s, self.color_sombra,
                             (cx - 9, cy + 5, 6, 11 + offset))
            pygame.draw.rect(s, self.color_sombra,
                             (cx + 3, cy + 5, 6, 11 - offset))

            # Cuerpo
            pygame.draw.ellipse(s, self.color_cuerpo,
                                (cx - 13, cy - 6, 26, 18))

            # Cabeza
            pygame.draw.circle(s, self.color_cuerpo, (cx, cy - 11), 12)

            # Orejas de animal (triangulares)
            pygame.draw.polygon(s, self.color_sombra, [
                (cx - 10, cy - 19), (cx -  4, cy - 30), (cx,      cy - 19)])
            pygame.draw.polygon(s, self.color_sombra, [
                (cx,       cy - 19), (cx +  4, cy - 30), (cx + 10, cy - 19)])

            # Ojos
            ojo_y = cy - 13
            pygame.draw.circle(s, (30, 30, 30), (cx - 4, ojo_y), 3)
            pygame.draw.circle(s, (30, 30, 30), (cx + 4, ojo_y), 3)
            pygame.draw.circle(s, (255, 255, 255), (cx - 3, ojo_y - 1), 1)
            pygame.draw.circle(s, (255, 255, 255), (cx + 5, ojo_y - 1), 1)

            # Nariz pequeña
            pygame.draw.ellipse(s, self.color_sombra, (cx - 2, cy - 8, 4, 3))

            frames.append(s)
        return frames

    def getImagen(self):
        self.cont_frames += 1
        vel_mag = math.hypot(self.vel_x, self.vel_y)
        if vel_mag > 0.1:
            intervalo = max(3, int(18 / vel_mag))
            if self.cont_frames > intervalo:
                self.cont_frames = 0
                self.frame = (self.frame + 1) % 4
        else:
            self.frame = 0

        img = self._frames[self.frame]
        if self.vel_x < 0:
            img = pygame.transform.flip(img, True, False)
        return img

    def dibujate(self, personaje=None):
        ref = personaje or self.personaje
        sx  = int(self.pos_x_mundo - ref.camara_x)
        sy  = int(self.pos_y_mundo - ref.camara_y)

        self.pantalla.blit(self.getImagen(),
                           pygame.Rect(sx, sy, self.rect.width, self.rect.height))

        if self._fuente is None:
            self._fuente = pygame.font.SysFont(None, 16)

        # Nombre sobre el personaje
        nom = self._fuente.render(self.nombre, True, (255, 255, 255))
        self.pantalla.blit(nom,
                           (sx + self.rect.width // 2 - nom.get_width() // 2,
                            sy - 16))

        # Burbuja de diálogo
        if self.estado == self.SALUDAR and self.dialogo:
            fuente2 = pygame.font.SysFont(None, 18)
            txt     = fuente2.render(f'"{self.dialogo}"', True, (40, 40, 40))
            bx = sx + self.rect.width // 2 - txt.get_width() // 2
            by = sy - 34
            fondo = pygame.Surface(
                (txt.get_width() + 10, txt.get_height() + 8), pygame.SRCALPHA
            )
            fondo.fill((255, 250, 220, 210))
            pygame.draw.rect(fondo, (200, 185, 130),
                             (0, 0, fondo.get_width(), fondo.get_height()), 1)
            self.pantalla.blit(fondo, (bx - 5, by - 4))
            self.pantalla.blit(txt,   (bx,     by))

    def muevete(self, personaje, obstaculos=None):
        match self.estado:
            case 0: self._deambular(personaje)
            case 1: self._saludar(personaje)
            case 2: self._regresar(personaje)

        bloqueantes = (obstaculos.get_obstaculos()
                       if hasattr(obstaculos, 'get_obstaculos')
                       else (obstaculos if isinstance(obstaculos, list) else []))

        # Movimiento en X con colisión
        self.pos_x_mundo += self.vel_x
        mi = pygame.Rect(int(self.pos_x_mundo), int(self.pos_y_mundo),
                         self.rect.width, self.rect.height)
        for obs in bloqueantes:
            if mi.colliderect(obs):
                if self.vel_x > 0:
                    self.pos_x_mundo = float(obs.left - self.rect.width)
                else:
                    self.pos_x_mundo = float(obs.right)
                mi.x   = int(self.pos_x_mundo)
                self.vel_x = 0

        # Movimiento en Y con colisión
        self.pos_y_mundo += self.vel_y
        mi = pygame.Rect(int(self.pos_x_mundo), int(self.pos_y_mundo),
                         self.rect.width, self.rect.height)
        for obs in bloqueantes:
            if mi.colliderect(obs):
                if self.vel_y > 0:
                    self.pos_y_mundo = float(obs.top - self.rect.height)
                else:
                    self.pos_y_mundo = float(obs.bottom)
                mi.y   = int(self.pos_y_mundo)
                self.vel_y = 0

        # No salir del mapa
        self.pos_x_mundo = max(0.0, min(self.pos_x_mundo, 4960.0))
        self.pos_y_mundo = max(0.0, min(self.pos_y_mundo, 4960.0))

    def _deambular(self, personaje):
        if self.tiempo_espera > 0:
            self.vel_x = self.vel_y = 0
            self.tiempo_espera -= 1
            if self._ver_personaje(personaje, radio=220):
                self.estado = self.SALUDAR
                self._elegir_dialogo()
            return

        dx   = self.destino_x - self.pos_x_mundo
        dy   = self.destino_y - self.pos_y_mundo
        dist = math.hypot(dx, dy)

        if dist < abs(self.vel) * 2 or dist == 0:
            self.vel_x = self.vel_y = 0
            self.tiempo_espera = random.randint(60, 200)
            ang = random.uniform(0, 2 * math.pi)
            r   = random.uniform(0, self.zona_radio)
            self.destino_x = max(50, min(4900, self.zona_cx + math.cos(ang) * r))
            self.destino_y = max(50, min(4900, self.zona_cy + math.sin(ang) * r))
        else:
            self.vel_x = (dx / dist) * abs(self.vel)
            self.vel_y = (dy / dist) * abs(self.vel)

        if self._ver_personaje(personaje, radio=220):
            self.estado = self.SALUDAR
            self._elegir_dialogo()

    def _saludar(self, personaje):
        px, py = personaje.get_pos_mundo()
        dx = px - self.pos_x_mundo
        dy = py - self.pos_y_mundo
        dist = math.hypot(dx, dy)

        if dist > 85:
            spd = abs(self.vel) * 0.6
            self.vel_x = (dx / dist) * spd
            self.vel_y = (dy / dist) * spd
        else:
            self.vel_x = self.vel_y = 0
            self.tiempo_dialogo += 1
            if self.tiempo_dialogo > 160:
                self.tiempo_dialogo = 0
                self.dialogo        = ''
                self.estado         = self.REGRESAR

        if not self._ver_personaje(personaje, radio=380):
            self.dialogo = ''
            self.estado  = self.REGRESAR

    def _regresar(self, personaje=None):
        dx   = self.pos_base_x - self.pos_x_mundo
        dy   = self.pos_base_y - self.pos_y_mundo
        dist = math.hypot(dx, dy)

        if dist < abs(self.vel) * 2:
            self.pos_x_mundo   = self.pos_base_x
            self.pos_y_mundo   = self.pos_base_y
            self.vel_x = self.vel_y = 0
            self.estado        = self.DEAMBULAR
            self.tiempo_espera = 60
        else:
            self.vel_x = (dx / dist) * abs(self.vel)
            self.vel_y = (dy / dist) * abs(self.vel)

        if personaje and self._ver_personaje(personaje, radio=220):
            self.estado = self.SALUDAR
            self._elegir_dialogo()

    def _elegir_dialogo(self):
        frases = [
            '¡Hola, viajero!',
            '¡Qué bonito dia!',
            '¿Has visto las flores?',
            'Me gusta este pueblo.',
            '¡Buenos dias!',
            'Las manzanas estan ricas.',
            'El lago se ve precioso.',
            '¿Ya recogiste frutas hoy?',
            'Hace fresquito',
            '¡Te estaba buscando!',
            '¡Abrazame!',
        ]
        self.dialogo        = random.choice(frases)
        self.tiempo_dialogo = 0

    def _ver_personaje(self, personaje, radio=220):
        px, py = personaje.get_pos_mundo()
        return math.hypot(px - self.pos_x_mundo, py - self.pos_y_mundo) < radio


# ==============================================================
#  Habitante  (aldeano especial con A*)
#  Igual que Aldeano pero los estados SALUDAR y REGRESAR
# ==============================================================
class Habitante(Aldeano):
    def __init__(self, x, y, w, h, vel,
                 zona_cx, zona_cy, zona_radio,
                 pantalla, personaje,
                 nombre='Habitante', indice_color=0,
                 mapa_celdas=None):
        super().__init__(x, y, w, h, vel,
                         zona_cx, zona_cy, zona_radio,
                         pantalla, personaje,
                         nombre, indice_color)
        self.mapa_celdas          = mapa_celdas or {}
        self._camino              = []
        self._indice_camino       = 0
        self._frames_recalculo    = 0
        self._intervalo_recalculo = 20
        self._obstaculos_ref      = []

    def set_mapa_celdas(self, mapa_celdas):
        self.mapa_celdas = mapa_celdas

    def muevete(self, personaje, obstaculos=None):
        if hasattr(obstaculos, 'get_obstaculos'):
            self._obstaculos_ref = obstaculos.get_obstaculos()
        elif isinstance(obstaculos, list):
            self._obstaculos_ref = obstaculos
        else:
            self._obstaculos_ref = []
        super().muevete(personaje, obstaculos)

    def _saludar(self, personaje):
        """Usa A* para acercarse al jugador sorteando obstáculos."""
        px, py = personaje.get_pos_mundo()
        dist   = math.hypot(px - self.pos_x_mundo, py - self.pos_y_mundo)

        if dist <= 85:
            self.vel_x = self.vel_y = 0
            self.tiempo_dialogo += 1
            if self.tiempo_dialogo > 200:
                self.tiempo_dialogo = 0
                self.dialogo        = ''
                self.estado         = self.REGRESAR
                self._camino        = []
            return

        self._frames_recalculo += 1
        if self._frames_recalculo >= self._intervalo_recalculo or not self._camino:
            self._frames_recalculo = 0
            self._camino = _astar(
                (self.pos_x_mundo, self.pos_y_mundo),
                (px, py),
                self._obstaculos_ref,
                self.rect.width, self.rect.height,
                mapa_celdas=self.mapa_celdas
            )
            self._indice_camino = 0

        self._seguir_camino()

        if not self._ver_personaje(personaje, radio=450):
            self.dialogo = ''
            self.estado  = self.REGRESAR
            self._camino = []

    def _regresar(self, personaje=None):
        """Usa A* para volver a su posición base"""
        dx   = self.pos_base_x - self.pos_x_mundo
        dy   = self.pos_base_y - self.pos_y_mundo
        dist = math.hypot(dx, dy)

        if dist <= abs(self.vel) * 2:
            self.pos_x_mundo = self.pos_base_x
            self.pos_y_mundo = self.pos_base_y
            self.vel_x = self.vel_y = 0
            self.estado  = self.DEAMBULAR
            self._camino = []
            return

        self._frames_recalculo += 1
        if self._frames_recalculo >= self._intervalo_recalculo or not self._camino:
            self._frames_recalculo = 0
            self._camino = _astar(
                (self.pos_x_mundo, self.pos_y_mundo),
                (self.pos_base_x,  self.pos_base_y),
                self._obstaculos_ref,
                self.rect.width, self.rect.height,
                mapa_celdas=self.mapa_celdas
            )
            self._indice_camino = 0

        self._seguir_camino()

        if personaje and self._ver_personaje(personaje, radio=260):
            self.estado = self.SALUDAR
            self._elegir_dialogo()
            self._camino = []

    def _seguir_camino(self):
        """Avanza al siguiente waypoint del camino A*."""
        if not (self._camino and self._indice_camino < len(self._camino)):
            self.vel_x = self.vel_y = 0
            return

        ox, oy  = self._camino[self._indice_camino]
        dx, dy  = ox - self.pos_x_mundo, oy - self.pos_y_mundo
        dist_wp = math.hypot(dx, dy)

        if dist_wp < abs(self.vel) * 2:
            self._indice_camino += 1
            if self._indice_camino < len(self._camino):
                ox, oy  = self._camino[self._indice_camino]
                dx, dy  = ox - self.pos_x_mundo, oy - self.pos_y_mundo
                dist_wp = math.hypot(dx, dy)

        if dist_wp > 0.5:
            self.vel_x = (dx / dist_wp) * abs(self.vel)
            self.vel_y = (dy / dist_wp) * abs(self.vel)
        else:
            self.vel_x = self.vel_y = 0


# ==============================================================
#  Personaje 
# ==============================================================
class Personaje(Sprite):
    def __init__(self, x, y, w, h, archivo_imagen, pantalla):
        super().__init__(x, y, w, h, archivo_imagen, pantalla)
        self.vel    = 5
        self.vel_x  = 0
        self.vel_y  = 0
        self.cuadro     = 0
        self.aux_cuadro = 0
        self.corriendo  = False
        self.estado     = 0

        self._cx = pantalla.get_width()  // 2 - w // 2
        self._cy = pantalla.get_height() // 2 - h // 2

        self.camara_x       = float(x) - self._cx
        self.camara_y       = float(y) - self._cy
        self.pos_x_absoluta = self.camara_x
        self.pos_y_absoluta = self.camara_y

        self.inventario     = []
        self.max_inventario = 10
        self.recoger_activo = False

    def get_pos_mundo(self):
        return (self.camara_x + self._cx, self.camara_y + self._cy)

    def _get_rect_mundo(self):
        mx, my = self.get_pos_mundo()
        return pygame.Rect(int(mx), int(my), self.rect.width, self.rect.height)

    def dibujate(self):
        pygame.draw.rect(
            self.pantalla, (255, 255, 0),
            (self._cx, self._cy, self.rect.width, self.rect.height), 1
        )
        self.pantalla.blit(self.getImagen(), (self._cx, self._cy))

    def getImagen(self):
        imagen = pygame.Surface((32, 32), pygame.SRCALPHA).convert_alpha()
        match self.estado:
            case 0: animacion, max_cuadros, max_aux = 0, 12, 10
            case 1: animacion, max_cuadros, max_aux = 1,  7, 10
            case 2: animacion, max_cuadros, max_aux = 1,  7,  5
            case _: animacion, max_cuadros, max_aux = 0, 12, 10

        imagen.blit(self.imagen, (0, 0),
                    (self.cuadro * 32, animacion * 32, 32, 32))
        imagen = pygame.transform.scale(imagen, (self.rect.width, self.rect.height))

        if self.vel_x < 0:
            imagen = pygame.transform.flip(imagen, True, False)

        self.aux_cuadro += 1
        if self.aux_cuadro > max_aux:
            self.aux_cuadro = 0
            self.cuadro    += 1
            if self.cuadro > max_cuadros:
                self.cuadro = 0
        return imagen

    def recoger_item(self, items):
        """Intenta recoger un ítem cercano cuando se presiona ESPACIO."""
        if not self.recoger_activo:
            return None
        self.recoger_activo = False
        mx, my = self.get_pos_mundo()
        zona = pygame.Rect(int(mx) - 24, int(my) - 24,
                           self.rect.width + 48, self.rect.height + 48)
        for item in items:
            if not item.recogido and zona.colliderect(item.rect):
                if len(self.inventario) < self.max_inventario:
                    item.recogido = True
                    self.inventario.append(item.tipo)
                    return item.tipo
        return None

    def muevete(self, obstaculos=None):
        self.recoger_activo = False

        for evento in pygame.event.get():
            if evento.type == pygame.KEYUP:
                if evento.key == pygame.K_LEFT:   self.vel_x = 0
                if evento.key == pygame.K_RIGHT:  self.vel_x = 0
                if evento.key == pygame.K_UP:     self.vel_y = 0
                if evento.key == pygame.K_DOWN:   self.vel_y = 0
                if evento.key == pygame.K_LSHIFT:
                    self.vel_x   /= 2
                    self.corriendo = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:   self.vel_x = -self.vel
                if evento.key == pygame.K_RIGHT:  self.vel_x =  self.vel
                if evento.key == pygame.K_UP:     self.vel_y = -self.vel
                if evento.key == pygame.K_DOWN:   self.vel_y =  self.vel
                if evento.key == pygame.K_ESCAPE: return False
                if evento.key == pygame.K_LSHIFT:
                    self.vel_x   *= 2
                    self.corriendo = True
                if evento.key == pygame.K_SPACE:
                    self.recoger_activo = True
            if evento.type == pygame.QUIT:
                return False

        self.actualizarEstado()

        bloqueantes = (obstaculos.get_obstaculos()
                       if hasattr(obstaculos, 'get_obstaculos')
                       else (obstaculos if isinstance(obstaculos, list) else []))

        mundo_x, mundo_y = self.get_pos_mundo()

        mundo_x += self.vel_x
        jr = pygame.Rect(int(mundo_x), int(mundo_y), self.rect.width, self.rect.height)
        for obs in bloqueantes:
            if jr.colliderect(obs):
                mundo_x = (float(obs.left - self.rect.width)
                            if self.vel_x > 0 else float(obs.right))
                jr.x = int(mundo_x)

        mundo_y += self.vel_y
        jr = pygame.Rect(int(mundo_x), int(mundo_y), self.rect.width, self.rect.height)
        for obs in bloqueantes:
            if jr.colliderect(obs):
                mundo_y = (float(obs.top - self.rect.height)
                            if self.vel_y > 0 else float(obs.bottom))
                jr.y = int(mundo_y)

        mundo_x = max(0.0, min(mundo_x, 5000.0 - self.rect.width))
        mundo_y = max(0.0, min(mundo_y, 5000.0 - self.rect.height))

        self.camara_x       = mundo_x - self._cx
        self.camara_y       = mundo_y - self._cy
        self.pos_x_absoluta = self.camara_x
        self.pos_y_absoluta = self.camara_y
        return True

    def actualizarEstado(self):
        if   self.vel_x == 0 and self.vel_y == 0: self.estado = 0
        elif self.corriendo:                        self.estado = 1
        else:                                       self.estado = 2
