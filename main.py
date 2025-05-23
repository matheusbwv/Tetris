import pygame
import random
import os

from audio_manager import AudioManager
from main_menu import MainMenu
from pause_menu import PauseMenu
from settings_menu import SettingsMenu

pygame.font.init()

# Definir o caminho para a fonte
FONT_PATH = os.path.join(
    'assets', 'fonts', 'BigBlueTermPlusNerdFont-Regular.ttf')

# GLOBALS VARS
s_width = 1280
s_height = 800

block_size = 30
play_width = 300  # 10 colunas * 30px/coluna
play_height = 600  # 20 linhas * 30px/linha

top_left_x = (s_width - play_width) // 2
top_left_y = (s_height - play_height) // 2

# Wall kick offsets (simplified for basic functionality, not full SRS)
WALL_KICKS = [
    (0, 0),
    (-1, 0),
    (1, 0),
    (-2, 0),
    (2, 0),
    (0, -1),
    (0, -2)
]

# SHAPE FORMATS (permanecem os mesmos)
S = [['.....', '.....', '..00.', '.00..', '.....'],
     ['.....', '..0..', '..00.', '...0.', '.....']]

Z = [['.....', '.00..', '..00.', '.....', '.....'],
     ['.....', '..0..', '.00..', '.0...', '.....']]

I = [['..0..', '..0..', '..0..', '..0..', '.....'],
     ['.....', '0000.', '.....', '.....', '.....']]

O = [['.....', '.....', '.00..', '.00..', '.....']]

J = [['.....', '.0...', '.000.', '.....', '.....'],
     ['.....', '..00.', '..0..', '..0..', '.....'],
     ['.....', '.....', '.000.', '...0.', '.....'],
     ['.....', '..0..', '..0..', '.00..', '.....']]

L = [['.....', '...0.', '.000.', '.....', '.....'],
     ['.....', '..0..', '..0..', '..00.', '.....'],
     ['.....', '.....', '.000.', '.0...', '.....'],
     ['.....', '.00..', '..0..', '..0..', '.....']]

T = [['.....', '..0..', '.000.', '.....', '.....'],
     ['.....', '..0..', '..00.', '..0..', '.....'],
     ['.....', '.....', '.000.', '..0..', '.....'],
     ['.....', '..0..', '.00..', '..0..', '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255),
                (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j, i)]
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


def valid_space(shape, grid, locked_positions):
    """
    Verifica se a posição atual da peça é válida (não colide com paredes, chão ou blocos travados).
    `grid` é usada apenas para suas dimensões. `locked_positions` é a fonte da verdade para blocos ocupados.
    """
    formatted = convert_shape_format(shape)

    for pos in formatted:
        x, y = pos

        if not (0 <= x < 10):
            return False

        if y >= 20:
            return False

        if y >= 0 and (x, y) in locked_positions:
            return False

    return True


def check_lost(positions):
    """Verifica se alguma peça travou acima da área de jogo visível."""
    for pos in positions:
        x, y = pos
        if y < 0:
            return True
    return False


def get_shape():
    """Retorna uma nova peça aleatória."""
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    """Desenha texto centralizado na tela."""
    try:
        font = pygame.font.Font(FONT_PATH, size)
    except FileNotFoundError:
        print(
            f"Erro: Fonte não encontrada em {FONT_PATH}. Usando fonte padrão.")
        font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (s_width / 2 - (label.get_width() / 2),
                 s_height / 2 - label.get_height() / 2))


def clear_rows(grid, locked):
    """
    Remove linhas completas e move os blocos acima para baixo.
    `grid` é usada apenas para suas dimensões (largura/altura).
    A verificação e modificação são feitas em `locked_positions`.
    """
    inc = 0
    full_rows_indices = []

    for i in range(len(grid) - 1, -1, -1):
        is_row_full = True
        for j in range(len(grid[i])):
            if (j, i) not in locked:
                is_row_full = False
                break

        if is_row_full:
            inc += 1
            full_rows_indices.append(i)

            for j in range(len(grid[i])):
                if (j, i) in locked:
                    del locked[(j, i)]

    if inc > 0:
        keys_to_move = []
        for key in locked:
            x, y = key
            lines_to_descend = 0
            for row_idx_cleared in full_rows_indices:
                if y < row_idx_cleared:
                    lines_to_descend += 1

            if lines_to_descend > 0:
                keys_to_move.append(key)

        temp_storage = {}
        for key in keys_to_move:
            color = locked.pop(key)
            x, y = key

            lines_to_descend_final = 0
            for row_idx_cleared in full_rows_indices:
                if y < row_idx_cleared:
                    lines_to_descend_final += 1

            temp_storage[(x, y + lines_to_descend_final)] = color

        locked.update(temp_storage)

    return inc


def draw_next_shape(shape, surface):
    """Desenha a próxima peça no canto superior direito."""
    try:
        font = pygame.font.Font(FONT_PATH, 30)
    except FileNotFoundError:
        print(
            f"Erro: Fonte não encontrada em {FONT_PATH}. Usando fonte padrão.")
        font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Próxima Peça', 1, (255, 255, 255))

    sx_next_shape = top_left_x + play_width + 100
    sy_next_shape = top_left_y + 80

    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                # Desenha a peça com cor sólida
                pygame.draw.rect(surface, shape.color,
                                 (sx_next_shape + j*block_size, sy_next_shape + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx_next_shape + 10, sy_next_shape - 30))


def update_score(nscore):
    """Atualiza o recorde se a nova pontuação for maior."""
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


def max_score():
    """Lê o recorde do arquivo scores.txt."""
    try:
        with open('scores.txt', 'r') as f:
            lines = f.readlines()
            if len(lines) > 0:
                try:
                    score = int(lines[0].strip())
                except ValueError:
                    score = 0
            else:
                score = 0
    except FileNotFoundError:
        score = 0

    return str(score)


def draw_window(surface, grid, current_score, high_score):
    """Desenha todos os elementos do jogo na tela principal."""
    surface.fill((0, 0, 0))  # Preenche o fundo geral da janela com preto

    try:
        font_title = pygame.font.Font(FONT_PATH, 60)
        font_scores = pygame.font.Font(FONT_PATH, 30)
    except FileNotFoundError:
        print(
            f"Erro: Fonte não encontrada em {FONT_PATH}. Usando fonte padrão.")
        font_title = pygame.font.SysFont('comicsans', 60)
        font_scores = pygame.font.SysFont('comicsans', 30)

    # Título do jogo (centralizado na parte superior da tela)
    label_title = font_title.render('TETRIS', 1, (255, 255, 255))
    title_x = s_width / 2 - (label_title.get_width() / 2)
    title_y = 20
    surface.blit(label_title, (title_x, title_y))

    # Pontuação do Jogador (P = <pontos do jogador>)
    label_player_score = font_scores.render(
        f'P = {current_score}', 1, (255, 255, 255))
    sx_player_elements = top_left_x + play_width + 100
    sy_player_score = top_left_y + 250
    surface.blit(label_player_score, (sx_player_elements, sy_player_score))

    # Recorde do Jogo (GR = <recorde atual>)
    label_game_record = font_scores.render(
        f'GR = {high_score}', 1, (255, 255, 255))
    sx_game_record = sx_player_elements
    sy_game_record = sy_player_score + label_player_score.get_height() + 10
    surface.blit(label_game_record, (sx_game_record, sy_game_record))

    # Desenha os blocos coloridos da grade
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            block_color = grid[i][j]
            if block_color != (0, 0, 0):  # Se não for um espaço vazio
                pygame.draw.rect(surface, block_color,
                                 (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    # Desenha as linhas da grade por cima dos blocos
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (top_left_x, top_left_y +
                         i*block_size), (top_left_x+play_width, top_left_y + i*block_size), 1)
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (top_left_x + j*block_size,
                             top_left_y), (top_left_x + j*block_size, top_left_y + play_height), 1)

    # Desenha a borda da área de jogo (a borda vermelha)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x,
                     top_left_y, play_width, play_height), 5)


def draw_game_over_screen(surface, final_score, high_score):
    """Desenha a tela de Game Over."""
    overlay = pygame.Surface((s_width, s_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    try:
        font_game_over = pygame.font.Font(FONT_PATH, 80)
        font_scores = pygame.font.Font(FONT_PATH, 40)
        font_prompt = pygame.font.Font(FONT_PATH, 25)
    except FileNotFoundError:
        print(
            f"Erro: Fonte não encontrada em {FONT_PATH}. Usando fonte padrão.")
        font_game_over = pygame.font.SysFont("comicsans", 80, bold=True)
        font_scores = pygame.font.SysFont("comicsans", 40, bold=True)
        font_prompt = pygame.font.SysFont("comicsans", 25)

    # Título Game Over
    label_game_over = font_game_over.render('GAME OVER', True, (255, 255, 255))
    rect_game_over = label_game_over.get_rect(
        center=(s_width / 2, s_height / 2 - 100))
    surface.blit(label_game_over, rect_game_over)

    # Pontuação Atual
    label_final_score = font_scores.render(
        f'Sua Pontuação: {final_score}', True, (255, 255, 255))
    rect_final_score = label_final_score.get_rect(
        center=(s_width / 2, s_height / 2 - 20))
    surface.blit(label_final_score, rect_final_score)

    # High Score
    label_high_score = font_scores.render(
        f'Recorde: {high_score}', True, (255, 255, 255))
    rect_high_score = label_high_score.get_rect(
        center=(s_width / 2, s_height / 2 + 40))
    surface.blit(label_high_score, rect_high_score)

    # Prompt para o usuário
    label_prompt = font_prompt.render(
        'Pressione ESPAÇO para jogar novamente ou ESC para o menu', True, (200, 200, 200))
    rect_prompt = label_prompt.get_rect(
        center=(s_width / 2, s_height / 2 + 120))
    surface.blit(label_prompt, rect_prompt)

    pygame.display.update()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "restart"
                if event.key == pygame.K_ESCAPE:
                    return "menu"


def main(win):
    audio.play_music('game')
    pause_menu = PauseMenu(win, audio)

    locked_positions = {}
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()

    change_piece = False
    run = True
    paused = False

    fall_time = 0
    level_time = 0
    score = 0

    # Ajustando as velocidades para valores fixos
    # Velocidade inicial mais rápida (menor = mais rápido)
    base_fall_speed = 0.1
    fast_fall_speed = 0.15  # Velocidade após 60 segundos
    soft_drop_multiplier = 0.4

    lock_delay_ms = 500
    lock_delay_start_time = None

    das_delay_ms = 150
    arr_delay_ms = 30

    left_pressed_time = 0
    right_pressed_time = 0

    while run:
        current_time_ms = pygame.time.get_ticks()
        current_high_score_in_game = max_score()

        grid = create_grid(locked_positions)

        shape_pos = convert_shape_format(current_piece)

        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick(60)

        # Modificando o sistema de levels para mudar apenas uma vez após 60 segundos
        if level_time / 1000 > 60:  # 60 segundos
            base_fall_speed = fast_fall_speed
            if not hasattr(main, 'level_up_played'):
                audio.play_sound('level_up')
                main.level_up_played = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if not paused:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid, locked_positions):
                            current_piece.x += 1
                        else:
                            audio.play_sound('move')
                            lock_delay_start_time = None
                        left_pressed_time = current_time_ms

                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid, locked_positions):
                            current_piece.x -= 1
                        else:
                            audio.play_sound('move')
                            lock_delay_start_time = None
                        right_pressed_time = current_time_ms

                    elif event.key == pygame.K_UP:
                        original_rotation = current_piece.rotation
                        original_x = current_piece.x
                        original_y = current_piece.y

                        current_piece.rotation = (
                            current_piece.rotation + 1) % len(current_piece.shape)

                        rotated_successfully = False
                        for dx, dy in WALL_KICKS:
                            current_piece.x = original_x + dx
                            current_piece.y = original_y + dy
                            if valid_space(current_piece, grid, locked_positions):
                                rotated_successfully = True
                                audio.play_sound('rotate')
                                test_piece_below = Piece(
                                    current_piece.x, current_piece.y + 1, current_piece.shape)
                                test_piece_below.rotation = current_piece.rotation
                                if not valid_space(test_piece_below, grid, locked_positions):
                                    lock_delay_start_time = current_time_ms
                                break
                            else:
                                current_piece.x = original_x
                                current_piece.y = original_y

                        if not rotated_successfully:
                            current_piece.rotation = original_rotation
                            current_piece.x = original_x
                            current_piece.y = original_y
                        else:
                            left_pressed_time = 0
                            right_pressed_time = 0

                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid, locked_positions):
                            current_piece.y -= 1
                            if lock_delay_start_time is None:
                                lock_delay_start_time = current_time_ms
                        else:
                            audio.play_sound('move')
                            lock_delay_start_time = None
                            fall_time = 0

                    elif event.key == pygame.K_SPACE:
                        audio.play_sound('drop')
                        while valid_space(current_piece, grid, locked_positions):
                            current_piece.y += 1
                        current_piece.y -= 1
                        change_piece = True
                        lock_delay_start_time = None

                if event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        audio.play_sound('pause')
                        audio.pause_music()
                    else:
                        audio.unpause_music()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    left_pressed_time = 0
                elif event.key == pygame.K_RIGHT:
                    right_pressed_time = 0
                elif event.key == pygame.K_DOWN:
                    pass

        if not paused:
            if left_pressed_time != 0 and current_time_ms - left_pressed_time > das_delay_ms:
                if (current_time_ms - left_pressed_time - das_delay_ms) % arr_delay_ms < (clock.get_rawtime() / 1000 * 1000):
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid, locked_positions):
                        current_piece.x += 1
                    else:
                        audio.play_sound('move')
                        lock_delay_start_time = None

            if right_pressed_time != 0 and current_time_ms - right_pressed_time > das_delay_ms:
                if (current_time_ms - right_pressed_time - das_delay_ms) % arr_delay_ms < (clock.get_rawtime() / 1000 * 1000):
                    current_piece.x += 1
                    if not valid_space(current_piece, grid, locked_positions):
                        current_piece.x -= 1
                    else:
                        audio.play_sound('move')
                        lock_delay_start_time = None

            current_fall_speed = base_fall_speed
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                current_fall_speed *= soft_drop_multiplier

            test_piece_below = Piece(
                current_piece.x, current_piece.y + 1, current_piece.shape)
            test_piece_below.rotation = current_piece.rotation
            can_fall_naturally = valid_space(
                test_piece_below, grid, locked_positions)

            if not can_fall_naturally:
                if lock_delay_start_time is None:
                    lock_delay_start_time = current_time_ms
                elif (current_time_ms - lock_delay_start_time) >= lock_delay_ms:
                    change_piece = True
                    lock_delay_start_time = None
            else:
                lock_delay_start_time = None

                if fall_time/1000 >= current_fall_speed:
                    fall_time = 0
                    current_piece.y += 1
                    if not valid_space(current_piece, grid, locked_positions):
                        current_piece.y -= 1
                        change_piece = True
                        if lock_delay_start_time is None:
                            lock_delay_start_time = current_time_ms
                    else:
                        lock_delay_start_time = None

            temp_grid = [row[:] for row in grid]
            for pos in shape_pos:
                x, y = pos
                if y > -1:
                    temp_grid[y][x] = current_piece.color

            draw_window(win, temp_grid, score, current_high_score_in_game)
            draw_next_shape(next_piece, win)

            if change_piece:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    locked_positions[p] = current_piece.color

                current_piece = next_piece
                next_piece = get_shape()
                change_piece = False

                left_pressed_time = 0
                right_pressed_time = 0

                grid = create_grid(locked_positions)

                rows_cleared = clear_rows(grid, locked_positions)

                if rows_cleared == 1:
                    score += 100
                elif rows_cleared == 2:
                    score += 300
                elif rows_cleared == 3:
                    score += 500
                elif rows_cleared == 4:
                    score += 800
                    audio.play_sound('rocket')

                if rows_cleared > 0:
                    audio.play_sound('clear')

            if check_lost(locked_positions):
                audio.play_sound('game_over')
                update_score(score)
                current_high_score_after_game = max_score()

                action = draw_game_over_screen(
                    win, score, current_high_score_after_game)

                if action == "restart":
                    audio.stop_music()
                    return main(win)
                elif action == "menu":
                    audio.stop_music()
                    return
                elif action == "quit":
                    run = False
        else:  # Se estiver pausado
            audio.pause_music()
            action = pause_menu.run(win)

            if action == "continue":
                paused = False
                audio.unpause_music()
                lock_delay_start_time = None
            elif action == "restart":
                audio.stop_music()
                return main(win)
            elif action == "menu":
                audio.stop_music()
                return
            elif action == "quit":
                run = False

        pygame.display.update()


if __name__ == "__main__":
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')

    # load_block_sprites() # Comentado, pois não usaremos sprites

    audio = AudioManager()

    audio.add_music('menu', 'assets/audio/music/main_theme.mp3')
    audio.add_music('game', 'assets/audio/music/game_theme.mp3')

    audio.load_sound('rotate', 'assets/audio/effects/rotate_piece.wav')
    audio.load_sound('move', 'assets/audio/effects/move_piece.wav')
    audio.load_sound('drop', 'assets/audio/effects/piece_landed.wav')
    audio.load_sound('clear', 'assets/audio/effects/line_clear.wav')
    audio.load_sound('level_up', 'assets/audio/effects/level_up_jingle.wav')
    audio.load_sound('game_over', 'assets/audio/effects/game_over.wav')
    audio.load_sound('rocket', 'assets/audio/effects/rocket_ending_sound.wav')
    audio.load_sound('pause', 'assets/audio/effects/pause_sound.wav')

    main_menu = MainMenu(win, audio)

    while True:
        if not main_menu.run(main):
            break

    pygame.quit()
