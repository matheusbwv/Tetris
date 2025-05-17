import pygame

class MainMenu:
    def __init__(self, win, audio_manager):
        self.win = win
        self.audio = audio_manager
        self.options = ["Iniciar Jogo", "Sair"]
        self.selected_index = 0
        self.font_title = pygame.font.SysFont('comicsans', 60)
        self.font_options = pygame.font.SysFont('comicsans', 40)
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 215, 0)  # Amarelo ouro para seleção
        self.option_spacing = 60
        self.title_pos = (win.get_width() // 2, 150)  # Centralizado horizontalmente
        self.option_start_pos = (win.get_width() // 2, 300)  # Centralizado
        
        # Inicia a música do menu
        self.audio.play_music('menu')
    
    def draw(self, surface):
        surface.fill(self.bg_color)
        
        # Desenha título
        title = self.font_title.render('TETRIS', True, self.text_color)
        title_rect = title.get_rect(center=self.title_pos)
        surface.blit(title, title_rect)
        
        # Desenha opções
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_index else self.text_color
            label = self.font_options.render(option, True, color)
            label_rect = label.get_rect(center=(
                self.option_start_pos[0],
                self.option_start_pos[1] + i * self.option_spacing
            ))
            surface.blit(label, label_rect)
        
        pygame.display.update()

    def run(self, main_function):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                        self.audio.play_sound('move')
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                        self.audio.play_sound('move')
                    elif event.key == pygame.K_RETURN:
                        self.audio.play_sound('drop')
                        if self.selected_index == 0:  # Iniciar Jogo
                            self.audio.stop_music()
                            main_function(self.win)  # Executa a função do jogo principal
                            self.audio.play_music('menu')  # Volta ao menu após o jogo
                        elif self.selected_index == 1:  # Sair
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            self.draw(self.win)
        
        pygame.quit()
        return False