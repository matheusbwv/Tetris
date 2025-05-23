import pygame
from settings_menu import SettingsMenu # Importe a nova classe
import os # Importar para usar os.path.join

# Definir o caminho para a fonte
FONT_PATH = os.path.join('assets', 'fonts', 'BigBlueTermPlusNerdFont-Regular.ttf') # Verifique o nome exato do arquivo


class MainMenu:
    def __init__(self, win, audio_manager):
        self.win = win
        self.audio = audio_manager
        # Adicione "Configurações" às opções
        self.options = ["Iniciar Jogo", "Configurações", "Sair"]
        self.selected_index = 0
        
        # Usar pygame.font.Font
        try:
            self.font_title = pygame.font.Font(FONT_PATH, 60)
            self.font_options = pygame.font.Font(FONT_PATH, 40)
        except FileNotFoundError:
            print(f"Erro: Fonte não encontrada em {FONT_PATH}. Usando fonte padrão.")
            self.font_title = pygame.font.SysFont('comicsans', 60)
            self.font_options = pygame.font.SysFont('comicsans', 40)
            
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 215, 0)  # Amarelo ouro para seleção
        self.option_spacing = 60
        self.title_pos = (win.get_width() // 2, 150)  # Centralizado horizontalmente
        self.option_start_pos = (win.get_width() // 2, 300)  # Centralizado
        
        # Inicia a música do menu (garantindo que só toque uma vez)
        if not self.audio.is_music_playing() or self.audio.current_track != 'menu':
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
        
        # Instancie o SettingsMenu aqui para que possa ser chamado
        settings_menu = SettingsMenu(self.win, self.audio) 

        while running:
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return False # Retorna False para sair do programa
                
                if event.type == pygame.KEYDOWN: # Verifique se o evento é de tecla pressionada
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                        self.audio.play_sound('move')
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                        self.audio.play_sound('move')
                    elif event.key == pygame.K_RETURN:
                        self.audio.play_sound('drop')
                        if self.selected_index == 0:  # Iniciar Jogo
                            self.audio.stop_music() # Para a música do menu
                            main_function(self.win)  # Executa a função do jogo principal
                            # Após o jogo terminar (e retornar), verifica se a música do menu deve tocar novamente
                            if not self.audio.is_music_playing() or self.audio.current_track != 'menu':
                                self.audio.play_music('menu')
                        elif self.selected_index == 1: # Configurações (novo)
                            # Ao entrar nas configurações, pausa a música do menu (se estiver tocando)
                            self.audio.pause_music() 
                            action = settings_menu.run(self.win) # Chama o menu de configurações
                            # Ao sair das configurações, despausa a música do menu (se estava tocando)
                            if action == "back":
                                self.audio.unpause_music()
                            elif action == "quit": # Se o usuário sair do jogo pelo menu de configurações
                                running = False
                                return False

                        elif self.selected_index == 2:  # Sair (índice ajustado)
                            running = False
                            return False # Retorna False para sair do programa
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        return False # Retorna False para sair do programa
            
            self.draw(self.win)
        
        return False