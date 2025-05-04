import pygame
import random
import sys

import pygame.display

pygame.init()

menu_options = ["Play", "Leaderboard", "Credits", "Exit"]
selected_option = 0
state = "Menu"

# Configurar pantalla
width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("PapuSnakeGame")

# Colores
Black = (0, 0, 0)
Green = (50, 205, 50)
Red = (255, 0, 0)
White = (255, 255, 255)

# Jugador (serpiente)
cellsize = 20
player = pygame.Rect(300, 200, cellsize, cellsize)
snake = [player.copy()]
velocity = cellsize
direction = "right"

# Comida
food = pygame.Rect(
    random.randint(0, (width - cellsize) // cellsize) * cellsize,
    random.randint(0, (height - cellsize) // cellsize) * cellsize,
    cellsize, cellsize
)

# Reloj de FPS
CLOCK = pygame.time.Clock()

 #Fuente
font = pygame.font.SysFont(None, 48)

#Puntuacion
score = 0

def reset_game():
    global snake, player, direction, food , score
    player = pygame.Rect(300, 200, cellsize, cellsize)
    snake = [player.copy()]
    direction = "right"
    food = pygame.Rect(
        random.randint(0,(width - cellsize) // cellsize) * cellsize,
        random.randint(0, (height - cellsize) // cellsize) * cellsize,
        cellsize, cellsize
    )
    score = 0

#Leaderboard
def load_leaderboard():
    try:
        with open("leaderboard.txt", "r") as f:
            entries = []
            for line in f:
                if ":" in line:
                    parts = line.strip().split(":")
                    if len(parts) == 2 and parts[1].isdigit():
                        entries.append((parts[0], int(parts[1])))
            return entries
    except FileNotFoundError:
        return []

def save_leaderboard(entries):
    with open("leaderboard.txt", "w") as f:
        for name, score in entries:
            f.write(f"{name}:{score}\n")

def update_leaderboard(new_score):
    leaderboard = load_leaderboard()
    if len(leaderboard) < 8 or new_score > leaderboard[-1][1]:
        name = input("New High Score! Enter your name: ")
        leaderboard.append((name, new_score))
        leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)[:8]
        save_leaderboard(leaderboard)

# Bucle principal
running = True
game_over = False
while running:
    CLOCK.tick(10)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if state == "Menu":
                if event.key == pygame.K_UP:
                    selected_option = (selected_option -1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == 1073741912:
                    print("Enter detected")
                    selected = menu_options[selected_option]
                    print(f"Pressed Enter, selected: {selected}")
                    if selected == "Play":
                        state = "Playing"
                        reset_game()
                    elif selected == "Leaderboard":
                        state = "Leaderboard"
                    elif selected == "Credits":
                        state = "Credits"
                    elif selected == "Exit":
                        running = False
            elif state == "Playing":
                    if event.key == pygame.K_LEFT and direction != "right":
                        direction = "left"
                    elif event.key == pygame.K_RIGHT and direction != "left":
                        direction = "right"
                    elif event.key == pygame.K_UP and  direction != "down":
                        direction = "up"
                    elif event.key == pygame.K_DOWN and direction != "up":
                        direction = "down"
            elif state == "Leaderboard":
                        if event.key == pygame.K_ESCAPE:
                            state = "Menu"

    #Draw
    screen.fill(Black)

    if state == "Menu":
        title = font.render("Snake de Papu", True, Green)
        screen.blit(title, (width // 2 - title.get_width() // 2, 50))
        for i, option in enumerate(menu_options):
            color = White if i != selected_option else Red
            text = font.render(option, True, color)
            screen.blit(text, (width // 2 - text.get_width() // 2, 150 + i * 40))
    # Solo mover cuandoestamos playing
    elif state == "Playing":
        if not game_over:
        # Movimiento
            if direction == "left":
                new_head = player.move(-velocity, 0)
            elif direction == "right":
                new_head = player.move(velocity, 0)
            elif direction == "up":
                new_head = player.move(0, -velocity)
            elif direction == "down":
                new_head = player.move(0, velocity)

    # Warp Movement
            if new_head.x >= width:
                new_head.x = 0
            elif new_head.x < 0:
                new_head.x = width - cellsize
            if new_head.y >= height:
                new_head.y = 0
            elif new_head.y < 0:
                new_head.y = height - cellsize

    # Agregar nueva cabeza
            snake.insert(0, new_head)

            if new_head in snake[1:]:
                game_over = True
                update_leaderboard(score)


        # Comer comida o mover
            if new_head.colliderect(food):
                score += 50
                food.x = random.randint(0, (width - cellsize) // cellsize) * cellsize
                food.y = random.randint(0, (height - cellsize) // cellsize) * cellsize
            else:
                snake.pop()
    # Actualizar cabeza
            player = new_head

        for segment in snake:
            pygame.draw.rect(screen, Green, segment)
        pygame.draw.rect(screen, Red, food)
        font_score = pygame.font.SysFont(None, 36)
        score_text = font_score.render(f"Score: {score}", True, White)
        screen.blit(score_text, (10, 10))

        if game_over:
            font_big = pygame.font.SysFont(None, 60)
            game_over_text = font_big.render("Game Over", True, Red)
            screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - game_over_text.get_height() // 2 - 100))

            font_small = pygame.font.SysFont(None, 36)
            restart_text = font_small.render("Press SPACE to restart", True, White)
            screen.blit(restart_text, (width // 2 - restart_text.get_width() // 2, height // 2))

            font_score = pygame.font.SysFont(None, 36)
            score_text = font_score.render(f"Score: {score}", True, White)
            screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2 + 50))
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                update_leaderboard(score)
                reset_game()
                game_over = False

    elif state == "Leaderboard":
                    screen.fill(Black)
                    title = font.render("Leaderboard", True, Green)
                    screen.blit(title, (width // 2 - title.get_width() // 2, 50))

                    leaderboard = load_leaderboard()
                    font_small = pygame.font.SysFont(None, 32)

                    for i, (name, score_value) in enumerate(leaderboard):
                        entry_text = f"{i + 1}. {name} - {score_value}"
                        text = font_small.render(entry_text, True, White)
                        screen.blit(text,(width // 2 - text.get_width() // 2, 120 + i * 30))

                    back_text = font_small.render("Press ESC to return", True, Red)
                    screen.blit(back_text, (width // 2 - back_text.get_width() // 2, height - 50))

    pygame.display.update()
pygame.quit()