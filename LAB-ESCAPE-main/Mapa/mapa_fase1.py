import pygame
import pytmx
from pytmx import TiledTileLayer, TiledObjectGroup, load_pygame

class Map:
    def __init__(self, tmx_path):
        # Carrega TMX 
        self.tmx = load_pygame(tmx_path)

        self.width = self.tmx.width * self.tmx.tilewidth
        self.height = self.tmx.height * self.tmx.tileheight

        # --- Colisões ---
        self.colisoes_parede = []
        camada_col = self.tmx.get_layer_by_name("Colisao")
        for obj in camada_col:
            rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            self.colisoes_parede.append(rect)

        self.armadilhas = []
     
        camada_traps = self.tmx.get_layer_by_name("Trap") 
        for obj in camada_traps:
            rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            self.armadilhas.append(rect)

        self.tempo = 0
    
        self.recargas = [
            pygame.Rect(112, 186, 32, 32),
            pygame.Rect(63, 186, 32, 32),
            pygame.Rect(170, 186, 32, 32),
            pygame.Rect(252, 1113, 32, 32),
            pygame.Rect(1039, 1111, 32, 32),
            pygame.Rect(1891, 1052, 32, 32),
            pygame.Rect(2111, 805, 32, 32)
        ]
        self.sheet_recarga = pygame.image.load("Mapa/Recarga/recarga.png").convert_alpha()
        
        # 2. Configurar o recorte (baseado no tamanho dos seus frames)
        self.frames_recarga = []
        largura_frame = 32  
        altura_frame = 32
        colunas = 15        
        linhas = 2          
        
        # 3. Cortar e guardar na lista
        for y in range(linhas):
            for x in range(colunas):
                # Define a área de corte (x, y, largura, altura)
                rect_corte = (x * largura_frame, y * altura_frame, largura_frame, altura_frame)
                
                try:
                    # Recorta o pedaço da imagem
                    imagem = self.sheet_recarga.subsurface(rect_corte)
                    # Redimensiona para ficar pequeno no mapa (32x32)
                    imagem = pygame.transform.scale(imagem, (32, 32))
                    self.frames_recarga.append(imagem)
                except ValueError:
                    # Caso a imagem acabe antes do esperado, para o loop
                    break

    def draw(self, screen, offset_x, offset_y):
        self.tempo = pygame.time.get_ticks()

        tw = self.tmx.tilewidth
        th = self.tmx.tileheight
        
        sw = screen.get_width()
        sh = screen.get_height()
        
        min_x = (offset_x // tw) - 1
        max_x = ((offset_x + sw) // tw) + 1
        min_y = (offset_y // th) - 1
        max_y = ((offset_y + sh) // th) + 1

        for layer in self.tmx.visible_layers:

            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    if gid == 0:
                        continue
                    if x < min_x or x > max_x or y < min_y or y > max_y:
                        continue

                    props = self.tmx.get_tile_properties_by_gid(gid)
                    frame_gid = gid

                    if props and "frames" in props:
                        frames = props["frames"]
                        total_dur = sum(f[1] for f in frames)
                        t_atual = self.tempo % total_dur

                        acumulado = 0
                        for fgid, dur in frames:
                            acumulado += dur
                            if t_atual < acumulado:
                                frame_gid = fgid
                                break

                    tile = self.tmx.get_tile_image_by_gid(frame_gid)

                    if tile:
                        px = (x * tw) - offset_x
                        py = (y * th) - offset_y
                        screen.blit(tile, (px, py))

            elif isinstance(layer, TiledObjectGroup):
                if layer.name != "Colisao":

                    for obj in layer:

                        if not obj.gid:
                            continue

                        if (obj.x - offset_x) < -200 or (obj.x - offset_x) > sw + 200:
                            continue
                        if (obj.y - offset_y) < -200 or (obj.y - offset_y) > sh + 200:
                            continue

                        props = self.tmx.get_tile_properties_by_gid(obj.gid)
                        frame_gid = obj.gid

                        if props and "frames" in props:
                            frames = props["frames"]
                            total_dur = sum(f[1] for f in frames)
                            t_atual = self.tempo % total_dur

                            acumulado = 0
                            for fgid, dur in frames:
                                acumulado += dur
                                if t_atual < acumulado:
                                    frame_gid = fgid
                                    break

                        tile = self.tmx.get_tile_image_by_gid(frame_gid)

                        if tile:
                            px = obj.x - offset_x
                            py = obj.y - offset_y - tile.get_height()
                            screen.blit(tile, (px, py))

        if len(self.frames_recarga) > 0:
            # Velocidade da animação (quanto menor o número, mais rápido)
            velocidade_animacao = 50 
            
            # Calcula qual quadro mostrar agora
            indice_atual = (self.tempo // velocidade_animacao) % len(self.frames_recarga)
            imagem_animada = self.frames_recarga[indice_atual]

        for rec in self.recargas:
            screen.blit(imagem_animada, (rec.x - offset_x, rec.y - offset_y))

                            