
import pygame
import math
import random
import os


class Sprite():
    def __init__(self,x, y, w, h, pantalla):
        self.w = int(w*1)
        self.h = int(h*1)
        self.rect = pygame.Rect(x, y, self.w, self.h)
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.pantalla = pantalla
        
        
        ruta_base = os.path.dirname(__file__)
        ruta_imagen = os.path.join(ruta_base, 'monitoB.png')
        ruta_imagen2 = os.path.join(ruta_base, 'Bat_Sprites.png')
        
        try:
            self.imagen = pygame.image.load(ruta_imagen).convert_alpha()
            self.imagen2 = pygame.image.load(ruta_imagen2).convert_alpha()
        except pygame.error as e:
            print(f"No se pudo cargar la imagen: {e}")
            self.imagen = pygame.Surface((32, 32))
            self.imagen2 = pygame.Surface((16, 24))
            

    def dibujate(self):
        self.pantalla.blit(self.getImagen(), self.rect)

    def getImagen(self):
        return self.imagen
    
    def detectaColision(self, other):
        return self.rect.colliderect(other.rect)
    
    def update_rect(self):
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)


class TileSet (Sprite):
    def __init__(self, x, y, w, h, ruta_imagen3, pantalla, anchura_Tile, altura_Tile):
        super().__init__(x, y, w, h, pantalla)
        
        ruta_base = os.path.dirname(__file__)
        ruta_ts = os.path.join(ruta_base, ruta_imagen3)
        
        try:
            self.imagen = pygame.image.load(ruta_ts).convert_alpha()
            
        except (pygame.error, FileNotFoundError) as e:
            print(f" No se pudo cargar el tileset: {e}")
            print(f"   Buscando en: {ruta_ts}")
            print("   Archivos en la carpeta:")
            for f in sorted(os.listdir(ruta_base)):
                print(f"     → {f}")
            raise  
        self.anchura_Tile = int(anchura_Tile)
        self.altura_Tile = int(altura_Tile)
        self.num_frames = self.imagen.get_width() // self.anchura_Tile
        self.num_animaciones = self.imagen.get_height() // self.altura_Tile
        
        self.ImagenesFuenteTile = []
        
        for j in range(self.num_animaciones):
            fila_frames = []
            for i in range(self.num_frames):
                frame = pygame.Surface((self.anchura_Tile, self.altura_Tile), pygame.SRCALPHA).convert_alpha()
                frame.blit(self.imagen, (0, 0), (i * self.anchura_Tile, j * self.altura_Tile, self.anchura_Tile, self.altura_Tile))
                
                fila_frames.append(frame)
            self.ImagenesFuenteTile.append(fila_frames)

    def getImagen(self):
        return self.ImagenesFuenteTile[0][0]

    

class TileSetArena(TileSet):
    def __init__(self, x, y, w, h, archivo_imagen, pantalla, anchura_Tile, altura_Tile):
        super().__init__(x, y, w, h, archivo_imagen, pantalla, anchura_Tile, altura_Tile)
        self.obstaculos = []
        self.imagen_mapa = self.dibujaSuelo()


    def get_obstaculos(self):
        return list(self.obstaculos)

    def getImagen(self):
        return self.imagen_mapa

    def getTileSuelo(self):
        fila = random.randint(8 ,9)
        columna = random.randint(0, 9)
        return self.ImagenesFuenteTile[fila][columna]
    

    def dibujaSuelo(self):
        Tile_w = self.anchura_Tile
        Tile_h = self.altura_Tile

        num_columnas_pantalla = (int)(self.pantalla.get_width() + Tile_w - 1) // Tile_w
        num_filas_pantalla = (int)(self.pantalla.get_height() + Tile_h - 1) // Tile_h
        
        lienzo = pygame.Surface((self.pantalla.get_width(), self.pantalla.get_height()), pygame.SRCALPHA).convert_alpha()

    #arena
        for j in range(num_filas_pantalla):
            for i in range(num_columnas_pantalla):
                lienzo.blit(self.getTileSuelo(), (i * Tile_w, j * Tile_h))


    #hierba y huesos
        for _ in range(20):

            i = random.randint(0, num_columnas_pantalla - 1)
            j = random.randint(0, num_filas_pantalla - 1)
            Tile_objeto_x = random.randint(0, 2)
            Tile_objeto_y = random.randint(13, 16)     
            lienzo.blit(self.ImagenesFuenteTile[Tile_objeto_y][Tile_objeto_x], (i * Tile_w, j * Tile_h))
        
        
    #pilares
        self.obstaculos.clear()
        for _ in range(10):
            i = random.randint(0, num_columnas_pantalla - 1)
            j = random.randint(0, max(0, num_filas_pantalla - 2))
            variante = random.randint(0, 2)

            lienzo.blit(self.ImagenesFuenteTile[11][variante], (i * Tile_w, j * Tile_h))
            lienzo.blit(self.ImagenesFuenteTile[12][variante], (i * Tile_w, (j + 1) * Tile_h))

            rect_columna = pygame.Rect(i * Tile_w, j * Tile_h, Tile_w, Tile_h * 2)
            self.obstaculos.append(rect_columna)


        return lienzo


class SpriteAnimado(Sprite):
    def __init__(self, x, y, w, h,  pantalla):
        super().__init__(x, y, w, h, pantalla)
        self.frame = 0 
        self.animacion_fila = 0
        self.max_frame = 4
        self.cont_frames = 0
        self.max_cont_frame = 20
        self.estado = 0
    
    def cargar_frames(self, imagen, ancho_frame, alto_frame, filas, columnas):
        matriz = []
        for fila in range(filas):
            fila_frames = []
            for col in range(columnas):
                
                frame = pygame.Surface((ancho_frame, alto_frame), pygame.SRCALPHA)
                frame.blit(self.imagen2, (0, 0),
                           (col * ancho_frame, fila * alto_frame, ancho_frame, alto_frame))
    
                frame = pygame.transform.scale(frame, (self.w, self.h))
                fila_frames.append(frame)
            matriz.append(fila_frames)
        return matriz


    def setMAxContFrames(self, vel):
        if vel == 0:
            self.max_cont_frame = 10
        else:
            self.max_cont_frame = max(1, min(25, int(40 / abs(vel))))
        '''else:
            self.max_cont_frame = int(40 / abs(vel))
            if self.max_cont_frame > 25:
                self.max_cont_frame = 25
            if self.max_cont_frame < 1:
                self.max_cont_frame = 1'''


class Enemigo(SpriteAnimado):
    def __init__(self, x, y, w, h, vel, x_min, x_max, pantalla, archivo_imagen_enemigo=None):
        super().__init__(x, y, w, h, pantalla)
        self.x_min = x_min
        self.x_max = x_max
        self.vel = vel
        self.vel_x = vel if vel != 0 else 2
        self.vel_y = 0
        self.y_inicial = y
        #self.frames = self.cargar_frames()

        
        if archivo_imagen_enemigo:
            try:
                ruta = archivo_imagen_enemigo
                if not os.path.isabs(ruta):
                    ruta = os.path.join(os.path.dirname(__file__), archivo_imagen_enemigo)
                self.imagen2 = pygame.image.load(ruta).convert_alpha()
            except pygame.error as e:
                print(f"No se pudo cargar la imagen del enemigo: {e}")

        self.frames = self.cargar_frames(self.imagen2, 16, 24, 3, 4)
    

    def getImagen(self):
    
        match self.estado:
            case 0 | 2:          # vigilando 
                self.animacion_fila = 1
            case 1 | 3:          # persiguiendo
                self.animacion_fila = 0
            case 4:              # otro estado 
                self.animacion_fila = 2
                
        self.setMAxContFrames(self.vel_x) 
        self.cont_frames += 1
        if self.cont_frames > self.max_cont_frame:
            self.cont_frames = 0
            self.frame = (self.frame + 1) % self.max_frame

        imagen = self.frames[self.animacion_fila][self.frame]
        if self.vel_x < 0:
            imagen = pygame.transform.flip(imagen, True, False)

        return imagen


    def muevete(self, personaje):
        match self.estado:
            case 0:
                self.vigilar(personaje)
            case 1:
                self.perseguirPersonaje(personaje)
            case 2:
                self.regresaApuntoDeVigilancia()


        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        self.update_rect()
        

    def regresaApuntoDeVigilancia(self):
        
        if self.rect.centery < self.y_inicial:
            self.vel_y = 1
        else:
            self.vel_y = -1

        if abs(self.rect.centery - self.y_inicial) <= abs(self.vel_y):
            self.pos_y = self.y_inicial
            self.vel_y = 0
            self.estado = 0
        
        
        '''if self.rect.top < self.y_inicial:
            self.vel_y = 1
		
        else:
            
            self.vel_y = -1
        
        if self.rect.top == self.y_inicial:
                self.vel_y = 0
                self.estado = 0'''


    def vigilar(self, personaje):
        if self.rect.left > self.x_max:
            self.vel_x = -abs(self.vel_x)
        if self.rect.left < self.x_min:
            self.vel_x = abs(self.vel_x)

        if self.buscarPersonaje(personaje):
            self.estado = 1
   
    def perseguirPersonaje(self, personaje):
        dx = personaje.rect.centerx - self.rect.centerx
        dy = personaje.rect.centery - self.rect.centery
        distancia = math.hypot(dx, dy)

        if distancia != 0:

            self.vel_x = (dx / distancia) * abs(self.vel)
            self.vel_y = (dy / distancia) * abs(self.vel)
        else:
            self.vel_x = self.vel_y = 0


        if not self.buscarPersonaje(personaje):
            self.estado = 2
     
    def buscarPersonaje(self, personaje):
        distancia = math.hypot(self.rect.centerx - personaje.rect.centerx, self.rect.centery - personaje.rect.centery)
        if distancia < 200:
            return True
        else:
            return False


class personaje(SpriteAnimado):
    def __init__(self, x, y, w, h, pantalla, archivo_imagen_personaje=None):
        super().__init__(x, y, w, h, pantalla)
        
        if archivo_imagen_personaje:
            try:

                if os.path.isabs(archivo_imagen_personaje):
                    ruta = archivo_imagen_personaje
                else:
                    ruta = os.path.join(os.path.dirname(__file__), archivo_imagen_personaje)
                self.imagen = pygame.image.load(ruta).convert_alpha()
            except pygame.error as e:
                print(f"No se pudo cargar la imagen del personaje: {e}")

        
        self.vel = 5
        self.vel_x = 0
        self.vel_y = 0
        self.status = "wait"
        self.indice_actual = 0
        self.ultimo_status = None
        
        self.anim =  {
            "wait":        (0,  8, False),
            "left":        (1,  8, False),
            "sword_right": (2,  8, False),
            "sword_left":  (3,  8, False),
            "sword_down":  (4,  8, False),
            "up":          (5,  6, False),
            "right":       (6,  4, False),
            "bow":         (7,  6, False),
            "hit":         (8,  4, False),
            "cast":        (9,  7, False),
            "died":        (11, 6, False),
            "run_left":    (13, 8, False),
            "run_right":   (13, 8, True),
            "down":        (0,  8, False),   
        }

        self.animacion = {}
        for nombre, (fila, frames, flip) in self.anim.items():
                self.animacion[nombre] = self.load_animacion(fila, frames, flip)
    
    def load_animacion(self, fila, num_frames, flip=False):
        frames_lista = []
            
        for col in range(num_frames):
            frame = pygame.Surface((32, 32), pygame.SRCALPHA)
            frame.blit(self.imagen, (0, 0), (col * 32, fila * 32, 32, 32))
            if flip:
                frame = pygame.transform.flip(frame, True, False)
            frame = pygame.transform.scale(frame, (self.w, self.h))
            frames_lista.append(frame)
        return frames_lista



            #imag = pygame.Surface((32,32), pygame.SRCALPHA).convert_alpha()
            #imag.blit(self.imagen, (0, 0), (i * 32, pos_y, 32, 32))

            #if flip:
                    #imag = pygame.transform.flip(imag, True, False)

            #imag = pygame.transform.scale(imag, (self.rect.width, self.rect.height))
        
            #self.animacion[nombre].append(imag)

    def getImagen(self):

        if self.status != self.ultimo_status:
            self.indice_actual = 0
            self.cont_frames = 0
            self.ultimo_status = self.status

        frames = self.animacion.get(self.status, self.animacion["wait"])
        if not frames:
            return self.imagen

        self.cont_frames += 1
        if self.cont_frames > 5:
            self.cont_frames = 0
            self.indice_actual = (self.indice_actual + 1) % len(frames)

        return frames[self.indice_actual]

    def muevete(self, obstaculos=None):
        keys   = pygame.key.get_pressed()
        self.vel_x = 0
        self.vel_y = 0
        moving = False

        # movimiento 
        if keys[pygame.K_a]:
            self.vel_x = -self.vel
            self.status = "left"
            moving = True
        elif keys[pygame.K_d]:
            self.vel_x = self.vel
            self.status = "right"
            moving = True

        if keys[pygame.K_w]:
            self.vel_y = -self.vel
            self.status = "up"
            moving = True
        elif keys[pygame.K_s]:
            self.vel_y = self.vel
            self.status = "down"
            moving = True

        #acciones especiales
        if keys[pygame.K_j]:
            if self.status in ("left",):
                self.status = "sword_left"
            elif self.status in ("right",):
                self.status = "sword_right"
            else:
                self.status = "sword_down"
            moving = True
        if keys[pygame.K_k]:
            self.status = "bow"
            moving = True
        if keys[pygame.K_l]:
            self.status = "died"
            moving = True
#velocidad
        dx = self.vel_x
        dy = self.vel_y
        if dx != 0 and dy != 0:
            dx = int(dx * 0.707)
            dy = int(dy * 0.707)

        if not moving:
            self.status = "wait"
        
        if not obstaculos:
            self.rect.x += dx
            self.rect.y += dy
            return True
#colisión eje x
        if dx != 0:
            self.rect.x += dx
            for obs in obstaculos:
                if self.rect.colliderect(obs):
                    if dx > 0:  
                        self.rect.right = obs.left
                    else:    
                        self.rect.left = obs.right

#colisión eje y       
        if dy != 0:
            self.rect.y += dy
            for obs in obstaculos:
                if self.rect.colliderect(obs):
                    if dy > 0:  
                        self.rect.bottom = obs.top
                    else:      
                        self.rect.top = obs.bottom


        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        return True


def colision(self, rect2):
    if self.rect.colliderect(rect2):
        print("Colisión Detectada")