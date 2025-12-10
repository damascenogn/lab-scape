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
from Inimigo.InimigoAtirador import InimigoAtirador
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

        # Inicialização dos Inimigos
        self.inimigos = []

        # 1. Inimigo Patrulha (Posição Original)
        inimigo1 = InimigoPatrulha(
            x=1200,
            y=700,
            limite_esquerdo=1100,
            limite_direito=1500,
            velocidade=150
        )
        self.inimigos.append(inimigo1)

        # 2. Inimigo Atirador (Posicionamento Corrigido)
        atirador1 = InimigoAtirador(
            x=850,
            y=265,
            limite_esquerdo=800,
            limite_direito=900
        )
        self.inimigos.append(atirador1)

        self.projeteis_inimigos_ativos = []

        self.offset_x = 0
        self.offset_y = 0

        self.pausado = False
        self.menu_pause = MenuPause(self.window, self.sons)
        self.p_pressionado_anteriormente = False

        self.soco_acertou = False

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

        # Lógica de reset do flag de hit do soco
        if not self.volt_personagem.atacando:
            self.soco_acertou = False

        self.volt_personagem.update(self.map, self.keyboard, dt)

        volt_rect = self.volt_personagem.rect
        volt_invencivel = self.volt_personagem.invencivel

        # Atualiza inimigos e processa dano/projéteis
        for inimigo in self.inimigos:
            if inimigo.morto:
                if hasattr(inimigo, '_update_projeteis'):
                    inimigo._update_projeteis(dt)
                continue

            resultado_update = inimigo.update(dt, volt_rect, volt_invencivel)

            # 1. Coleta projéteis do InimigoAtirador
            if isinstance(inimigo, InimigoAtirador):
                self.projeteis_inimigos_ativos.extend(resultado_update)

            # 2. Processa o dano do ataque corpo-a-corpo (InimigoPatrulha)
            if isinstance(inimigo, InimigoPatrulha) and resultado_update and resultado_update[
                "tipo"] == "dano" and not volt_invencivel:
                dano_info = resultado_update
                direcao_knockback = dano_info["direcao"] * -1

                self.volt_personagem.tomar_dano(dano_info["dano"], direcao_knockback)
                self.volt_personagem.invencivel = True
                self.volt_personagem.tempo_invencivel = pygame.time.get_ticks()

        # LÓGICA DE DANO DE MAPA/ARMADILHA
        self.volt_personagem.verifica_dano(self.map)

        # 3. COLISÃO PROJÉTEIS INIMIGOS vs VOLT (CORREÇÃO HIT KILL)
        projeteis_a_remover_por_acerto = []
        for projetil in self.projeteis_inimigos_ativos:
            if projetil.rect.colliderect(volt_rect) and not volt_invencivel:
                self.volt_personagem.tomar_dano(projetil.DANO, projetil.direcao)

                self.volt_personagem.invencivel = True
                self.volt_personagem.tempo_invencivel = pygame.time.get_ticks()

                # 🟢 CRÍTICO: MARCA O PROJÉTIL PARA REMOÇÃO E O DESATIVA IMEDIATAMENTE
                projeteis_a_remover_por_acerto.append(projetil)
                projetil.ativo = False

                # 4. VERIFICAÇÃO FINAL DE GAME OVER
        if self.volt_personagem.vida_atual <= 0:
            print("Game Over!")
            return "gameover"

        agora = pygame.time.get_ticks()
        inimigos_a_remover = []
        raios_a_remover = []

        # 5. Colisão RAIOS e SOCO do Volt vs Inimigos - LÓGICA DE MORTE

        # Colisão de RAIOS
        for poder in self.volt_personagem.poderes:
            rect_poder = pygame.Rect(
                poder.sprite.x,
                poder.sprite.y,
                poder.sprite.width,
                poder.sprite.height
            )
            for inimigo in self.inimigos:
                if not inimigo.morto and rect_poder.colliderect(inimigo.rect):
                    morreu = inimigo.tomar_dano(InimigoPatrulha.DANO_SOCO_VOLT)

                    if morreu:
                        self.sons.som_Poder()
                        inimigos_a_remover.append(inimigo)

                    raios_a_remover.append(poder)
                    break

        # Colisão de SOCO (Dano único por animação)
        if self.volt_personagem.atacando and not self.soco_acertou and (
                self.volt_personagem.estado == "soco_direita" or self.volt_personagem.estado == "soco_esquerda"):

            if self.volt_personagem.frame_atual == 2:
                area_soco = self.volt_personagem.dano_soco()

                for inimigo in self.inimigos:
                    if not inimigo.morto and area_soco.colliderect(inimigo.rect):
                        morreu = inimigo.tomar_dano(InimigoPatrulha.DANO_SOCO_VOLT)

                        if morreu:
                            self.sons.som_Poder()
                            inimigos_a_remover.append(inimigo)

                        self.soco_acertou = True
                        break

        # 6. REMOÇÃO DOS MORTOS e LIMPEZA
        for inimigo_morto in inimigos_a_remover:
            if inimigo_morto in self.inimigos:
                self.inimigos.remove(inimigo_morto)
        for raio_removido in raios_a_remover:
            if raio_removido in self.volt_personagem.poderes:
                self.volt_personagem.poderes.remove(raio_removido)

        # LIMPEZA DOS PROJÉTEIS INIMIGOS (Remove os que acertaram ou saíram da tela)
        self.projeteis_inimigos_ativos = [p for p in self.projeteis_inimigos_ativos if
                                          p not in projeteis_a_remover_por_acerto and p.ativo]

        # 7. calcula offsets de câmera
        tela_w = self.window.width
        tela_h = self.window.height
        ideal_offset_x = self.volt_personagem.rect.centerx - (tela_w / 2)
        ideal_offset_y = self.volt_personagem.rect.centery - (tela_h / 2)
        self.offset_x = max(0, ideal_offset_x)
        self.offset_x = min(self.offset_x, max(0, self.map.width - tela_w))
        self.offset_y = max(0, ideal_offset_y)
        self.offset_y = min(self.offset_y, max(0, self.map.height - tela_h))

        return None

    def draw(self):

        self.screen.fill((0, 0, 0))

        if self.map:
            self.map.draw(self.screen, int(self.offset_x), int(self.offset_y))

            for inimigo in self.inimigos:
                inimigo.draw(self.screen, int(self.offset_x), int(self.offset_y))

            # Desenha projéteis inimigos ativos
            for projetil in self.projeteis_inimigos_ativos:
                projetil.draw(self.screen, self.offset_x, self.offset_y)

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