import pygame
from PPlay.window import Window


class MenuPause:
    COR_PADRAO = (200, 200, 200)
    COR_HIGHLIGHT = (255, 255, 0)

    def __init__(self, window: Window, sons_menu=None):
        self.window = window
        self.teclado = window.get_keyboard()
        self.mouse = pygame.mouse
        self.sons = sons_menu

        self.opcoes = ["VOLTAR", "MENU PRINCIPAL"]
        self.selecao_atual = 0  # Inicialmente em "VOLTAR" (0)
        self.retangulos_opcoes = []

        pygame.font.init()
        self.fonte_titulo = pygame.font.Font(None, 80)
        self.fonte_opcoes = pygame.font.Font(None, 60)

        self.tempo_ultimo_movimento = pygame.time.get_ticks()
        self.cooldown_movimento = 200
        self.enter_pressionado_anteriormente = False

    def _atualizar_selecao_mouse(self):
        """Atualiza self.selecao_atual se o mouse estiver sobre uma opção."""
        mouse_pos = self.mouse.get_pos()
        for i, rect in enumerate(self.retangulos_opcoes):
            if rect.collidepoint(mouse_pos):
                self.selecao_atual = i
                return True
        return False

    def handle_events(self):
        agora = pygame.time.get_ticks()

        # 🟢 1. Atualiza a seleção via mouse ANTES de qualquer ENTER ou CLIQUE
        self._atualizar_selecao_mouse()

        # 2. Lógica de Navegação (Cooldown)
        movimento_permitido = agora - self.tempo_ultimo_movimento > self.cooldown_movimento

        if movimento_permitido:
            if self.teclado.key_pressed("UP"):
                self.selecao_atual = (self.selecao_atual - 1) % len(self.opcoes)
                self.tempo_ultimo_movimento = agora
                if self.sons: self.sons.tocar_selecao()
            elif self.teclado.key_pressed("DOWN"):
                self.selecao_atual = (self.selecao_atual + 1) % len(self.opcoes)
                self.tempo_ultimo_movimento = agora
                if self.sons: self.sons.tocar_selecao()

                # 3. Lógica de Confirmação (ENTER)
        tecla_enter_agora = self.teclado.key_pressed("ENTER")

        if tecla_enter_agora and not self.enter_pressionado_anteriormente:
            if self.sons: self.sons.tocar_selecao_ok()
            self.enter_pressionado_anteriormente = tecla_enter_agora
            return self.finalizar_pause()  # DECISÃO BASEADA EM self.selecao_atual (0 ou 1)

        self.enter_pressionado_anteriormente = tecla_enter_agora

        # 4. Despausa (ESCAPE)
        if self.teclado.key_pressed("ESCAPE"):
            if self.sons: self.sons.tocar_selecao_ok()
            return "jogo"

            # 5. Controle por MOUSE CLIQUE
        if self.mouse.get_pressed()[0]:
            # Como _atualizar_selecao_mouse já foi chamado, self.selecao_atual está correto.
            # Se o clique ocorreu sobre uma das opções, ele confirma:
            mouse_pos = self.mouse.get_pos()
            for rect in self.retangulos_opcoes:
                if rect.collidepoint(mouse_pos):
                    if self.sons: self.sons.tocar_selecao_ok()
                    return self.finalizar_pause()

        return "pausa"

    def finalizar_pause(self):
        """Define o próximo estado baseado na opção selecionada."""
        if self.selecao_atual == 0:
            return "jogo"  # Opção "VOLTAR" -> Retorna para o jogo
        elif self.selecao_atual == 1:
            return "menu"  # Opção "MENU PRINCIPAL" -> Retorna para o menu

    def draw(self):
        # ... (Desenho do overlay e título) ...
        overlay = pygame.Surface((self.window.width, self.window.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.window.screen.blit(overlay, (0, 0))

        W = self.window.width
        H = self.window.height

        titulo_surface = self.fonte_titulo.render("JOGO PAUSADO", True, (255, 255, 255))
        titulo_rect = titulo_surface.get_rect(center=(W // 2, H // 4))
        self.window.screen.blit(titulo_surface, titulo_rect)

        # Opções
        self.retangulos_opcoes = []
        y_pos = H // 2

        # 🟢 Chamamos _atualizar_selecao_mouse antes do draw para garantir que o highlight esteja correto.
        mouse_pos = self.mouse.get_pos()

        for i, opcao in enumerate(self.opcoes):
            cor = self.COR_PADRAO

            texto_surface = self.fonte_opcoes.render(opcao, True, cor)
            texto_rect = texto_surface.get_rect(center=(W // 2, y_pos))
            self.retangulos_opcoes.append(texto_rect)

            # Highlight
            if texto_rect.collidepoint(mouse_pos):
                self.selecao_atual = i
                cor = self.COR_HIGHLIGHT
            elif i == self.selecao_atual:
                cor = self.COR_HIGHLIGHT

            texto_surface = self.fonte_opcoes.render(opcao, True, cor)
            self.window.screen.blit(texto_surface, texto_rect)

            y_pos += 80

    def run(self):
        # 🟢 Limpa o estado inicial de ENTER antes de entrar no loop
        self.enter_pressionado_anteriormente = self.teclado.key_pressed("ENTER")

        while True:
            proximo_estado = self.handle_events()
            if proximo_estado != "pausa":
                return proximo_estado

            self.draw()
            self.window.update()