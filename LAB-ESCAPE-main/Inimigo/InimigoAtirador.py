import pygame
import os
from .ProjetilInimigo import ProjetilInimigo


class InimigoAtirador:
    # --- Configurações do Inimigo ---
    SPRITE_WIDTH = 128
    SPRITE_HEIGHT = 128
    VELOCIDADE_ANIMACAO = 0.1
    ALCANCE_DISPARO = 500
    COOLDOWN_DISPARO = 2.0
    VELOCIDADE_MOVIMENTO = 0

    FRAMES_PARADO = 4
    FRAMES_ANDAR = 6
    FRAMES_ATAQUE = 4
    JANELA_DISPARO = 2

    VIDA_TOTAL = 100
    DANO_DO_PROJETIL = ProjetilInimigo.DANO

    def __init__(self, x, y, limite_esquerdo, limite_direito):
        self.limite_esquerdo = limite_esquerdo
        self.limite_direito = limite_direito

        self.vida_atual = self.VIDA_TOTAL
        self.morto = False

        self.estado = "parado"
        self.direcao = 1
        self.tempo_animacao = 0.0
        self.tempo_cooldown = 0.0

        self.projeteis = []
        self.atirou_no_ciclo = False

        # --- Carregamento das Spritesheets ---
        CAMINHO_BASE = os.path.join("Assets", "Images", "Inimigos", "InimigoAtirador")

        # Inicialização de Fallback
        placeholder_sprite = [pygame.Surface((self.SPRITE_WIDTH, self.SPRITE_HEIGHT))]
        self.animacao_parado = placeholder_sprite
        self.animacao_andar_esquerda = placeholder_sprite
        self.animacao_andar_direita = placeholder_sprite
        self.animacao_ataque_esquerda = placeholder_sprite
        self.animacao_ataque_direita = placeholder_sprite

        try:
            self.animacao_parado = self._carregar_spritesheet(os.path.join(CAMINHO_BASE, "Parado.png"),
                                                              self.FRAMES_PARADO, y_offset=0)
            self.animacao_andar_esquerda = self._carregar_spritesheet(os.path.join(CAMINHO_BASE, "Esquerda.png"),
                                                                      self.FRAMES_ANDAR, y_offset=0)
            self.animacao_andar_direita = self._carregar_spritesheet(os.path.join(CAMINHO_BASE, "Direita.png"),
                                                                     self.FRAMES_ANDAR, y_offset=0)
            self.animacao_ataque_esquerda = self._carregar_spritesheet(os.path.join(CAMINHO_BASE, "Esquerdatiro.png"),
                                                                       self.FRAMES_ATAQUE, y_offset=0)
            self.animacao_ataque_direita = self._carregar_spritesheet(os.path.join(CAMINHO_BASE, "Direitatiro.png"),
                                                                      self.FRAMES_ATAQUE, y_offset=0)

        except Exception as e:
            print(f"ERRO DE CARREGAMENTO CRÍTICO DE SPRITES ATIRADOR: Falha ao carregar sheets. Erro: {e}")

        self.sprites_atuais = self.animacao_parado
        self.frame_atual = 0
        self.image = self.sprites_atuais[self.frame_atual]
        self.rect = self.image.get_rect(x=x, y=y)

        self.estado_anterior = self.estado

    def _carregar_spritesheet(self, caminho_sheet, num_frames, y_offset):
        """Carrega uma spritesheet (imagem única) e a divide em frames."""
        spritesheet = pygame.image.load(caminho_sheet).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame_surface = pygame.Surface((self.SPRITE_WIDTH, self.SPRITE_HEIGHT), pygame.SRCALPHA)
            area_crop = (i * self.SPRITE_WIDTH, y_offset, self.SPRITE_WIDTH, self.SPRITE_HEIGHT)
            frame_surface.blit(spritesheet, (0, 0), area_crop)
            frames.append(frame_surface)
        return frames

    def tomar_dano(self, dano):
        """Aplica dano ao inimigo e retorna True se ele morreu."""
        if not self.morto:
            self.vida_atual -= dano
            if self.vida_atual <= 0:
                self.vida_atual = 0
                self.morto = True
                return True
        return False

    def update(self, dt, volt_rect, volt_invencivel):
        if self.morto:
            self._update_projeteis(dt)
            return self.projeteis

        self.tempo_animacao += dt
        self.tempo_cooldown += dt

        distancia_x = self.rect.centerx - volt_rect.centerx

        # 1. Lógica de Estado
        self.estado_anterior = self.estado

        # TENTA MUDAR PARA ATAQUE APENAS SE O COOLDOWN TERMINOU
        if abs(distancia_x) <= self.ALCANCE_DISPARO and self.tempo_cooldown >= self.COOLDOWN_DISPARO:
            self.direcao = -1 if distancia_x > 0 else 1
            self.estado = "atacando"
            self.atirou_no_ciclo = False
            self.tempo_cooldown = 0.0  # ZERA O COOLDOWN NO INÍCIO DO ATAQUE
        else:
            if self.estado != "atacando":
                self.estado = "parado"

        # 2. Lógica de Ação e Animação

        if self.estado == "atacando":

            if self.direcao == 1:
                self.sprites_atuais = self.animacao_ataque_direita
            else:
                self.sprites_atuais = self.animacao_ataque_esquerda

            # CRIAÇÃO DO PROJÉTIL (Uma única vez na janela de disparo)
            if self.frame_atual == self.JANELA_DISPARO and not self.atirou_no_ciclo:
                x_disparo = self.rect.centerx + (self.SPRITE_WIDTH // 4 * self.direcao)
                y_disparo = self.rect.centery

                novo_projetil = ProjetilInimigo(x_disparo, y_disparo, self.direcao)
                self.projeteis.append(novo_projetil)

                self.atirou_no_ciclo = True

            # SAÍDA DO ESTADO DE ATAQUE: Quando a animação terminar
            if self.frame_atual == len(self.sprites_atuais) - 1 and self.tempo_animacao >= self.VELOCIDADE_ANIMACAO:
                self.estado = "parado"

        elif self.estado == "parado":
            self.sprites_atuais = self.animacao_parado

        # 3. Troca de Frame Comum
        if self.estado != self.estado_anterior:
            self.frame_atual = 0

        if self.tempo_animacao >= self.VELOCIDADE_ANIMACAO:
            self.frame_atual = (self.frame_atual + 1) % len(self.sprites_atuais)
            self.tempo_animacao = 0.0

        self.image = self.sprites_atuais[self.frame_atual]

        # 4. Atualiza Posição dos Projéteis (e remove inativos)
        self._update_projeteis(dt)

        return self.projeteis

    def _update_projeteis(self, dt):
        """Atualiza a posição dos projéteis e remove os inativos."""
        projeteis_ativos = []
        for p in self.projeteis:
            p.update(dt)
            if p.ativo:
                projeteis_ativos.append(p)
        self.projeteis = projeteis_ativos

    def draw(self, screen, offset_x, offset_y):
        if self.morto: return
        screen_x = self.rect.x - offset_x
        screen_y = self.rect.y - offset_y

        screen.blit(self.image, (screen_x, screen_y))

        # Desenha os projéteis
        for p in self.projeteis:
            p.draw(screen, offset_x, offset_y)