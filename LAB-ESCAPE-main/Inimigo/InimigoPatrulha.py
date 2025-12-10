# Inimigo/InimigoPatrulha.py

import pygame


class InimigoPatrulha(pygame.sprite.Sprite):
    def __init__(self, x, y, limite_esquerdo, limite_direito, velocidade=100):
        super().__init__()

        # 1. Aparência e Posição
        # Exemplo: um bloco vermelho simples (você substituirá isso por uma imagem depois)
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))  # Vermelho
        self.rect = self.image.get_rect(topleft=(x, y))

        # 2. Movimento
        self.velocidade_base = velocidade
        self.velocidade_x = velocidade  # Começa movendo-se para a direita

        # 3. Limites de Patrulha
        self.limite_esquerdo = limite_esquerdo
        self.limite_direito = limite_direito

        # 4. Estado (Vida, etc.)
        self.vida = 1

    def update(self, dt):
        """
        Atualiza a posição do inimigo e verifica os limites de patrulha.
        dt é o tempo decorrido em segundos.
        """

        # Move o inimigo
        self.rect.x += self.velocidade_x * dt

        # Lógica de Patrulha: Verifica se atingiu os limites
        if self.velocidade_x > 0:  # Movendo para a direita
            if self.rect.right >= self.limite_direito:
                self.velocidade_x *= -1  # Inverte a direção (agora negativo, vai para a esquerda)
                # Opcional: ajusta a posição para não ficar "preso" no limite
                self.rect.right = self.limite_direito

        elif self.velocidade_x < 0:  # Movendo para a esquerda
            if self.rect.left <= self.limite_esquerdo:
                self.velocidade_x *= -1  # Inverte a direção (agora positivo, vai para a direita)
                # Opcional: ajusta a posição para não ficar "preso" no limite
                self.rect.left = self.limite_esquerdo

    def draw(self, surface, offset_x, offset_y):
        """
        Desenha o inimigo na tela, ajustado pelo offset da câmera.
        """
        screen_x = self.rect.x - offset_x
        screen_y = self.rect.y - offset_y
        surface.blit(self.image, (screen_x, screen_y))