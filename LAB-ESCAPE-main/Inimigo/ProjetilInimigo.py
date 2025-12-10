import pygame
import os


class ProjetilInimigo:
    DANO = 25

    def __init__(self, x, y, direcao):

        # --- Configurações Gráficas ---
        CAMINHO_SPRITE = os.path.join("Assets", "Images", "Inimigos", "InimigoAtirador", "tiro.png")

        try:
            self.image = pygame.image.load(CAMINHO_SPRITE).convert_alpha()
        except pygame.error as e:
            # Placeholder vermelho para debug de falha de carregamento
            print(f"ERRO CRÍTICO NO PROJÉTIL (TIRO): Falha ao carregar '{CAMINHO_SPRITE}'. Erro: {e}")
            self.image = pygame.Surface((24, 24))
            self.image.fill((255, 0, 0))

        self.width = 24
        self.height = 24
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        # --- Configurações Físicas ---
        self.velocidade = 500
        self.direcao = direcao
        self.rect = self.image.get_rect(centerx=x, centery=y)
        self.ativo = True

    def update(self, dt):
        if not self.ativo:
            return

        self.rect.x += self.velocidade * self.direcao * dt

        if self.rect.right < 0 or self.rect.left > 1080:
            self.ativo = False

    def draw(self, screen, offset_x, offset_y):
        if self.ativo:
            screen_x = self.rect.x - offset_x
            screen_y = self.rect.y - offset_y

            # 🟢 LÓGICA DE FLIP/ROTAÇÃO: Vira horizontalmente (True) se a direção for -1 (esquerda)
            imagem_a_desenhar = self.image
            if self.direcao == -1:
                imagem_a_desenhar = pygame.transform.flip(self.image, True, False)

            screen.blit(imagem_a_desenhar, (screen_x, screen_y))