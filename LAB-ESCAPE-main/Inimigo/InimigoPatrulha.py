import pygame
import os
from PPlay.sprite import Sprite
from PPlay.collision import Collision


class InimigoPatrulha:
    # DEFINIÇÕES DE COMBATE E SPRITES
    SPRITE_WIDTH = 128
    SPRITE_HEIGHT = 128
    VELOCIDADE_ANIMACAO = 0.1
    ALCANCE_ATAQUE = 100
    JANELA_DANO_INICIO = 3
    JANELA_DANO_FIM = 4
    FRAMES_ATAQUE = 6
    DANO_Soco = 20

    # 🟢 NOVO: Dano que o soco do Volt causa (assumindo que o soco do Volt causa 50 de dano)
    DANO_SOCO_VOLT = 50

    # 🟢 VIDA DO INIMIGO (Para morrer com 2 socos, vida deve ser 100)
    VIDA_TOTAL = 100

    def __init__(self, x, y, limite_esquerdo, limite_direito, velocidade):

        # 1. Configuração do Inimigo e Limites
        self.limite_esquerdo = limite_esquerdo
        self.limite_direito = limite_direito
        self.velocidade_movimento = velocidade

        # 🟢 VIDA
        self.vida_total = self.VIDA_TOTAL
        self.vida_atual = self.VIDA_TOTAL
        self.morto = False  # Flag de estado
        # ... (Restante do seu código original) ...

        # Estado inicial
        self.direcao = 1
        self.estado = "patrulha"
        self.tempo_animacao = 0.0
        self.atacando = False

        # 2. Carregamento das Spritesheets
        CAMINHO_BASE = os.path.join("Assets", "Images", "Inimigos", "InimigoPatrulha")

        try:
            # Animações de MOVIMENTO (4 e 6 frames)
            self.animacao_parado = self._carregar_spritesheet(os.path.join(CAMINHO_BASE, "Parado.png"), num_frames=4)
            self.animacao_andar_direita = self._carregar_spritesheet(os.path.join(CAMINHO_BASE, "Direita.png"),
                                                                     num_frames=6)
            self.animacao_andar_esquerda = self._carregar_spritesheet(os.path.join(CAMINHO_BASE, "Esquerda.png"),
                                                                      num_frames=6)

            # ANIMAÇÕES DE ATAQUE (6 frames)
            self.animacao_soco_direita = self._carregar_spritesheet(os.path.join(CAMINHO_BASE, "Direitasoco.png"),
                                                                    num_frames=self.FRAMES_ATAQUE)
            self.animacao_soco_esquerda = self._carregar_spritesheet(os.path.join(CAMINHO_BASE, "Esquerdasoco.png"),
                                                                     num_frames=self.FRAMES_ATAQUE)

        except Exception as e:
            print(f"ERRO DE CARREGAMENTO DE SPRITES INIMIGO: {e}")
            self.animacao_parado = [pygame.Surface((self.SPRITE_WIDTH, self.SPRITE_HEIGHT))]
            self.animacao_andar_direita = self.animacao_parado
            self.animacao_andar_esquerda = self.animacao_parado
            self.animacao_soco_direita = self.animacao_parado
            self.animacao_soco_esquerda = self.animacao_parado

        # 3. Inicialização do Sprite
        self.sprites_atuais = self.animacao_parado
        self.frame_atual = 0
        self.image = self.sprites_atuais[self.frame_atual]

        self.rect = self.image.get_rect(x=x, y=y)

    def _carregar_spritesheet(self, caminho_sheet, num_frames):
        spritesheet = pygame.image.load(caminho_sheet).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame_surface = pygame.Surface((self.SPRITE_WIDTH, self.SPRITE_HEIGHT), pygame.SRCALPHA)
            area_crop = (i * self.SPRITE_WIDTH, 0, self.SPRITE_WIDTH, self.SPRITE_HEIGHT)
            frame_surface.blit(spritesheet, (0, 0), area_crop)
            frames.append(frame_surface)
        return frames

    # 🟢 NOVO: Método para tomar dano
    def tomar_dano(self, dano):
        if not self.morto:
            self.vida_atual -= dano
            if self.vida_atual <= 0:
                self.vida_atual = 0
                self.morto = True
                return True  # Inimigo morreu
        return False  # Inimigo ainda está vivo

    def gerar_hitbox_soco(self):
        # A hitbox é um retângulo que se projeta do inimigo durante o ataque.
        if self.estado != "atacando" or self.frame_atual < self.JANELA_DANO_INICIO or self.frame_atual > self.JANELA_DANO_FIM:
            return None

        hitbox_width = 40
        hitbox_height = 80
        hitbox_y = self.rect.y + 30

        if self.direcao == 1:
            hitbox_x = self.rect.right - 20
        else:
            hitbox_x = self.rect.left - hitbox_width + 20

        return pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

    def update(self, dt, volt_rect, volt_invencivel):

        if self.morto:
            return None  # Não atualiza se estiver morto

        self.tempo_animacao += dt

        distancia_x = abs(self.rect.centerx - volt_rect.centerx)

        # 1. MUDANÇA DE ESTADO: PATRULHA -> ATAQUE
        if self.estado == "patrulha" and distancia_x <= self.ALCANCE_ATAQUE and not self.atacando:
            self.estado = "atacando"
            self.atacando = True
            self.frame_atual = 0
            self.tempo_animacao = 0.0

            if volt_rect.centerx > self.rect.centerx:
                self.direcao = 1
            else:
                self.direcao = -1

        # 2. LÓGICA DE PATRULHA (Só se não estiver atacando)
        if self.estado == "patrulha":
            movimento_x = self.velocidade_movimento * self.direcao * dt
            self.rect.x += movimento_x

            # Verifica limites e inverte direção
            if self.rect.x < self.limite_esquerdo:
                self.rect.x = self.limite_esquerdo
                self.direcao = 1
            elif self.rect.x + self.rect.width > self.limite_direito:
                self.rect.x = self.limite_direito - self.rect.width
                self.direcao = -1

        # 3. ATUALIZA ANIMAÇÃO E ESTADO DO ATAQUE
        if self.estado == "atacando":

            if self.direcao == 1:
                self.sprites_atuais = self.animacao_soco_direita
            else:
                self.sprites_atuais = self.animacao_soco_esquerda

            # Se a animação terminou, volta à patrulha
            if self.frame_atual >= self.FRAMES_ATAQUE - 1 and self.tempo_animacao >= self.VELOCIDADE_ANIMACAO:
                self.estado = "patrulha"
                self.atacando = False
                self.frame_atual = 0
                self.tempo_animacao = 0.0

            # LÓGICA DE DANO: Colisão com o jogador
            hitbox = self.gerar_hitbox_soco()
            if hitbox and volt_rect.colliderect(hitbox) and not volt_invencivel:
                # Retorna o dano para ser processado no main.py
                return {"tipo": "dano", "dano": self.DANO_Soco, "direcao": self.direcao}

        elif self.estado == "patrulha":
            # Animação de andar/parado
            if self.direcao == 1:
                self.sprites_atuais = self.animacao_andar_direita
            else:
                self.sprites_atuais = self.animacao_andar_esquerda

        # 4. Troca de Frame Comum
        if self.tempo_animacao >= self.VELOCIDADE_ANIMACAO:
            self.frame_atual = (self.frame_atual + 1) % len(self.sprites_atuais)
            self.tempo_animacao = 0.0

        self.image = self.sprites_atuais[self.frame_atual]
        return None  # Retorna None se não houver dano ou se estiver morto

    def draw(self, screen, offset_x, offset_y):
        if self.morto: return
        screen_x = self.rect.x - offset_x
        screen_y = self.rect.y - offset_y

        # Desenha a imagem
        screen.blit(self.image, (screen_x, screen_y))

        # DEBUG: Desenha a hitbox ativa
        hitbox = self.gerar_hitbox_soco()
        if hitbox:
            hitbox_screen = hitbox.move(-offset_x, -offset_y)
            pygame.draw.rect(screen, (255, 0, 0), hitbox_screen, 2)