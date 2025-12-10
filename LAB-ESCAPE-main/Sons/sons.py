from PPlay.sound import Sound


class efeitos_sonoros:
    def __init__(self):
        # 🚨 OBSERVAÇÃO: Seu código original não especificava o caminho "Assets/Sons/",
        # então estou usando apenas "Sons/" como no seu código anterior.

        self.musica_fundo = Sound("Sons/alien_superstar.mp3")
        self.musica_fundo.set_volume(30)
        self.musica_fundo.set_repeat(True)

        # 🟢 SOM DE RECARGA (Será usado para menus)
        self.som_recarga = Sound("Sons/som_recarga.mp3")
        self.som_recarga.set_volume(5)
        self.som_recarga.set_repeat(False)

        self.som_poder = Sound("Sons/som_poder.mp3")
        self.som_poder.set_volume(5)
        self.som_poder.set_repeat(False)

        # 💡 DICA: Adicionar um som de morte do inimigo que está faltando no main.py
        # self.som_morte_inimigo = Sound("Sons/som_morte_inimigo.wav")

    def tocar_musica(self):
        self.musica_fundo.play()

    def som_Recarga(self):
        self.som_recarga.play()

    def som_Poder(self):
        self.som_poder.play()

    # Método auxiliar chamado no main.py, que agora usa o som_Recarga
    def tocar_selecao(self):
        self.som_Recarga()

    # Método auxiliar chamado no menu_pause.py, que agora usa o som_Recarga
    def tocar_selecao_ok(self):
        self.som_Recarga()