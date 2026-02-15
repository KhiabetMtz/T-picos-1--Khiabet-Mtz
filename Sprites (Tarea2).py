import pygame

class Sprite(): 
    def __init__(self, x, y, w, h, pantalla, color=(255, 0, 0)):
        self.rect = pygame.Rect(x, y, w, h)
        self.pantalla = pantalla
        self.color = color
        
    def detecta_colision(self, otro_sprite):
        return self.rect.colliderect(otro_sprite.rect)  

    def dibujate(self):
        pygame.draw.rect(self.pantalla, self.color, self.rect)

class Enemigo(Sprite):
    def __init__(self, x, y, w, h, x_min, x_max, pantalla):
        super().__init__(x, y, w, h, pantalla, (0, 0, 255))
        self.x_min = x_min
        self.x_max = x_max
        self.direccion_x = 2

    def muevete(self):
        self.rect.x += self.direccion_x
        if self.rect.right > self.x_max or self.rect.left < self.x_min:
            self.direccion_x *= -1

class Personaje(Sprite):
    def __init__(self, x, y, w, h, pantalla):
        super().__init__(x, y, w, h, pantalla, (0, 255, 0))
        self.paso = 20 

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_a: self.rect.x -= self.paso
            if evento.key == pygame.K_d: self.rect.x += self.paso
            if evento.key == pygame.K_w: self.rect.y -= self.paso
            if evento.key == pygame.K_s: self.rect.y += self.paso