import pygame
from PPlay.window import Window
import os


class MenuControles:
    # Cores
    COR_TITULO = (255, 220, 0)
    COR_ACAO = (0, 150, 255)
    COR_TECLA = (255, 255, 255)
    ESPACO_LINHA = 50

    def __init__(self, window: Window, sons_menu=None):
        self.window = window
        self.teclado = window.get_keyboard()
        self.running = True
        self.proxima_cena = "menu"
        self.sons = sons_menu

        # --- CONFIGURAÇÃO DE ASSETS ---
        caminho_bg = "Assets/Images/background_menu.png"

        pygame.font.init()
        self.fonte_titulo = pygame.font.Font(None, 70)
        self.fonte_texto = pygame.font.Font(None, 40)

        # Carregamento do Background
        try:
            img_bg = pygame.image.load(caminho_bg).convert()
            self.background = pygame.transform.scale(img_bg, (window.width, window.height))
        except:
            self.background = None

    def handle_events(self):
        # Apenas ESCAPE retorna
        if self.teclado.key_pressed("ESCAPE"):
            if self.sons:
                self.sons.tocar_selecao()
            self.running = False
            self.proxima_cena = "menu"

    def draw(self):
        # 1. Desenha Background
        if self.background:
            self.window.screen.blit(self.background, (0, 0))
        else:
            self.window.screen.fill((0, 0, 0))

        W = self.window.width
        H = self.window.height

        # 2. Desenha Título
        titulo_surface = self.fonte_titulo.render("Controles", True, self.COR_TITULO)
        titulo_rect = titulo_surface.get_rect(center=(W // 2, H // 6))
        self.window.screen.blit(titulo_surface, titulo_rect)

        # 3. Desenha a Lista de Controles
        # 🟢 BOTÕES ATUALIZADOS PARA SUA CONFIGURAÇÃO FINAL
        controles = [
            ("MOVIMENTO", "A (Esq), D (Dir)"),
            ("PULO", "ESPAÇO"),
            ("ATAQUE CORPO-A-CORPO (Soco)", "E"),
            ("ATAQUE À DISTÂNCIA (Raio)", "Q"),
            ("PAUSAR JOGO", "P"),
            ("VOLTAR AO MENU", "ESC")
        ]

        y_pos = titulo_rect.bottom + 50

        for acao, tecla in controles:
            # Renderiza a Ação
            acao_surface = self.fonte_texto.render(acao + ":", True, self.COR_ACAO)
            acao_rect = acao_surface.get_rect(midright=(W // 2 - 20, y_pos))
            self.window.screen.blit(acao_surface, acao_rect)

            # Renderiza a Tecla
            tecla_surface = self.fonte_texto.render(tecla, True, self.COR_TECLA)
            tecla_rect = tecla_surface.get_rect(midleft=(W // 2 + 20, y_pos))
            self.window.screen.blit(tecla_surface, tecla_rect)

            y_pos += self.ESPACO_LINHA

        # 4. Desenha instrução de retorno no rodapé
        instrucao_surface = self.fonte_texto.render("Pressione ESC para voltar", True, self.COR_TECLA)
        instrucao_rect = instrucao_surface.get_rect(center=(W // 2, H - 50))
        self.window.screen.blit(instrucao_surface, instrucao_rect)

    def run(self):
        while self.running:
            self.window.screen.fill((0, 0, 0))
            self.handle_events()
            self.draw()
            self.window.update()
        return self.proxima_cena