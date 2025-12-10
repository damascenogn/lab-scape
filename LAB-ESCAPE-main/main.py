# main.py (PPlay version)
import pygame
import pytmx
from Menu.menu import MenuPrincipal # NOVA IMPORTAÇÃO
from PPlay.window import Window
from PPlay.keyboard import Keyboard
from sys import exit
from Sons.sons import efeitos_sonoros
from Personagem.Volt import Volt
from Mapa.mapa_fase1 import Map
from Inimigo.InimigoPatrulha import InimigoPatrulha
import os


class Game:
    def __init__(self, largura=1080, altura=720):
        self.window = Window(largura, altura)
        self.keyboard = self.window.get_keyboard()
        self.sons = efeitos_sonoros()
        self.sons.tocar_musica()
    
        pygame.display.set_caption("Lab-Escape")
        self.screen = pygame.display.get_surface()

        self.clock = pygame.time.Clock()
        self.running = True

        # carregar mapa 
        self.map = Map("Mapa/Fase-1.tmx")

       # a posição onde o personagem aparecerá no mapa será fixa: 90, 1500
        self.volt_personagem = Volt(910, 500)
        # câmera offsets
        # Inimigos
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

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(60)  # ms desde última iteração
            dt_segundos = dt_ms / 1000.0
            self.handle_events()
            self.update(dt_segundos)
            self.draw()
            # atualiza eventos
            self.window.update()

    def handle_events(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()

    def update(self, dt):
        # atualiza personagem (usa mapa para colisões)
        self.volt_personagem.update(self.map, self.keyboard, dt)

        # Atualiza todos os inimigos
        for inimigo in self.inimigos:
            inimigo.update(dt)

        self.volt_personagem.verifica_dano(self.map)

        agora = pygame.time.get_ticks()
        inimigos_a_remover = []
        raios_a_remover = []

        # 1. Colisão INIMIGO vs VOLT (SÓ PARA DANO/KNOCKBACK)
        # Nenhuma lógica de morte deve estar neste loop!
        for inimigo in self.inimigos:
            if self.volt_personagem.rect.colliderect(inimigo.rect) and not self.volt_personagem.invencivel:

                # Determina a direção do Dano/Knockback
                if self.volt_personagem.rect.centerx < inimigo.rect.centerx:
                    direcao_knockback = -1
                else:
                    direcao_knockback = 1

                # Aplica Dano e Knockback
                self.volt_personagem.tomar_dano(10, direcao_knockback)

                # Ativa Invencibilidade
                self.volt_personagem.invencivel = True
                self.volt_personagem.tempo_invencivel = agora

                if self.volt_personagem.vida_atual <= 0:
                    print("Game Over!")
                    self.running = False

        # --- NOVO BLOCO: COLISÃO ATAQUES vs INIMIGOS (PARA MORTE) ---

        # 2. Colisão RAIOS vs INIMIGOS
        # Este loop deve estar alinhado com o loop 1 (inimigo vs volt)
        for poder in self.volt_personagem.poderes:
            # Precisa do retangulo do poder para colisão
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
                    self.sons.som_MorteInimigo()
                    break  # O raio só pode atingir um inimigo

        # 3. Colisão SOCO vs INIMIGOS
        # Este bloco deve estar alinhado com o loop 1 e 2
        if self.volt_personagem.atacando and (
                self.volt_personagem.estado == "soco_direita" or self.volt_personagem.estado == "soco_esquerda"):

            # Só pega a área de soco no frame de acerto
            if self.volt_personagem.frame_atual == 2:
                # O dano_soco() do Volt.py deve retornar o retângulo de ataque!
                area_soco = self.volt_personagem.dano_soco()

                for inimigo in self.inimigos:
                    if area_soco.colliderect(inimigo.rect):
                        inimigos_a_remover.append(inimigo)
                        self.sons.som_MorteInimigo()

        # 4. REMOÇÃO DOS MORTOS (DEPOIS DE TODOS OS LOOPS DE VERIFICAÇÃO)

        for inimigo_morto in inimigos_a_remover:
            if inimigo_morto in self.inimigos:
                self.inimigos.remove(inimigo_morto)

        for raio_removido in raios_a_remover:
            if raio_removido in self.volt_personagem.poderes:
                self.volt_personagem.poderes.remove(raio_removido)

        # calcula offsets de câmera para centralizar personagem
        tela_w = self.window.width
        tela_h = self.window.height

        ideal_offset_x = self.volt_personagem.rect.centerx - (tela_w / 2)
        ideal_offset_y = self.volt_personagem.rect.centery - (tela_h / 2)

        self.offset_x = max(0, ideal_offset_x)
        self.offset_x = min(self.offset_x, max(0, self.map.width - tela_w))

        self.offset_y = max(0, ideal_offset_y)
        self.offset_y = min(self.offset_y, max(0, self.map.height - tela_h))



    def draw(self):


        
        # limpa tela (pygame surface)
        self.screen.fill((0, 0, 0))

        # desenha o mapa (parte visível)
        self.map.draw(self.screen, int(self.offset_x), int(self.offset_y))

        #Desenha todos os inimigos
        for inimigo in self.inimigos:
            inimigo.draw(self.screen, int(self.offset_x), int(self.offset_y))
        
        # desenha personagem em posição relativa à câmera
        screen_x = self.volt_personagem.rect.x - int(self.offset_x)
        screen_y = self.volt_personagem.rect.y - int(self.offset_y)
        self.volt_personagem.draw(self.screen, int(self.offset_x), int(self.offset_y))

        # desenha HUD (vida)
        self.volt_personagem.draw_vida(self.screen)

        # atualiza display (pygame flip)
        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()

    # 1. Configurações Iniciais da Janela (reaproveitando sua classe Game para a Window)
    # Criamos uma instância temporária de Game só para obter o objeto Window e configurações.
    temp_game = Game(1080, 720)
    window_obj = temp_game.window

    # NOVO: Gerenciador de Estados/Cenas
    estado_jogo = "menu"

    while estado_jogo != "sair":

        if estado_jogo == "menu":
            menu = MenuPrincipal(window_obj)
            estado_jogo = menu.run()  # O menu executa até o jogador escolher INICIAR ou SAIR

        elif estado_jogo == "jogo":
            # Aqui, criamos a instância real do jogo
            game = Game(1080, 720)
            game.run()
            # Quando o game.run() terminar (game over ou quit), voltamos ao menu
            estado_jogo = "menu"

            # Se estado_jogo for "sair", o loop While termina
    pygame.quit()
    exit()

if __name__ == "__main__":
    pygame.init()
    game = Game(1080, 720)
    game.run()
