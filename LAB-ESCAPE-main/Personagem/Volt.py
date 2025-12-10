import pygame
import os
from Poderes.bola_raio import Raio
from Sons.sons import efeitos_sonoros


class Volt:
    def __init__(self, x, y):
        # Carregar imagens e animações
        self.carregar_imagens()
        self.sons = efeitos_sonoros()

        self.frame_atual = 0
        self.image = self.respirando[self.frame_atual]
        self.rect = pygame.Rect(x, y, 40, 106)
        self.rect.center = (x, y)

        # FÍSICA
        self.gravidade = 0.8
        self.vel_y = 0
        self.forca_pulo = -18.5
        self.no_chao = False
        self.pos_no_chao = self.rect.y

        # MOVIMENTO
        self.velocidade = 5
        self.velocidade_animacao = 150

        # ESTADOS
        self.atacando = False
        self.olhando_direita = True
        self.estado = "parado"
        self.ultima_atualizacao = pygame.time.get_ticks()
        self.carregando = False

        # VIDA
        self.max_vida = 100
        self.vida_atual = 100

        # CARGAS RAIO
        self.cargas_raio = 0
        self.max_cargas_raio = 3

        # CONTROLE DE DANO
        self.invencivel = False
        self.tempo_invencivel = 0
        self.duracao = 1000  # 1 segundo de invencibilidade

        # CONTROLE DE KNOCKBACK
        self.em_knockback = False
        self.kb_velocidade = 0
        self.kb_duracao = 0.25
        self.kb_tempo_restante = 0
        # Força base do knockback horizontal
        self.FORCA_KB_HORIZONTAL = 10
        # Força base do knockback vertical
        self.FORCA_KB_VERTICAL = -5

    def carregar_imagens(self):
        # Este método não precisou de alterações, mantendo a originalidade.
        base = "Personagem"

        respirando = pygame.image.load(os.path.join(base, "Parado", "respirandocurto.png")).convert_alpha()
        correndo_direita = pygame.image.load(os.path.join(base, "correndo", "correndo-direita.png")).convert_alpha()
        correndo_esquerda = pygame.image.load(os.path.join(base, "correndo", "correndo-esquerda.png")).convert_alpha()
        pulando_direita = pygame.image.load(os.path.join(base, "Pulando", "pulando-direita.png")).convert_alpha()
        pulando_esquerda = pygame.image.load(os.path.join(base, "Pulando", "pulando-esquerda.png")).convert_alpha()
        poder_direita = pygame.image.load(os.path.join(base, "Poder", "poder-direita.png")).convert_alpha()
        poder_esquerda = pygame.image.load(os.path.join(base, "Poder", "poder-esquerda.png")).convert_alpha()
        socando_direita = pygame.image.load(os.path.join(base, "Socando", "socando_direita.png")).convert_alpha()
        socando_esquerda = pygame.image.load(os.path.join(base, "Socando", "socando_esquerda.png")).convert_alpha()
        recarregando = pygame.image.load(os.path.join(base, "Parado", "recarregando.png")).convert_alpha()

        self.moldura_vida = pygame.image.load(os.path.join(base, "Vida", "moldura_vida.png")).convert_alpha()
        img_raio_azul = pygame.image.load("Poderes/Raio/carga/carga_cheia.png").convert_alpha()
        self.icone_raio_azul = pygame.transform.scale(img_raio_azul, (30, 30))
        img_raio_cinza = pygame.image.load("Poderes/Raio/carga/barra_carga.png").convert_alpha()
        self.icone_raio_cinza = pygame.transform.scale(img_raio_cinza, (30, 30))

        self.respirando = []
        self.correndo_direita = []
        self.correndo_esquerda = []
        self.pulando_direita = []
        self.pulando_esquerda = []
        self.poder_raio_esquerda = []
        self.poder_raio_direita = []
        self.poderes = []
        self.novo_tiro = []
        self.soco_esq = []
        self.soco_dir = []
        self.recarregando = []

        for i in range(6):
            self.soco_dir.append(socando_direita.subsurface((i * 128, 0, 128, 106)))
            self.soco_esq.append(socando_esquerda.subsurface((i * 128, 0, 128, 106)))
            self.poder_raio_direita.append(poder_direita.subsurface((i * 128, 0, 128, 96)))
            self.poder_raio_esquerda.append(poder_esquerda.subsurface((i * 128, 0, 128, 96)))
            self.correndo_direita.append(correndo_direita.subsurface((i * 40, 0, 40, 106)))
            self.correndo_esquerda.append(correndo_esquerda.subsurface((i * 40, 0, 40, 106)))

        for i in range(8):
            self.pulando_direita.append(pulando_direita.subsurface((i * 40, 0, 40, 106)))
            self.pulando_esquerda.append(pulando_esquerda.subsurface((i * 40, 0, 40, 106)))

        for i in range(4):
            self.respirando.append(respirando.subsurface((i * 38, 0, 38, 106)))
            self.recarregando.append(recarregando.subsurface((i * 128, 0, 128, 106)))

    def animar(self):
        # Este método não precisou de alterações.
        agora = pygame.time.get_ticks()
        if agora - self.ultima_atualizacao > self.velocidade_animacao:
            self.ultima_atualizacao = agora
            antigo_rect = self.rect.copy()

            if self.estado == "parado":
                self.frame_atual = (self.frame_atual + 1) % len(self.respirando)
                self.image = self.respirando[self.frame_atual]

            elif self.estado == "correndo_direita":
                self.frame_atual = (self.frame_atual + 1) % len(self.correndo_direita)
                self.image = self.correndo_direita[self.frame_atual]

            elif self.estado == "correndo_esquerda":
                self.frame_atual = (self.frame_atual + 1) % len(self.correndo_esquerda)
                self.image = self.correndo_esquerda[self.frame_atual]

            elif self.estado == "pulando_direita":
                self.frame_atual = (self.frame_atual + 1) % len(self.pulando_direita)
                self.image = self.pulando_direita[self.frame_atual]

            elif self.estado == "pulando_esquerda":
                self.frame_atual = (self.frame_atual + 1) % len(self.pulando_esquerda)
                self.image = self.pulando_esquerda[self.frame_atual]

            elif self.estado == "poder_raio_direita":
                if self.frame_atual >= len(self.poder_raio_direita) - 1:
                    self.frame_atual = 0
                    self.estado = "parado"
                    self.atacando = False
                else:
                    self.frame_atual += 1
                    if self.frame_atual == 5 and not self.carregando:
                        self.criar_raio()
                self.image = self.poder_raio_direita[self.frame_atual]

            elif self.estado == "poder_raio_esquerda":
                if self.frame_atual >= len(self.poder_raio_esquerda) - 1:
                    self.frame_atual = 0
                    self.estado = "parado"
                    self.atacando = False
                else:
                    self.frame_atual += 1
                    if self.frame_atual == 5 and not self.carregando:
                        self.criar_raio()
                self.image = self.poder_raio_esquerda[self.frame_atual]

            elif self.estado == "soco_esquerda":
                if self.frame_atual >= len(self.soco_esq) - 1:
                    self.frame_atual = 0
                    self.estado = "parado"
                    self.atacando = False
                else:
                    self.frame_atual += 1
                    if self.frame_atual == 2:
                        self.dano_soco()
                self.image = self.soco_esq[self.frame_atual]

            elif self.estado == "soco_direita":
                if self.frame_atual >= len(self.soco_dir) - 1:
                    self.frame_atual = 0
                    self.estado = "parado"
                    self.atacando = False
                else:
                    self.frame_atual += 1
                    if self.frame_atual == 2:
                        self.dano_soco()
                self.image = self.soco_dir[self.frame_atual]

            elif self.estado == "recarregando":
                if self.frame_atual >= len(self.recarregando) - 1:
                    self.frame_atual = 0
                    self.estado = "parado"
                    self.atacando = False
                else:
                    self.frame_atual += 1

                self.image = self.recarregando[self.frame_atual]

            novo_rect = self.image.get_rect()
            novo_rect.midbottom = antigo_rect.midbottom
            self.rect = novo_rect

    def colisoes_mapa(self, mapa, tecla_get):
        velocidade_x = 0

        # 1. TRATAMENTO DA VELOCIDADE X (Prioridade: Knockback > Input)

        # A. KNOCKBACK TEM PRIORIDADE MÁXIMA
        if self.em_knockback:
            velocidade_x = self.kb_velocidade

        # B. PROCESSAMENTO DE INPUT NORMAL
        elif not self.em_knockback:
            if tecla_get[pygame.K_q] and not self.atacando and self.cargas_raio > 0:
                self.sons.som_Poder()
                self.atacando = True
                self.frame_atual = 0
                self.carregando = False

                self.cargas_raio -= 1

                self.estado = "poder_raio_direita" if self.olhando_direita else "poder_raio_esquerda"
                velocidade_x = 0

            elif tecla_get[pygame.K_e] and not self.atacando:
                # --- CORREÇÃO DO SOCO: ADICIONA INVENCIBILIDADE ---
                agora = pygame.time.get_ticks()
                self.invencivel = True
                self.tempo_invencivel = agora
                # A duração de 1000ms que você definiu deve ser suficiente para o teste
                # mas você pode reduzi-la para algo como 300ms se for muito longa.

                self.atacando = True
                self.frame_atual = 0
                self.estado = "soco_direita" if self.olhando_direita else "soco_esquerda"
                velocidade_x = 0
                self.atacando = True
                self.frame_atual = 0
                self.estado = "soco_direita" if self.olhando_direita else "soco_esquerda"
                velocidade_x = 0

            elif tecla_get[pygame.K_SPACE] and self.no_chao and not self.atacando:
                self.vel_y = self.forca_pulo
                self.no_chao = False
                self.estado = "pulando_direita" if self.olhando_direita else "pulando_esquerda"

            elif not self.atacando:
                if tecla_get[pygame.K_d]:
                    self.estado = "correndo_direita"
                    self.olhando_direita = True
                    velocidade_x = self.velocidade

                elif tecla_get[pygame.K_a]:
                    self.estado = "correndo_esquerda"
                    self.olhando_direita = False
                    velocidade_x = -self.velocidade

                elif self.no_chao:
                    self.pos_no_chao = self.rect.y
                    self.estado = "parado"

            # ATENÇÃO: Corrigido para ser '==' e movido para dentro do bloco de input
            elif tecla_get[pygame.K_RIGHT]:
                self.estado = "socando_esquerda"

                # Zera velocidade se estiver atacando (mas não em knockback)
            if self.atacando:
                velocidade_x = 0

        # FIM DO BLOCO DE TRATAMENTO DE VELOCIDADE X

        # 2. MOVIMENTO HORIZONTAL E COLISÃO (FORA DO elif/if de Knockback)
        self.rect.x += velocidade_x
        for parede in mapa.colisoes_parede:
            if self.rect.colliderect(parede):
                if velocidade_x > 0:
                    self.rect.right = parede.left
                elif velocidade_x < 0:
                    self.rect.left = parede.right

        # 3. MOVIMENTO VERTICAL (Gravidade e Colisão Vertical)

        # A. APLICA GRAVIDADE E MOVIMENTO VERTICAL
        self.vel_y += self.gravidade
        self.rect.y += self.vel_y

        # B. COLISÃO VERTICAL
        self.no_chao = False

        for parede in mapa.colisoes_parede:
            if self.rect.colliderect(parede):
                if self.vel_y > 0:  # Caindo (Colisão por baixo)
                    self.rect.bottom = parede.top
                    self.vel_y = 0

                    # SÓ PODE ESTAR NO CHÃO SE NÃO ESTIVER EM KNOCKBACK
                    if not self.em_knockback:
                        self.no_chao = True

                elif self.vel_y < 0:  # Subindo (Colisão por cima/cabeça)
                    self.rect.top = parede.bottom
                    self.vel_y = 0

    def criar_raio(self):
        direcao = 1 if self.olhando_direita else -1
        # Cria o raio na posição atual
        novo_tiro = Raio(self.rect.centerx, self.rect.centery, direcao, "Poderes/Raio/raio.png")
        self.poderes.append(novo_tiro)
        self.ja_lancou = True

    def atualiza_knockback(self, dt):
        """Atualiza o tempo de knockback e zera a velocidade quando termina."""
        if self.em_knockback:
            self.kb_tempo_restante -= dt
            # O estado de 'no_chao' só é ativado no colisoes_mapa quando kb_tempo_restante <= 0
            if self.kb_tempo_restante <= 0:
                self.em_knockback = False
                self.kb_velocidade = 0

    def update(self, mapa, keyboard, dt):
        tecla = pygame.key.get_pressed()
        self.coletar_recarga(mapa)

        # CHAMA O CONTROLE DE KNOCKBACK ANTES DO MOVIMENTO (CORREÇÃO 3)
        self.atualiza_knockback(dt)

        self.colisoes_mapa(mapa, tecla)
        self.verifica_dano(mapa)
        self.animar()

        for poder in self.poderes[:]:
            poder.update(dt)

            rect_poder = pygame.Rect(
                poder.sprite.x,
                poder.sprite.y,
                poder.sprite.width,
                poder.sprite.height
            )
            for parede in mapa.colisoes_parede:
                if rect_poder.colliderect(parede):
                    self.poderes.remove(poder)
                    break

    def draw(self, surface, offset_x, offset_y):
        # Este método não precisou de alterações.
        rect_visual = self.image.get_rect()
        rect_visual.midbottom = self.rect.midbottom

        screen_x = self.rect.x - offset_x
        screen_y = self.rect.y - offset_y
        surface.blit(self.image, (screen_x, screen_y))

        for poder in self.poderes:
            real_x = poder.sprite.x
            real_y = poder.sprite.y
            poder.sprite.x = real_x - offset_x
            poder.sprite.y = real_y - 20 - offset_y
            poder.sprite.draw()
            poder.sprite.x = real_x
            poder.sprite.y = real_y

    def draw_vida(self, tela):
        # Este método não precisou de alterações.
        largura_barra = 150
        altura_barra = 20
        cor_fundo = (255, 0, 0)
        cor_vida = (0, 255, 0)

        mx = 20
        my = 20

        perc = self.vida_atual / self.max_vida
        largura_preenchimento = largura_barra * perc

        fundo_rect = pygame.Rect(mx + 30, my + 17, largura_barra, altura_barra)
        vida_rect = pygame.Rect(mx + 30, my + 17, largura_preenchimento, altura_barra)

        pygame.draw.rect(tela, cor_fundo, fundo_rect)
        pygame.draw.rect(tela, cor_vida, vida_rect)

        tela.blit(self.moldura_vida, (mx, my))
        self.draw_raio(tela)

    def dano_soco(self):
        # A área de soco só é relevante quando o ataque está ativo (frame 2 na animação)
        # O self.atacando já garante que estamos no estado de soco.

        area_soco = pygame.Rect(0, 0, 60, 60)
        area_soco.centery = self.rect.centery

        if self.olhando_direita:
            area_soco.left = self.rect.right
        else:
            area_soco.right = self.rect.left

        return area_soco

    def verifica_dano(self, mapa):
        # Este método não precisou de alterações.
        agora = pygame.time.get_ticks()
        if self.invencivel and (agora - self.tempo_invencivel > self.duracao):
            self.invencivel = False

        if not self.invencivel:
            for armadilha in mapa.armadilhas:
                if self.rect.colliderect(armadilha):
                    self.tomar_dano(10, 0)  # Assumimos direcao 0 para armadilhas fixas
                    self.invencivel = True
                    self.tempo_invencivel = agora

    def tomar_dano(self, quantidade, direcao_dano):
        """
        Recebe dano e inicia o knockback.
        direcao_dano: 1 (direita), -1 (esquerda), 0 (sem knockback horizontal, ex: armadilha)
        """
        self.vida_atual -= quantidade
        if self.vida_atual < 0:
            self.vida_atual = 0

        # Inicia o Knockback apenas se houver direção definida
        if direcao_dano != 0:
            self.em_knockback = True
            self.kb_tempo_restante = self.kb_duracao

            # Define a velocidade e a direção do knockback
            self.kb_velocidade = self.FORCA_KB_HORIZONTAL * direcao_dano
            self.vel_y = self.FORCA_KB_VERTICAL  # Joga o Volt para cima

    def coletar_recarga(self, mapa):
        # Este método não precisou de alterações.
        for rec in mapa.recargas[:]:
            if self.rect.colliderect(rec):
                if self.cargas_raio < self.max_cargas_raio:
                    self.cargas_raio += 1
                    mapa.recargas.remove(rec)
                    self.sons.som_Recarga()
                    self.atacando = True
                    self.estado = "recarregando"
                    self.frame_atual = 0

    def draw_raio(self, tela):
        # Este método não precisou de alterações.
        inicio_x = 50
        inicio_y = 50
        espacamento = 35

        for i in range(self.max_cargas_raio):
            pos_x = inicio_x + (i * espacamento)
            if i < self.cargas_raio:
                tela.blit(self.icone_raio_azul, (pos_x, inicio_y))
            else:
                tela.blit(self.icone_raio_cinza, (pos_x, inicio_y))