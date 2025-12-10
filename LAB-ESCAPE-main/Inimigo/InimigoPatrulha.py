import pygame
import os
from PPlay.sprite import Sprite
from PPlay.collision import Collision


class InimigoPatrulha:
    # 🟢 DEFINIÇÕES FINAIS DA SPRITESHEET
    SPRITE_WIDTH = 128
    SPRITE_HEIGHT = 128
    VELOCIDADE_ANIMACAO = 0.1  # Tempo em segundos para mudar de frame (10 frames/segundo)

    def __init__(self, x, y, limite_esquerdo, limite_direito, velocidade):

        # 1. Configuração do Inimigo e Limites
        self.limite_esquerdo = limite_esquerdo
        self.limite_direito = limite_direito
        self.velocidade_movimento = velocidade

        # Estado inicial
        self.direcao = 1  # 1: Direita, -1: Esquerda
        self.estado = "andar_direita"
        self.tempo_animacao = 0.0

        # 2. Carregamento das Spritesheets
        # NOTA: O caminho é Assets/Images/Inimigos/InimigoPatrulha/[Nome do Arquivo]
        CAMINHO_BASE = os.path.join("Assets", "Images", "Inimigos", "InimigoPatrulha")

        try:
            # PARADO (512x128 -> 4 frames)
            self.animacao_parado = self._carregar_spritesheet(
                os.path.join(CAMINHO_BASE, "Parado.png"),
                num_frames=4
            )

            # ANDAR DIREITA (768x128 -> 6 frames)
            self.animacao_andar_direita = self._carregar_spritesheet(
                os.path.join(CAMINHO_BASE, "Direita.png"),
                num_frames=6
            )

            # ANDAR ESQUERDA (768x128 -> 6 frames)
            self.animacao_andar_esquerda = self._carregar_spritesheet(
                os.path.join(CAMINHO_BASE, "Esquerda.png"),
                num_frames=6
            )

        except Exception as e:
            print(
                f"ERRO DE CARREGAMENTO DE SPRITES INIMIGO. Verifique se os arquivos (Parado.png, Direita.png, Esquerda.png) estão na pasta {CAMINHO_BASE}. Erro: {e}")
            # Cria um sprite placeholder em caso de falha para evitar crash
            self.animacao_parado = [pygame.Surface((self.SPRITE_WIDTH, self.SPRITE_HEIGHT))]
            self.animacao_andar_direita = self.animacao_parado
            self.animacao_andar_esquerda = self.animacao_parado

        # 3. Inicialização do Sprite
        self.sprites_atuais = self.animacao_parado
        self.frame_atual = 0
        self.image = self.sprites_atuais[self.frame_atual]

        # Cria o retângulo de colisão (Pygame Rect)
        self.rect = self.image.get_rect(x=x, y=y)

        # Ajuste o Y inicial para posicionar corretamente, considerando a altura da tela
        # self.rect.y -= (self.SPRITE_HEIGHT - 64) # Exemplo de ajuste se o y inicial era a base

    def _carregar_spritesheet(self, caminho_sheet, num_frames):
        """
        Carrega uma folha de sprites (sheets separadas) e a divide.
        Assume que todos os frames estão na mesma linha (y=0).
        """
        spritesheet = pygame.image.load(caminho_sheet).convert_alpha()
        frames = []

        for i in range(num_frames):
            frame_surface = pygame.Surface((self.SPRITE_WIDTH, self.SPRITE_HEIGHT), pygame.SRCALPHA)

            # Define a área a ser copiada da folha: (x, y, largura, altura)
            area_crop = (i * self.SPRITE_WIDTH, 0, self.SPRITE_WIDTH, self.SPRITE_HEIGHT)

            frame_surface.blit(spritesheet, (0, 0), area_crop)
            frames.append(frame_surface)

        return frames

    def update(self, dt):

        # 1. Movimento e Patrulha
        movimento_x = self.velocidade_movimento * self.direcao * dt
        self.rect.x += movimento_x

        # Verifica limites e inverte direção
        if self.rect.x < self.limite_esquerdo:
            self.rect.x = self.limite_esquerdo
            self.direcao = 1
            self.estado = "andar_direita"
        elif self.rect.x + self.rect.width > self.limite_direito:
            self.rect.x = self.limite_direito - self.rect.width
            self.direcao = -1
            self.estado = "andar_esquerda"

        # 2. Atualiza Animação
        self.tempo_animacao += dt

        # Define qual lista de sprites usar
        if self.direcao == 1:
            self.sprites_atuais = self.animacao_andar_direita
        elif self.direcao == -1:
            self.sprites_atuais = self.animacao_andar_esquerda
        else:
            self.sprites_atuais = self.animacao_parado

        # Troca o frame se o tempo passou
        if self.tempo_animacao >= self.VELOCIDADE_ANIMACAO:
            self.frame_atual = (self.frame_atual + 1) % len(self.sprites_atuais)
            self.tempo_animacao = 0.0

        # Atualiza a imagem exibida
        self.image = self.sprites_atuais[self.frame_atual]

    def draw(self, screen, offset_x, offset_y):
        # Desenha a imagem na tela, ajustada pelo offset da câmera
        screen_x = self.rect.x - offset_x
        screen_y = self.rect.y - offset_y

        # Desenha a imagem (o Surface do Pygame)
        screen.blit(self.image, (screen_x, screen_y))