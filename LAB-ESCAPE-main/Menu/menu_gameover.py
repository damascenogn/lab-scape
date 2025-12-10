import pygame
from PPlay.window import Window


class MenuGameOver:
    COR_TITULO = (255, 0, 0)
    COR_PADRAO = (200, 200, 200)
    COR_HIGHLIGHT = (255, 255, 0)

    def __init__(self, window: Window, sons_menu=None):
        self.window = window
        self.teclado = window.get_keyboard()
        self.mouse = pygame.mouse
        self.running = True
        self.proxima_cena = "gameover"
        self.sons = sons_menu
        self.selecao_anterior = 0

        # 🟢 Opções: MENU PRINCIPAL e SAIR
        self.opcoes = ["MENU PRINCIPAL", "SAIR"]
        self.selecao_atual = 0
        self.retangulos_opcoes = []

        pygame.font.init()
        self.fonte_titulo = pygame.font.Font(None, 120)
        self.fonte_opcoes = pygame.font.Font(None, 60)

        self.tempo_ultimo_movimento = pygame.time.get_ticks()
        self.cooldown_movimento = 200

    def handle_events(self):
        agora = pygame.time.get_ticks()
        self.selecao_anterior = self.selecao_atual

        # 1. Navegação (Teclado)
        if agora - self.tempo_ultimo_movimento > self.cooldown_movimento:
            if self.teclado.key_pressed("UP"):
                self.selecao_atual = (self.selecao_atual - 1) % len(self.opcoes)
                self.tempo_ultimo_movimento = agora
                if self.sons: self.sons.tocar_selecao()
            elif self.teclado.key_pressed("DOWN"):
                self.selecao_atual = (self.selecao_atual + 1) % len(self.opcoes)
                self.tempo_ultimo_movimento = agora
                if self.sons: self.sons.tocar_selecao()

                # Retorno/Aceite (ENTER)
            if self.teclado.key_pressed("ENTER"):
                if self.sons: self.sons.tocar_selecao_ok()
                return self._finalizar_gameover()

        # 2. Controle por Mouse
        if self.mouse.get_pressed()[0]:
            mouse_pos = self.mouse.get_pos()
            for i, rect in enumerate(self.retangulos_opcoes):
                if rect.collidepoint(mouse_pos):
                    self.selecao_atual = i
                    if self.sons: self.sons.tocar_selecao_ok()
                    return self._finalizar_gameover()

        return "gameover"

    def _finalizar_gameover(self):
        """Define o próximo estado baseado na opção selecionada."""
        if self.selecao_atual == 0:
            return "menu"  # Volta para o Menu Principal
        elif self.selecao_atual == 1:
            return "sair"  # Sai do jogo

    def draw(self):
        # 1. Desenha Overlay Preto (Geralmente o Game Over não mostra o jogo por baixo)
        self.window.screen.fill((0, 0, 0))

        W = self.window.width
        H = self.window.height

        # 2. Título GAME OVER
        titulo_surface = self.fonte_titulo.render("GAME OVER", True, self.COR_TITULO)
        titulo_rect = titulo_surface.get_rect(center=(W // 2, H // 4))
        self.window.screen.blit(titulo_surface, titulo_rect)

        # 3. Opções
        self.retangulos_opcoes = []
        y_pos = H // 2
        mouse_pos = self.mouse.get_pos()

        for i, opcao in enumerate(self.opcoes):
            cor = self.COR_PADRAO

            texto_surface = self.fonte_opcoes.render(opcao, True, cor)
            texto_rect = texto_surface.get_rect(center=(W // 2, y_pos))
            self.retangulos_opcoes.append(texto_rect)

            # Highlight
            if texto_rect.collidepoint(mouse_pos) or i == self.selecao_atual:
                self.selecao_atual = i
                cor = self.COR_HIGHLIGHT

            texto_surface = self.fonte_opcoes.render(opcao, True, cor)
            self.window.screen.blit(texto_surface, texto_rect)

            y_pos += 80

    def run(self):
        # Limpa o estado inicial de input (se o enter estava pressionado no momento da morte)
        self.teclado.key_pressed("ENTER")

        while True:
            proximo_estado = self.handle_events()
            if proximo_estado != "gameover":
                return proximo_estado

            self.draw()
            self.window.update()