import pygame
import pytmx
from Menu.menu import MenuPrincipal
from Menu.menu_controles import MenuControles
from Menu.menu_pause import MenuPause
from Menu.menu_gameover import MenuGameOver
from PPlay.window import Window
from PPlay.keyboard import Keyboard
from sys import exit
from Sons.sons import efeitos_sonoros
from Personagem.Volt import Volt
from Mapa.mapa_fase1 import Map
from Inimigo.InimigoPatrulha import InimigoPatrulha
import os


class Game:
    def __init__(self, largura=1080, altura=720, sons=None):
        self.window = Window(largura, altura)
        self.keyboard = self.window.get_keyboard()
        self.sons = sons if sons else efeitos_sonoros()
        if not sons:
            self.sons.tocar_musica()

        pygame.display.set_caption("Lab-Escape")
        self.screen = pygame.display.get_surface()

        self.clock = pygame.time.Clock()
        self.running = True

        # DEBUG E CARREGAMENTO DO MAPA
        try:
            self.map = Map("Mapa/Fase-1.tmx")
            print("INFO: Mapa Fase-1.tmx carregado com sucesso.")
        except Exception as e:
            print(f"ERRO CRÍTICO AO CARREGAR MAPA: {e}. Verifique o caminho 'Mapa/Fase-1.tmx'")
            self.map = None

        self.volt_personagem = Volt(910, 500)
        self.inimigos = []
        inimigo1 = InimigoPatrulha(
            x=1200,
            y=700,
            limite_esquerdo=1100,
            limite_direito=1500,
            velocidade=150
        )
        self.inimigos.append(inimigo1)
        self.offset_x = 0
        self.offset_y = 0

        self.pausado = False
        self.menu_pause = MenuPause(self.window, self.sons)
        self.p_pressionado_anteriormente = False

    def _handle_pausa_input(self):
        """Gerencia o input da tecla 'P' para alternar o estado de pausa."""
        tecla_p_agora = self.keyboard.key_pressed("P")

        if tecla_p_agora and not self.p_pressionado_anteriormente:
            self.pausado = not self.pausado
            if self.pausado:
                self.sons.tocar_selecao()
            else:
                self.sons.tocar_selecao_ok()

        self.p_pressionado_anteriormente = tecla_p_agora

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(60)
            dt_segundos = dt_ms / 1000.0

            self._handle_pausa_input()

            if self.pausado:
                proximo_estado = self.menu_pause.run()
                if proximo_estado == "jogo":
                    self.pausado = False
                elif proximo_estado == "menu":
                    self.running = False
                    return "menu"

                self.window.update()
                continue

            # --- Lógica normal do Jogo ---
            self.handle_events()

            proximo_estado = self.update(dt_segundos)
            if proximo_estado == "gameover":
                self.running = False
                return "gameover"

            self.draw()
            self.window.update()

        return "menu"

    def handle_events(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()

    def update(self, dt):
        self.volt_personagem.update(self.map, self.keyboard, dt)

        # Dados do Volt para o Inimigo
        volt_rect = self.volt_personagem.rect
        volt_invencivel = self.volt_personagem.invencivel

        # Atualiza e processa o dano de TODOS os inimigos
        for inimigo in self.inimigos:
            dano_info = inimigo.update(dt, volt_rect, volt_invencivel)

            if dano_info and not volt_invencivel:
                direcao_knockback = dano_info["direcao"] * -1

                self.volt_personagem.tomar_dano(dano_info["dano"], direcao_knockback)

                self.volt_personagem.invencivel = True
                self.volt_personagem.tempo_invencivel = pygame.time.get_ticks()

                # A verificação principal de gameover agora está no final

        # 🟢 LÓGICA DE DANO DE MAPA/ARMADILHA
        self.volt_personagem.verifica_dano(self.map)

        # 🟢 VERIFICAÇÃO FINAL DE GAME OVER APÓS TODOS OS DANOS
        if self.volt_personagem.vida_atual <= 0:
            print("Game Over!")
            return "gameover"

        agora = pygame.time.get_ticks()
        inimigos_a_remover = []
        raios_a_remover = []

        # 1. Colisão RAIOS vs INIMIGOS (e SOCO) - LÓGICA DE MORTE
        for poder in self.volt_personagem.poderes:
            rect_poder = pygame.Rect(
                poder.sprite.x,
                poder.sprite.y,
                poder.sprite.width,
                poder.sprite.height
            )
            for inimigo in self.inimigos:
                if rect_poder.colliderect(inimigo.rect):
                    inimigos_a_remover.append(inimigo)
                    raios_a_remover.append(poder)
                    self.sons.som_Poder()
                    break

        if self.volt_personagem.atacando and (
                self.volt_personagem.estado == "soco_direita" or self.volt_personagem.estado == "soco_esquerda"):
            if self.volt_personagem.frame_atual == 2:
                area_soco = self.volt_personagem.dano_soco()
                for inimigo in self.inimigos:
                    if area_soco.colliderect(inimigo.rect):
                        inimigos_a_remover.append(inimigo)
                        self.sons.som_Poder()

        # 4. REMOÇÃO DOS MORTOS
        for inimigo_morto in inimigos_a_remover:
            if inimigo_morto in self.inimigos:
                self.inimigos.remove(inimigo_morto)
        for raio_removido in raios_a_remover:
            if raio_removido in self.volt_personagem.poderes:
                self.volt_personagem.poderes.remove(raio_removido)

        # calcula offsets de câmera
        tela_w = self.window.width
        tela_h = self.window.height
        ideal_offset_x = self.volt_personagem.rect.centerx - (tela_w / 2)
        ideal_offset_y = self.volt_personagem.rect.centery - (tela_h / 2)
        self.offset_x = max(0, ideal_offset_x)
        self.offset_x = min(self.offset_x, max(0, self.map.width - tela_w))
        self.offset_y = max(0, ideal_offset_y)
        self.offset_y = min(self.offset_y, max(0, self.map.height - tela_h))

        return None  # Retorna None se o jogo continuar

    def draw(self):

        self.screen.fill((0, 0, 0))

        if self.map:
            self.map.draw(self.screen, int(self.offset_x), int(self.offset_y))

            for inimigo in self.inimigos:
                inimigo.draw(self.screen, int(self.offset_x), int(self.offset_y))

            self.volt_personagem.draw(self.screen, int(self.offset_x), int(self.offset_y))
            self.volt_personagem.draw_vida(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    temp_game = Game(1080, 720, sons=None)
    window_obj = temp_game.window
    sons_obj = temp_game.sons

    estado_jogo = "menu"

    while estado_jogo != "sair":

        if estado_jogo == "menu":
            menu = MenuPrincipal(window_obj, sons_menu=sons_obj)
            estado_jogo = menu.run()

        elif estado_jogo == "controles":
            controles_menu = MenuControles(window_obj, sons_menu=sons_obj)
            estado_jogo = controles_menu.run()

        elif estado_jogo == "jogo":
            game = Game(1080, 720, sons=sons_obj)
            estado_jogo = game.run()

        elif estado_jogo == "gameover":
            game_over_menu = MenuGameOver(window_obj, sons_menu=sons_obj)
            estado_jogo = game_over_menu.run()

    pygame.quit()
    exit()