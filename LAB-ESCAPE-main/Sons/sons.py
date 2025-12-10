from PPlay.sound import Sound

class efeitos_sonoros:
    def __init__(self):
        self.musica_fundo = Sound("Sons/alien_superstar.mp3")
        self.musica_fundo.set_volume(30)
        self.musica_fundo.set_repeat(True)

        self.som_recarga = Sound("Sons/som_recarga.mp3")
        self.som_recarga.set_volume(5)
        self.som_recarga.set_repeat(False)

        self.som_poder = Sound("Sons/som_poder.mp3")
        self.som_poder.set_volume(5)
        self.som_poder.set_repeat(False)

    def tocar_musica(self):
        self.musica_fundo.play()
    def som_Recarga(self):
        self.som_recarga.play()
    def som_Poder(self):
        self.som_poder.play()
