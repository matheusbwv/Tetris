import pygame

pygame.font.init()


class PauseMenu:
    def __init__(self, win, audio_manager):
        self.win = win
        self.audio = audio_manager
        self.options = [
            "Continuar",
            "Volume Música +",
            "Volume Música -",
            "Volume Efeitos +",
            "Volume Efeitos -",
            "Reiniciar",
            "Voltar ao Menu",
            "Sair"
        ]
        self.selected_index = 0

        # Configurações de fonte e cores
        self.font_title = pygame.font.SysFont('comicsans', 70, bold=True)
        self.font_options = pygame.font.SysFont('comicsans', 45)
        self.bg_color = (0, 0, 0, 180)  # Preto com mais transparência
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 255, 0)  # Amarelo mais vibrante

        # Ajustando o espaçamento e posicionamento
        self.option_spacing = 45  # Reduzido o espaçamento entre opções
        self.title_spacing = 60   # Reduzido o espaço após o título
        self.menu_offset_y = -50  # Deslocamento para cima do menu inteiro

    def draw(self, surface):
        # Overlay semi-transparente
        overlay = pygame.Surface(
            (surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        surface.blit(overlay, (0, 0))

        # Título centralizado (movido para cima)
        title = self.font_title.render('JOGO PAUSADO', True, self.text_color)
        title_rect = title.get_rect(
            center=(surface.get_width()//2,
                    (surface.get_height()//4) + self.menu_offset_y))
        surface.blit(title, title_rect)

        # Opções do menu com melhor espaçamento
        start_y = title_rect.bottom + self.title_spacing

        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_index else self.text_color

            # Adiciona indicador visual para a opção selecionada
            text = f"> {option} <" if i == self.selected_index else option

            label = self.font_options.render(text, True, color)
            label_rect = label.get_rect(
                center=(surface.get_width()//2, start_y + i * self.option_spacing))

            # Adiciona um efeito de sombra suave
            if i == self.selected_index:
                shadow = self.font_options.render(text, True, (100, 100, 100))
                shadow_rect = shadow.get_rect(
                    center=(label_rect.centerx + 2, label_rect.centery + 2))
                surface.blit(shadow, shadow_rect)

            surface.blit(label, label_rect)

        pygame.display.update()

    def handle_volume_adjustment(self, option):
        """Ajusta os volumes conforme a opção selecionada"""
        if option == "Volume Música +":
            new_vol = min(1.0, self.audio.music_volume + 0.1)
            self.audio.set_music_volume(new_vol)
        elif option == "Volume Música -":
            new_vol = max(0.0, self.audio.music_volume - 0.1)
            self.audio.set_music_volume(new_vol)
        elif option == "Volume Efeitos +":
            new_vol = min(1.0, self.audio.effects_volume + 0.1)
            self.audio.set_effects_volume(new_vol)
        elif option == "Volume Efeitos -":
            new_vol = max(0.0, self.audio.effects_volume - 0.1)
            self.audio.set_effects_volume(new_vol)

        # Toca um som de feedback
        self.audio.play_sound('move')

    def run(self, surface):
        clock = pygame.time.Clock()
        paused = True

        while paused:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (
                            self.selected_index - 1) % len(self.options)
                        self.audio.play_sound('move')
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (
                            self.selected_index + 1) % len(self.options)
                        self.audio.play_sound('move')
                    elif event.key == pygame.K_RETURN:
                        selected_option = self.options[self.selected_index]

                        # Opções que retornam uma ação
                        if selected_option == "Continuar":
                            return "continue"
                        elif selected_option == "Reiniciar":
                            return "restart"
                        elif selected_option == "Voltar ao Menu":
                            return "menu"
                        elif selected_option == "Sair":
                            return "quit"
                        # Opções que ajustam volume
                        else:
                            self.handle_volume_adjustment(selected_option)

                    elif event.key == pygame.K_ESCAPE:
                        return "continue"

            self.draw(surface)

        return "continue"
