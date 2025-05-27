#!/usr/bin/env python3

import pygame
import random
import sys
import os
import requests

music_muted = False
sound_effects_enabled = True
paused_option = 0
pause_menu_options = ["Resume", "Toggle Sound Effects", "Toggle Music", "Main Menu"]

pygame.init()

menu_options = ["Play", "Leaderboard", "Credits", "Exit"]
selected_option = 0
state = "Menu"
input_name = ""
name_enter_active = False
new_high_score = False

width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("PapuSnakeGame")

Black = (0, 0, 0)
Green = (50, 205, 50)
Red = (255, 0, 0)
White = (255, 255, 255)

cellsize = 20
player = pygame.Rect(300, 200, cellsize, cellsize)
snake = [player.copy()]
velocity = cellsize
direction = "right"
next_direction = direction
speed_level = 1

food = pygame.Rect(
    random.randint(0, (width - cellsize) // cellsize) * cellsize,
    random.randint(0, (height - cellsize) // cellsize) * cellsize,
    cellsize, cellsize
)

CLOCK = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
fps = 10
score = 0

def update_speed():
    global fps
    fps = 10 + (score // 1000) * 2

def reset_game():
    global snake, player, direction, next_direction, food, score
    player = pygame.Rect(300, 200, cellsize, cellsize)
    snake = [player.copy()]
    direction = "right"
    next_direction = direction
    food.x = random.randint(0, (width - cellsize) // cellsize) * cellsize
    food.y = random.randint(0, (height - cellsize) // cellsize) * cellsize
    score = 0

FIREBASE_DB_URL = "https://papusnakeleaderboard-default-rtdb.firebaseio.com/"

def load_leaderboard():
    try:
        res = requests.get(f"{FIREBASE_DB_URL}/scores.json")
        if res.status_code == 200 and res.json():
            data = res.json()
            entries = [(v["name"], v["score"]) for v in data.values()]
            return sorted(entries, key=lambda x: x[1], reverse=True)[:8]
    except Exception as e:
        print("Failed to load leaderboard:", e)
    return []

base_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(base_dir, "papusprogramming.png")

def update_leaderboard(name, new_score):
    leaderboard = load_leaderboard()
    if len(leaderboard) < 8 or new_score > leaderboard[-1][1]:
        try:
            data = {"name": name, "score": new_score}
            requests.post(f"{FIREBASE_DB_URL}/scores.json", json=data)
        except Exception as e:
            print("Failed to update leaderboard:", e)

def check_high_score(new_score):
    leaderboard = load_leaderboard()
    return len(leaderboard) < 8 or new_score > leaderboard[-1][1]

def get_highest_score():
    leaderboard = load_leaderboard()
    if leaderboard:
        return max(score for _, score in leaderboard)
    return 0

highest_score = get_highest_score()

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
        if pygame.time.get_ticks() - start_time > 2000:
            showing = False

pygame.mixer.init()

background_music_path = os.path.join(base_dir, "background.wav")
eat_sound = pygame.mixer.Sound(os.path.join(base_dir, "eat.wav"))
death_sound = pygame.mixer.Sound(os.path.join(base_dir, "death.wav"))

pygame.mixer.music.load(background_music_path)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

show_intro()
running = True
game_over = False

# Zoom-in animation function for Game Over text
def game_over_zoom_in_animation():
    base_font = pygame.font.SysFont(None, 60)
    max_size = 100
    min_size = 20
    steps = 15
    for step in range(steps):
        size = min_size + (max_size - min_size) * (step / (steps - 1))
        font_zoom = pygame.font.SysFont(None, int(size))
        text = font_zoom.render("Game Over", True, Red)
        screen.fill(Black)
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
        pygame.display.update()
        pygame.time.delay(50)

# Add a flag attribute to remember if animation ran
game_over_zoom_in_animation.done = False

while running:
    CLOCK.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                if state in ("Playing", "GameOver"):
                    reset_game()
                    state = "Menu"
                    game_over = False
                    game_over_zoom_in_animation.done = False  # Reset animation flag on quit
                elif state == "Leaderboard":
                    pass
                elif state == "Credits":
                    pass
                else:
                    running = False

            if event.key == pygame.K_m and state not in ("EnterName",):
                music_muted = not music_muted
                pygame.mixer.music.set_volume(0 if music_muted else 0.5)

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
                        game_over_zoom_in_animation.done = False
                    elif selected == "Leaderboard":
                        state = "Leaderboard"
                    elif selected == "Credits":
                        state = "Credits"
                    elif selected == "Exit":
                        running = False

            elif state == "Playing":
                if event.key == pygame.K_LEFT and direction != "right":
                    next_direction = "left"
                elif event.key == pygame.K_RIGHT and direction != "left":
                    next_direction = "right"
                elif event.key == pygame.K_UP and direction != "down":
                    next_direction = "up"
                elif event.key == pygame.K_DOWN and direction != "up":
                    next_direction = "down"
                elif event.key == pygame.K_p:
                    state = "Paused"

            elif state == "Paused":
                if event.key == pygame.K_UP:
                    paused_option = (paused_option - 1) % len(pause_menu_options)
                elif event.key == pygame.K_DOWN:
                    paused_option = (paused_option + 1) % len(pause_menu_options)
                elif event.key == pygame.K_RETURN or event.key == 1073741912:
                    selected = pause_menu_options[paused_option]
                    if selected == "Resume":
                        for i in range (3, 0, -1):
                            screen.fill(Black)
                            countdown = font.render(str(i), True, White)
                            screen.blit(countdown, (width // 2 - countdown.get_width() // 2, height // 2))
                            pygame.display.update()
                            pygame.time.delay(1000)
                        state = "Playing"
                    elif selected == "Toggle Sound Effects":
                        sound_effects_enabled = not sound_effects_enabled
                    elif selected == "Toggle Music":
                        music_muted = not music_muted
                        pygame.mixer.music.set_volume(0 if music_muted else 0.5)
                    elif selected == "Main Menu":
                        reset_game()
                        state = "Menu"
                        game_over_zoom_in_animation.done = False

            elif state == "Credits" and event.key == pygame.K_ESCAPE:
                state = "Menu"

            elif state == "Leaderboard" and event.key == pygame.K_ESCAPE:
                state = "Menu"

            elif state == "EnterName":
                if (event.key == pygame.K_RETURN or event.key == 1073741912) and input_name:
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

    if state == "Playing" and not game_over:
        direction = next_direction

        if direction == "left":
            new_head = player.move(-velocity, 0)
        elif direction == "right":
            new_head = player.move(velocity, 0)
        elif direction == "up":
            new_head = player.move(0, -velocity)
        elif direction == "down":
            new_head = player.move(0, velocity)

        new_head.x %= width
        new_head.y %= height

        snake.insert(0, new_head)

        if new_head in snake[1:]:
            if sound_effects_enabled:
                death_sound.play()
            game_over = True
            if check_high_score(score):
                if score > highest_score:
                    new_high_score = True
                state = "EnterName"
                input_name = ""
            else:
                state = "GameOver"
                game_over_zoom_in_animation.done = False  # Reset animation flag when first entering GameOver

        if new_head.colliderect(food):
            if sound_effects_enabled:
                eat_sound.play()
            score += 50
            update_speed()
            food.x = random.randint(0, (width - cellsize) // cellsize) * cellsize
            food.y = random.randint(0, (height - cellsize) // cellsize) * cellsize
        else:
            snake.pop()

        player = new_head

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

    elif state == "Paused":
        pause_title = font.render("Game Paused", True, Green)
        screen.blit(pause_title, (width // 2 - pause_title.get_width() // 2, 50))

        for i, option in enumerate(pause_menu_options):
            label = option
            if option == "Toggle Sound Effects":
                label += f" ({'On' if sound_effects_enabled else 'Off'})"
            if option == "Toggle Music":
                label += f" ({'Off' if music_muted else 'On'})"
            color = Red if i == paused_option else White
            text = pygame.font.SysFont(None, 36).render(label, True, color)
            screen.blit(text, (width // 2 - text.get_width() // 2, 150 + i * 40))

    elif state == "Playing":
        for segment in snake:
            pygame.draw.rect(screen, Green, segment)
        pygame.draw.rect(screen, Red, food)
        s_text = pygame.font.SysFont(None, 36).render(f"Score: {score}", True, White)
        screen.blit(s_text, (10, 10))
        mute_status = pygame.font.SysFont(None, 24).render("Muted" if music_muted else "Press M to Mute", True, White)
        screen.blit(mute_status, (width - mute_status.get_width() - 10, 10))
        pause_status = pygame.font.SysFont(None, 24).render("Press P to Pause", True, White)
        screen.blit(pause_status, (width - pause_status.get_width() - 10, 30))
        quit_msg = pygame.font.SysFont(None, 24).render("Press Q for Main Menu", True, White)
        screen.blit(quit_msg, (width // 2 - quit_msg.get_width() // 2, 10))

    elif state == "GameOver":
        # Run zoom-in animation once
        if not game_over_zoom_in_animation.done:
            game_over_zoom_in_animation.done = True
            game_over_zoom_in_animation()

        # Draw "Game Over" in red at fixed size near the top
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("Game Over", True, Red)
        screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - 100))

        # Show prompt text below the Game Over text
        prompt_font = pygame.font.SysFont(None, 36)
        prompt_text = prompt_font.render("Press Enter to Restart or Q for Main Menu", True, White)
        screen.blit(prompt_text, (width // 2 - prompt_text.get_width() // 2, height // 2))

        # Check for input here (also handled in event loop)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] or keys[1073741912]:
            reset_game()
            state = "Playing"
            game_over = False
            game_over_zoom_in_animation.done = False
        elif keys[pygame.K_q]:
            reset_game()
            state = "Menu"
            game_over = False
            game_over_zoom_in_animation.done = False


    elif state == "Leaderboard":
        title = font.render("Leaderboard", True, Green)
        screen.blit(title, (width // 2 - title.get_width() // 2, 50))
        leaderboard = load_leaderboard()
        for i, (name, scr) in enumerate(leaderboard):
            entry = pygame.font.SysFont(None, 32).render(f"{i+1}. {name} - {scr}", True, White)
            screen.blit(entry, (width // 2 - entry.get_width() // 2, 100 + i * 30))
        esc = pygame.font.SysFont(None, 24).render("Press ESC to Return", True, Red)
        screen.blit(esc, (width // 2 - esc.get_width() // 2, height - 50))

    elif state == "EnterName":
        prompt = font.render("New High Score! Enter your name:", True, Green)
        screen.blit(prompt, (width // 2 - prompt.get_width() // 2, 100))
        name_surface = font.render(input_name, True, White)
        screen.blit(name_surface, (width // 2 - name_surface.get_width() // 2, 150))
        esc = pygame.font.SysFont(None, 24).render("Press ESC to Cancel", True, White)
        screen.blit(esc, (width // 2 - esc.get_width() // 2, height - 50))

    pygame.display.update()

pygame.quit()
