#from re import A, S
import pygame
import math
import os

class Sprite():
    def __init__(self,x, y, w, h, pantalla):
        self.w = int(w * 1)
        self.h = int(h * 1)
        self.rect = pygame.Rect(x, y, self.w, self.h)
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.pantalla = pantalla
        self.estado = 0
        
        ruta_base = os.path.dirname(__file__)
        ruta_imagen = os.path.join(ruta_base, 'monitoB.png')
        ruta_imagen2 = os.path.join(ruta_base, 'Bat_Sprites.png')

        try:
            self.imagen = pygame.image.load(ruta_imagen).convert_alpha()
            self.imagen2 = pygame.image.load(ruta_imagen2).convert_alpha()
        except pygame.error as e:
            print(f"No se pudo cargar la imagen: {e}")

            self.imagen = pygame.Surface((32,32))
            self.imagen2 = pygame.Surface((16,24))
        

    def dibujate(self):
        #pygame.draw.rect(self.pantalla, (r, g, b), self.rect, 1)
        self.pantalla.blit(self.getImagen(),self.rect)

    def getImagen(self):
        return self.imagen
    
    def detectacolision(self, other):
        
        colision = True
        if self.rect.left + self.rect.width < other.rect.left:
            colision = False
        elif self.rect.left > other.rect.left + other.rect.width:
            colision = True
        elif self.rect.top + self.rect.height < other.rect.top:
            colision = False
        elif self.rect.top > other.rect.top + other.rect.height:
            colision = False
        return colision


class SpriteAnimado(Sprite):
    def __init__(self, x, y, w, h,  pantalla):
        super().__init__(x, y, w, h, pantalla)
        self.frame = 0 
        self.animacion_fila = 0
        self.max_frame = 4
        self.cont_frames = 0
        self.max_cont_frame = 10

    #agregar matriz de sprites para los cuadros de animación

    def setMAxContFrames(self, vel):
        if vel == 0:
            self.max_cont_frame = 10

        else:
            self.max_cont_frame = 40 / abs(vel)
            if self.max_cont_frame > 25:
                self.max_cont_frame = 25


class Enemigo(SpriteAnimado):
    def __init__(self, x, y, w, h, vel, x_min, x_max, pantalla):
        super().__init__(x, y, w, h, pantalla,)
        self.x_min = x_min
        self.x_max = x_max
        self.vel_x = vel if vel != 0 else 2
        self.vel = vel
        self.vel_y = 0
        self.y_inicial = y


    def getImagen(self):
    
         match self.estado:
            case 0:
                self.animacion_fila = 1
            case 1:
                self.animacion_fila = 0
            case 2:
                self.animacion_fila = 1
            case 3:
                self.animacion_fila = 0
            case 4:
                self.animacion_fila = 2
                
         self.setMAxContFrames(self.vel_x) 

         self.cont_frames += 1
         if self.cont_frames > self.max_cont_frame:
            self.cont_frames = 0
            self.frame +=1
            if self.frame > self.max_frame:
                    self.frame = 0

         imagen_a_regresar = pygame.Surface((16, 24), pygame.SRCALPHA).convert_alpha()
         imagen_a_regresar.blit(self.imagen2, (0,0), (self.frame * 16, self.animacion_fila * 24, 16, 24))
        
         imagen_a_regresar = pygame.transform.scale(imagen_a_regresar, (self.rect.width, self.rect.height))
        
         if self.vel_x < 0: 
            imagen_a_regresar = pygame.transform.flip(imagen_a_regresar, True, False)

         return imagen_a_regresar

    def muevete(self, personaje):
        match self.estado:
            case 0:
                self.vigilar(personaje)
                print('vigilando')
            case 1:
                self.perseguirPersonaje(personaje)
                print('persiguiendo')
            case 2:
                self.regresaApuntoDeVigilancia()
                print('regresando')

        self.rect.left = self.rect.left + self.vel_x
        self.rect.top = self.rect.top + self.vel_y

    def regresaApuntoDeVigilancia(self):
        if self.rect.top < self.y_inicial:
            self.vel_y = 1
		
        else:
            
            self.vel_y = -1
        
        if self.rect.top == self.y_inicial:
                self.vel_y = 0
                self.estado = 0

    def vigilar(self, personaje):
        if self.rect.left > self.x_max:
            self.vel_x *= -1
        if self.rect.left < self.x_min:
            self.vel_x *= -1

        if self.buscarPersonaje(personaje) == True:
            self.estado = 1
   
    def perseguirPersonaje(self, personaje):
        if self.rect.centerx < personaje.rect.centerx:
            self.vel_x = 1
        else:
            self.vel_x = -1

        if self.rect.centery < personaje.rect.centery:
            self.vel_y = 1
        else:
            self.vel_y = -1
        
        if self.buscarPersonaje(personaje) == False:
            self.estado = 2
     

    def buscarPersonaje(self, personaje):
        distancia = math.pow(math.pow(self.rect.centerx - personaje.rect.centerx,2) + math.pow(self.rect.centery - personaje.rect.centery, 2), 0.5)
        if distancia < 200:
            #self.estado = 1
            print("visto")
            return True
        else:
            print("")
            return False

class personaje(SpriteAnimado):
    def __init__(self, x, y, w, h, pantalla):
        super().__init__(x, y, w, h, pantalla)
        self.vel = 5
        #self.vel_x = 0
        #self.vel_y = 0
        self.status = "wait"
        self.indice_actual = 0
        
        self.animacion = {
            "wait": [], 
            "right": [], 
            "left": [], 
            "up": [], 
            "down": [], 
            "sword": [],
            "bow": [],
            "died": []
        }

        #posición en Sprit
        self.load_animacion("wait", 0, 4, False)
        self.load_animacion("right",64, 6, False)
        self.load_animacion("left", 64, 6, True)
        self.load_animacion("up", 128, 6, False)
        self.load_animacion("down", 192, 6, True)
        self.load_animacion("sword", 256, 6, False)
        self.load_animacion("bow", 640, 8, False)
        self.load_animacion("died", 896, 7, False)

    def load_animacion(self, nombre, pos_y, frames, flip):
        #self.animacion[nombre] = []

        for i in range (frames):

            imag = pygame.Surface((32,32), pygame.SRCALPHA).convert_alpha()
            imag.blit(self.imagen, (0, 0), (i * 32, pos_y, 32, 32))

            if flip:
                    imag = pygame.transform.flip(imag, True, False)

            imag = pygame.transform.scale(imag, (self.rect.width, self.rect.height))
        
            self.animacion[nombre].append(imag)

    def getImagen(self):
        frames = self.animacion.get(self.status, [])
        if not frames: 
            return self.imagen

        self.cont_frames += 1
    
        if self.cont_frames > 5:
            self.cont_frames = 0
            self.indice_actual = (self.indice_actual + 1) % len (frames)

        return frames[self.indice_actual]

    def muevete(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        self.vel_y = 0
        moving = False
    
        if keys[pygame.K_a]:
            self.rect.x -= self.vel
            self.status = "left"
            moving = True
        elif keys[pygame.K_d]:
            self.rect.x += self.vel
            self.status = "right"
            moving = True
        
        if keys[pygame.K_w]:
            self.rect.y -= self.vel
            self.status = "up"
            moving = True
        elif keys[pygame.K_s]:
            self.rect.y += self.vel
            self.status = "down"
            moving = True

        if keys[pygame.K_j]:
            self.status = "sword"
            moving = True

        if not moving:
            self.status = "wait"
    
    
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
    
        return True

def colision(self, rect2):
    if self.rect.colliderect(rect2):
        print("Colisión Detectada")