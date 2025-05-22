#disallow duplicates on leaderboard
#use right leaderboard
#global variable for enter key

#!/usr/bin/env python3

import pygame
import random
import sys
import os

pygame.init()

menu_options = ["Play", "Leaderboard", "Credits", "Exit"]
selected_option = 0
state = "Menu"
input_name = ""
name_enter_active = False
new_high_score = False

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
speed_level = 1

# Comida
food = pygame.Rect(
    random.randint(0, (width - cellsize) // cellsize) * cellsize,
    random.randint(0, (height - cellsize) // cellsize) * cellsize,
    cellsize, cellsize
)

# Reloj de FPS
CLOCK = pygame.time.Clock()

# Fuente
font = pygame.font.SysFont(None, 48)

# Main game velocity
fps = 10

# Puntuacion
score = 0

def update_speed():
    global fps
    fps = 10 + (score // 1000) * 2

def reset_game():
    global snake, player, direction, food, score
    player = pygame.Rect(300, 200, cellsize, cellsize)
    snake = [player.copy()]
    direction = "right"
    food.x = random.randint(0, (width - cellsize) // cellsize) * cellsize
    food.y = random.randint(0, (height - cellsize) // cellsize) * cellsize
    score = 0

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

def update_leaderboard(name, new_score):
    leaderboard = load_leaderboard()
    leaderboard.append((name, new_score))
    leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)[:8]
    save_leaderboard(leaderboard)

def check_high_score(new_score):
    leaderboard = load_leaderboard()
    return len(leaderboard) < 8 or new_score > leaderboard[-1][1]

def get_highest_score():
    leaderboard = load_leaderboard()
    if leaderboard:
        return max(score for _, score in leaderboard)
    return 0

highest_score = get_highest_score()

# Get path to this script's directory
base_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_dir, "papusprogramming.png")  # Make sure this file is in the same directory

# Load and scale the intro image
intro_image = pygame.image.load(image_path)
intro_image = pygame.transform.scale(intro_image, (550, 350))

def show_intro():
    image_rect = intro_image.get_rect(center=(width // 2, height // 2))
    screen.blit(intro_image, image_rect.topleft)
    pygame.display.update()
    start_time = pygame.time.get_ticks()
    showing = True
    while showing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if pygame.time.get_ticks() - start_time > 3000:
            showing = False



# Bucle principal
show_intro()
running = True
game_over = False

while running:
    CLOCK.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if state == "Menu":
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN or event.key == 1073741912:
                    selected = menu_options[selected_option]
                    if selected == "Play":
                        state = "Playing"
                        reset_game()
                        game_over = False
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
                elif event.key == pygame.K_UP and direction != "down":
                    direction = "up"
                elif event.key == pygame.K_DOWN and direction != "up":
                    direction = "down"

            elif state == "Credits" and event.key == pygame.K_ESCAPE:
                state = "Menu"

            elif state == "Leaderboard" and event.key == pygame.K_ESCAPE:
                state = "Menu"

            elif state == "EnterName":
                if event.key == pygame.K_RETURN or event.key == 1073741912 and input_name:
                    update_leaderboard(input_name, score)
                    input_name = ""
                    new_high_score = False
                    highest_score = get_highest_score()
                    state = "Leaderboard"
                elif event.key == pygame.K_BACKSPACE:
                    input_name = input_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    input_name = ""
                    new_high_score = False
                    state = "Menu"
                else:
                    if len(input_name) < 10:
                        char = event.unicode
                        if char.isalnum() or char in " _-":
                            input_name += char

    # Game logic
    if state == "Playing" and not game_over:
        if direction == "left":
            new_head = player.move(-velocity, 0)
        elif direction == "right":
            new_head = player.move(velocity, 0)
        elif direction == "up":
            new_head = player.move(0, -velocity)
        elif direction == "down":
            new_head = player.move(0, velocity)

        # Warp
        new_head.x %= width
        new_head.y %= height

        snake.insert(0, new_head)

        if new_head in snake[1:]:
            game_over = True
            if check_high_score(score):
                if score > highest_score:
                    new_high_score = True
                state = "EnterName"
                input_name = ""
            else:
                state = "GameOver"

        if new_head.colliderect(food):
            score += 50
            update_speed()
            food.x = random.randint(0, (width - cellsize) // cellsize) * cellsize
            food.y = random.randint(0, (height - cellsize) // cellsize) * cellsize
        else:
            snake.pop()

        player = new_head

    # Draw everything
    screen.fill(Black)

    if state == "Menu":
        title = font.render("Snake de Papu", True, Green)
        screen.blit(title, (width // 2 - title.get_width() // 2, 50))
        for i, option in enumerate(menu_options):
            color = Red if i == selected_option else White
            text = font.render(option, True, color)
            screen.blit(text, (width // 2 - text.get_width() // 2, 150 + i * 40))

    elif state == "Credits":
        title = font.render("Credits", True, Green)
        screen.blit(title, (width // 2 - title.get_width() // 2, 50))
        credit = pygame.font.SysFont(None, 32).render("Made by PapusProgramming", True, Red)
        screen.blit(credit, (width // 2 - credit.get_width() // 2, height // 2))
        esc = pygame.font.SysFont(None, 32).render("Press ESC to Return", True, White)
        screen.blit(esc, (width // 2 - esc.get_width() // 2, height - 50))

    elif state == "Playing":
        for segment in snake:
            pygame.draw.rect(screen, Green, segment)
        pygame.draw.rect(screen, Red, food)
        s_text = pygame.font.SysFont(None, 36).render(f"Score: {score}", True, White)
        screen.blit(s_text, (10, 10))

    elif state == "GameOver":
        go_font = pygame.font.SysFont(None, 60)
        go_text = go_font.render("Game Over", True, Red)
        screen.blit(go_text, (width // 2 - go_text.get_width() // 2, height // 2 - 100))

        font_small = pygame.font.SysFont(None, 36)
        restart = font_small.render("Press SPACE to Restart", True, White)
        esc = font_small.render("Press ESC to Main Menu", True, Red)
        s_text = font_small.render(f"Score: {score}", True, White)

        screen.blit(restart, (width // 2 - restart.get_width() // 2, height // 2))
        screen.blit(esc, (width // 2 - esc.get_width() // 2, height // 2 + 40))
        screen.blit(s_text, (width // 2 - s_text.get_width() // 2, height // 2 + 80))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            reset_game()
            game_over = False
            state = "Playing"
        elif keys[pygame.K_ESCAPE]:
            reset_game()
            game_over = False
            state = "Menu"

    elif state == "EnterName":
        if new_high_score:
            prompt = font.render("🔥 New All-Time High Score! 🔥", True, Red)
        else:
            prompt = font.render("New High Score!", True, Green)

        screen.blit(prompt, (width // 2 - prompt.get_width() // 2, 50))

        entry_prompt = pygame.font.SysFont(None, 32).render("Enter your name:", True, White)
        screen.blit(entry_prompt, (width // 2 - entry_prompt.get_width() // 2, 120))

        entry_box = pygame.font.SysFont(None, 40).render(input_name, True, Red)
        screen.blit(entry_box, (width // 2 - entry_box.get_width() // 2, 160))

        inst = pygame.font.SysFont(None, 24).render("Press Enter to save, ESC to cancel", True, White)
        screen.blit(inst, (width // 2 - inst.get_width() // 2, height - 40))

    elif state == "Leaderboard":
        title = font.render("Leaderboard", True, Green)
        screen.blit(title, (width // 2 - title.get_width() // 2, 50))

        leaderboard = load_leaderboard()
        font_small = pygame.font.SysFont(None, 32)

        for i, (name, score_value) in enumerate(leaderboard):
            rank_text = font_small.render(f"{i + 1}. {name}", True, White)
            score_text = font_small.render(str(score_value), True, White)
            y = 120 + i * 30
            screen.blit(rank_text, (50, y))
            screen.blit(score_text, (400, y))

        back = font_small.render("Press ESC to Return", True, Red)
        screen.blit(back, (width // 2 - back.get_width() // 2, height - 40))

    pygame.display.update()

pygame.quit()
