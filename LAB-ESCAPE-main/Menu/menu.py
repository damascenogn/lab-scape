import pygame
from PPlay.window import Window
import os


class MenuPrincipal:
    # 🟢 VARIÁVEIS DE CLASSE (Configuração de Layout)
    ALTURA_LOGO_RELATIVA = 4
    ESPACO_LOGO_MENU = 150
    ESPACO_ENTRE_OPCOES = 60

    def __init__(self, window: Window, sons_menu=None):
        self.window = window
        self.teclado = window.get_keyboard()
        self.mouse = pygame.mouse
        self.running = True
        self.proxima_cena = "menu"
        self.sons = sons_menu
        self.selecao_anterior = 0

        # 1. TÍTULO E FONTES
        pygame.font.init()

        # --- DEFINIÇÃO DOS CAMINHOS ---
        caminho_fonte_base = "Assets/Fonts/"
        caminho_bg = "Assets/Images/background_menu.png"
        caminho_logo = os.path.join("Assets", "Images", "logo.png")

        # 2. INICIALIZAÇÃO DE FONTES E OBJETOS GRÁFICOS
        self.fonte_titulo_fallback = pygame.font.Font(None, 90)
        self.logo = None
        self.background = None

        # --- CARREGAMENTO DE ASSETS (O seu código original) ---
        try:
            self.fonte = pygame.font.Font(os.path.join(caminho_fonte_base, "MENU_OPCOES_FONTE.ttf"), 50)
        except Exception as e:
            print(f"AVISO: Fonte das opções não carregada. Erro: {e}. Usando fallback.")
            self.fonte = pygame.font.Font(None, 50)
        try:
            img_bg = pygame.image.load(caminho_bg).convert()
            self.background = pygame.transform.scale(img_bg, (window.width, window.height))
        except Exception as e:
            print(f"AVISO: Imagem de fundo não encontrada. Erro: {e}. Usando fundo preto.")
        try:
            self.logo = pygame.image.load(caminho_logo).convert_alpha()
        except Exception as e:
            print(f"AVISO: Logo imagem ({caminho_logo}) não encontrada. Erro: {e}. Usando texto de fallback.")
            self.logo = None

        # 3. OPÇÕES E CONTROLES
        self.opcoes = ["INICIAR JOGO", "CONTROLES", "SAIR"]
        self.selecao_atual = 0
        self.retangulos_opcoes = []
        self.tempo_ultimo_movimento = 0
        self.cooldown_movimento = 200

    def handle_events(self):
        agora = pygame.time.get_ticks()
        self.selecao_anterior = self.selecao_atual

        # 1. Controle por Teclado (Setas para cima/baixo)
        if agora - self.tempo_ultimo_movimento > self.cooldown_movimento:
            if self.teclado.key_pressed("UP"):
                self.selecao_atual = (self.selecao_atual - 1) % len(self.opcoes)
                self.tempo_ultimo_movimento = agora
            elif self.teclado.key_pressed("DOWN"):
                self.selecao_atual = (self.selecao_atual + 1) % len(self.opcoes)
                self.tempo_ultimo_movimento = agora

        # 🟢 Feedback Sonoro na Mudança de Seleção (Chama o tocar_selecao que usa som_Recarga)
        if self.selecao_atual != self.selecao_anterior and self.sons:
            self.sons.tocar_selecao()

        # Lógica de Transição (ENTER ou MOUSE CLIQUE)
        selecao_confirmada = False

        # 2. Controle por MOUSE CLIQUE
        if self.mouse.get_pressed()[0]:
            mouse_pos = self.mouse.get_pos()
            for i, rect in enumerate(self.retangulos_opcoes):
                if rect.collidepoint(mouse_pos):
                    self.selecao_atual = i
                    selecao_confirmada = True
                    break

        # 3. Controle por ENTER
        if self.teclado.key_pressed("ENTER"):
            selecao_confirmada = True

        # Executa a transição se a seleção foi confirmada
        if selecao_confirmada:
            if self.selecao_atual == 0:
                self.proxima_cena = "jogo"
            elif self.selecao_atual == 1:
                self.proxima_cena = "controles"
            elif self.selecao_atual == 2:
                self.proxima_cena = "sair"
            self.running = False

    def draw(self):
        if self.background:
            self.window.screen.blit(self.background, (0, 0))
        else:
            self.window.screen.fill((0, 0, 0))

        self.retangulos_opcoes = []
        mouse_pos = self.mouse.get_pos()
        titulo_area_y = self.window.height // self.ALTURA_LOGO_RELATIVA

        # 2. DESENHO DA LOGO (IMAGEM OU TEXTO FALLBACK)
        if self.logo:
            logo_rect = self.logo.get_rect(center=(self.window.width // 2, titulo_area_y))
            self.window.screen.blit(self.logo, logo_rect)
            y_pos_opcoes = logo_rect.bottom + self.ESPACO_LOGO_MENU
        else:
            # --- FALLBACK ---
            titulo_texto = "LAB-ESCAPE"
            cor_titulo = (255, 220, 0)
            cor_sombra = (0, 0, 0)
            offset_sombra = 6
            sombra_surface = self.fonte_titulo_fallback.render(titulo_texto, True, cor_sombra)
            titulo_rect = sombra_surface.get_rect(center=(self.window.width // 2, titulo_area_y))
            sombra_pos = (titulo_rect.x + offset_sombra, titulo_rect.y + offset_sombra)
            self.window.screen.blit(sombra_surface, sombra_pos)
            titulo_surface = self.fonte_titulo_fallback.render(titulo_texto, True, cor_titulo)
            self.window.screen.blit(titulo_surface, titulo_rect)
            y_pos_opcoes = titulo_rect.bottom + self.ESPACO_LOGO_MENU

        # 3. Desenha Opções (INICIAR JOGO, CONTROLES, SAIR)
        y_pos = y_pos_opcoes
        for i, opcao in enumerate(self.opcoes):
            cor_padrao = (0, 150, 255)
            cor_highlight = (255, 255, 0)
            cor = cor_padrao
            texto_surface = self.fonte.render(opcao, True, cor_padrao)
            texto_rect = texto_surface.get_rect(center=(self.window.width // 2, y_pos))
            self.retangulos_opcoes.append(texto_rect)

            if texto_rect.collidepoint(mouse_pos) or i == self.selecao_atual:
                self.selecao_atual = i
                cor = cor_highlight

            texto_surface = self.fonte.render(opcao, True, cor)
            self.window.screen.blit(texto_surface, texto_rect)
            y_pos += self.ESPACO_ENTRE_OPCOES

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.window.update()

        return self.proxima_cena