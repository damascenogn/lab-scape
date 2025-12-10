from PPlay.animation import*
from PPlay.sprite import*
from PPlay.window import*
from PPlay.keyboard import*


class Raio:
    def __init__(self, x, y, direcao, sprite):
        if direcao == 1:
            imagem = "Poderes/Raio/raio_direita.png"
        else:
            imagem = "Poderes/Raio/raio_esquerda.png"
        self.sprite = Sprite(imagem, 13)
        self.sprite.set_total_duration(900)
        # posição inicial
        self.sprite.x = x
        self.sprite.y = y

        self.direcao = direcao #1 direita -1 esquerda
        self.velocidade = 600
    def update(self, dt):
        self.sprite.move_x(self.velocidade*self.direcao*dt)
        self.sprite.update()