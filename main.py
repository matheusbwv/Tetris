import pygame
import random
from audio_manager import AudioManager
from main_menu import MainMenu
from pause_menu import PauseMenu

pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height
  
      
# SHAPE FORMATS

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape


class Piece(object):  # *
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_pos={}):  # *
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width /2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx+play_width, sy+ i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy),(sx + j*block_size, sy + play_height))


def clear_rows(grid, locked):

    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))


def update_score(nscore):
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


def max_score():
    try:
        with open('scores.txt', 'r') as f:
            lines = f.readlines()
            if len(lines) > 0:
                score = lines[0].strip()
            else:
                score = "0"
    except FileNotFoundError:
        score = "0"
    
    return score


def draw_window(surface, grid, score=0, last_score = 0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))
    # last score
    label = font.render('High Score: ' + last_score, 1, (255,255,255))

    sx = top_left_x - 200
    sy = top_left_y + 150

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)
    #pygame.display.update()


def main(win):
    # Configuração inicial do jogo
    audio.play_music('game')
    pause_menu = PauseMenu(win, audio)
    
    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    
    # Variáveis do jogo
    change_piece = False
    run = True
    paused = False
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
        
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return
            
            if not paused:
                if event.type == pygame.KEYDOWN:
                    # Movimento para esquerda/direita
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                        else:
                            audio.play_sound('move')
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                        else:
                            audio.play_sound('move')
                    
                    # Rotação (cima)
                    elif event.key == pygame.K_UP:
                        current_piece.rotation += 1
                        if not valid_space(current_piece, grid):
                            current_piece.rotation -= 1
                        else:
                            audio.play_sound('rotate')
                    
                    # Pause (tecla P)
                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                        else:
                            audio.play_sound('move')
                    elif event.key == pygame.K_p:
                        paused = True
                        audio.play_sound('pause')
            
            else:  # Se estiver pausado
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    paused = False

        # Lógica do jogo e tocar outros sons...
            if change_piece:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    locked_positions[p] = current_piece.color
                current_piece = next_piece
                next_piece = get_shape()
                change_piece = False
                score += clear_rows(grid, locked_positions) * 10
                audio.play_sound('drop')
            
            draw_window(win, grid, score, last_score)
            draw_next_shape(next_piece, win)
            pygame.display.update()

        rows_cleared = clear_rows(grid, locked_positions)
        if rows_cleared > 0:
            audio.play_sound('clear')
            if rows_cleared >= 4:
                audio.play_sound('rocket')

        # Se o jogo estiver pausado, mostra o menu de pause
        if paused:
            action = pause_menu.run(win)
            
            if action == "continue":
                paused = False
            elif action == "restart":
                return main(win)  # Reinicia o jogo
            elif action == "menu":
                return  # Volta para o menu principal
            elif action == "quit":
                run = False
                pygame.quit()
                return

        if not paused:
            shape_pos = convert_shape_format(current_piece)

            for i in range(len(shape_pos)):
                x, y = shape_pos[i]
                if y > -1:
                    grid[y][x] = current_piece.color

            if change_piece:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    locked_positions[p] = current_piece.color
                current_piece = next_piece
                next_piece = get_shape()
                change_piece = False
                score += clear_rows(grid, locked_positions) * 10

            draw_window(win, grid, score, last_score)
            draw_next_shape(next_piece, win)
            pygame.display.update()

            if check_lost(locked_positions):
                audio.play_sound('game_over')
                draw_text_middle(win, "VOCÊ PERDEU!", 80, (255,255,255))
                pygame.display.update()
                pygame.time.delay(1500)
                update_score(score)
                audio.play_music('menu')
                return
            
def menu(win, game_function):
    run = True
    while run:
        win.fill((0, 0, 0))
        # Título do jogo
        font = pygame.font.SysFont("comicsans", 60)
        label = font.render('TETRIS', 1, (255,255,255))
        win.blit(label, (s_width/2 - label.get_width()/2, s_height/2 - 150))
        
        # Instruções
        font = pygame.font.SysFont("comicsans", 30)
        label = font.render('Pressione qualquer tecla para jogar', 1, (255,255,255))
        win.blit(label, (s_width/2 - label.get_width()/2, s_height/2))
        
        label = font.render('ESC para sair', 1, (255,255,255))
        win.blit(label, (s_width/2 - label.get_width()/2, s_height/2 + 50))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                else:
                    game_function(win)  # Inicia o jogo
                    
    pygame.quit()
    quit()

# No final do arquivo, chame assim:
if __name__ == "__main__":
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')
    
    # Inicializa o AudioManager
    audio = AudioManager()
    
    # Carrega as músicas
    audio.add_music('menu', 'assets/audio/music/main_theme.mp3')
    audio.add_music('game', 'assets/audio/music/game_theme.mp3')
    
    # Carrega efeitos sonoros (usando o AudioManager)
    audio.load_sound('rotate', 'assets/audio/effects/rotate_piece.wav')
    audio.load_sound('move', 'assets/audio/effects/move_piece.wav')
    audio.load_sound('drop', 'assets/audio/effects/piece_landed.wav')
    audio.load_sound('clear', 'assets/audio/effects/line_clear.wav')
    audio.load_sound('level_up', 'assets/audio/effects/level_up_jingle.wav')
    audio.load_sound('game_over', 'assets/audio/effects/game_over.wav')
    audio.load_sound('rocket', 'assets/audio/effects/rocket_ending_sound.wav')
    
    # Inicia música do menu
    audio.play_music('menu')
    
    # Cria e roda o menu principal
    menu = MainMenu(win, audio)
    
    while True:
        should_continue = menu.run(main)
        if not should_continue:
            break