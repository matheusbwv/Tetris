import pygame
import os # Importar para usar os.path.join

pygame.font.init()

# Definir o caminho para a fonte
FONT_PATH = os.path.join('assets', 'fonts', 'BigBlueTermPlusNerdFont-Regular.ttf') # Verifique o nome exato do arquivo

class SettingsMenu:
    def __init__(self, win, audio_manager):
        self.win = win
        self.audio = audio_manager
        self.options = [
            "Volume Música: {:.0%}".format(self.audio.music_volume),
            "Volume Efeitos: {:.0%}".format(self.audio.effects_volume),
            "Voltar"
        ]
        self.selected_index = 0

        # Usar pygame.font.Font
        try:
            self.font_title = pygame.font.Font(FONT_PATH, 70)
            self.font_options = pygame.font.Font(FONT_PATH, 45)
        except FileNotFoundError:
            print(f"Erro: Fonte não encontrada em {FONT_PATH}. Usando fonte padrão.")
            self.font_title = pygame.font.SysFont('comicsans', 70, bold=True)
            self.font_options = pygame.font.SysFont('comicsans', 45)

        self.bg_color = (0, 0, 0, 180) # Preto com transparência
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 255, 0) # Amarelo vibrante

        self.option_spacing = 50
        self.title_spacing = 80
        self.menu_offset_y = -30

    def update_volume_options(self):
        # Atualiza os textos de volume para refletir os valores atuais
        self.options[0] = "Volume Música: {:.0%}".format(self.audio.music_volume)
        self.options[1] = "Volume Efeitos: {:.0%}".format(self.audio.effects_volume)

    def draw(self, surface):
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        surface.blit(overlay, (0, 0))

        title = self.font_title.render('CONFIGURAÇÕES', True, self.text_color)
        title_rect = title.get_rect(center=(surface.get_width()//2, (surface.get_height()//4) + self.menu_offset_y))
        surface.blit(title, title_rect)

        start_y = title_rect.bottom + self.title_spacing

        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_index else self.text_color
            text = f"> {option} <" if i == self.selected_index else option
            label = self.font_options.render(text, True, color)
            label_rect = label.get_rect(center=(surface.get_width()//2, start_y + i * self.option_spacing))

            if i == self.selected_index:
                shadow = self.font_options.render(text, True, (100, 100, 100))
                shadow_rect = shadow.get_rect(center=(label_rect.centerx + 2, label_rect.centery + 2))
                surface.blit(shadow, shadow_rect)

            surface.blit(label, label_rect)
        pygame.display.update()

    def run(self, surface):
        clock = pygame.time.Clock()
        in_settings = True

        while in_settings:
            clock.tick(60)
            self.update_volume_options() # Atualiza os textos de volume a cada frame

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                if event.type == pygame.KEYDOWN: # Garante que só verifica event.key em eventos KEYDOWN
                    self.audio.play_sound('move') # Som ao navegar no menu
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_KP_MINUS: # Tecla esquerda ou '-' do teclado numérico
                        if self.selected_index == 0: # Volume Música
                            new_vol = max(0.0, self.audio.music_volume - 0.1)
                            self.audio.set_music_volume(new_vol)
                        elif self.selected_index == 1: # Volume Efeitos
                            new_vol = max(0.0, self.audio.effects_volume - 0.1)
                            self.audio.set_effects_volume(new_vol)
                        self.audio.play_sound('drop') # Som de ajuste de volume
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP_PLUS: # Tecla direita ou '+' do teclado numérico
                        if self.selected_index == 0: # Volume Música
                            new_vol = min(1.0, self.audio.music_volume + 0.1)
                            self.audio.set_music_volume(new_vol)
                        elif self.selected_index == 1: # Volume Efeitos
                            new_vol = min(1.0, self.audio.effects_volume + 0.1)
                            self.audio.set_effects_volume(new_vol)
                        self.audio.play_sound('drop') # Som de ajuste de volume
                    elif event.key == pygame.K_RETURN:
                        self.audio.play_sound('drop') # Som de seleção
                        if self.selected_index == 2: # Voltar
                            in_settings = False
                    elif event.key == pygame.K_ESCAPE:
                        in_settings = False # Volta com ESC

            self.draw(surface)
        return "back" # Retorna para o MainMenu