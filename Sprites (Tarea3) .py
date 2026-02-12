import pygame

class Sprite():
    def __init__(self,x, y, w, h, pantalla):
        self.rect = pygame.Rect(x, y, w, h)
        self.pantalla = pantalla
    
    def dibujate(self, R, G, B):
        pygame.draw.rect(self.pantalla, (R, G, B), self.rect)

    def detectacolision(self, other):
        return self.rect.colliderect(other.rect)
  

class Enemigo(Sprite):
    def __init__(self, x, y, w, h, vel_x, x_min, x_max, pantalla):
        super().__init__(x, y, w, h, pantalla)
        self.x_min = x_min
        self.x_max = x_max
        self.vel_x = vel_x
    
    def muevete(self):
        if self.rect.left > self.x_max or self.rect.left < self.x_min:
            self.vel_x *= -1
        self.rect.left += self.vel_x
       

class personaje(Sprite):
    def __init__(self, x, y, w, h, pantalla):
        super().__init__(x, y, w, h, pantalla)
        self.vel = 5 


    def muevete(self):  
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.left -= self.vel
        if keys[pygame.K_RIGHT]:
            self.rect.left += self.vel
        if keys[pygame.K_UP]:
            self.rect.top -= self.vel
        if keys[pygame.K_DOWN]:
            self.rect.top += self.vel


def colision(self, rect2) -> None:
    if self.detectacolision(rect2):
        print("colision")