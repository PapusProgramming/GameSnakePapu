import pygame
import random
import sys

pygame.init()

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

# Bucle principal
running = True
game_over = False
while running:
    CLOCK.tick(10)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and direction != "right":
                direction = "left"
            elif event.key == pygame.K_RIGHT and direction != "left":
                direction = "right"
            elif event.key == pygame.K_UP and direction != "down":
                direction = "up"
            elif event.key == pygame.K_DOWN and direction != "up":
                direction = "down"

    # Movimiento de la cabeza
    if game_over:
        screen.fill(Black)
        font_big = pygame.font.SysFont(None, 60)
        game_over_text = font_big.render("Game Over", True, Red)
        screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - 40))

        font_small = pygame.font.SysFont(None, 36)
        score_text = font_small.render(f"Score: {score}", True, (255,255,255))
        screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2 + 10))

        instructions = font_small.render("Press SPACE to restart", True, White)
        screen.blit(instructions, (width // 2 - instructions.get_width() // 2, height // 2 + 50))

        pygame.display.update()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            reset_game()
            score = 0
            game_over = False
        continue #Salta todo si estamos game over

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


        # Comer comida o mover
    if new_head.colliderect(food):
        score += 50
        food.x = random.randint(0, (width - cellsize) // cellsize) * cellsize
        food.y = random.randint(0, (height - cellsize) // cellsize) * cellsize
        
    else:
        snake.pop()

    # Actualizar cabeza
    player = new_head

    # Dibujar todo
    screen.fill(Black)
    font = pygame.font.SysFont(None, 30)
    score_text = font.render("Score: " + str(score), True, White)
    screen.blit(score_text, (10, 10))
    pygame.draw.rect(screen, Red, food)
    for segment in snake:
        pygame.draw.rect(screen, Green, segment)

    pygame.display.update()
pygame.quit()
