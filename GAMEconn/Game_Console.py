import pygame
import serial
import random

# Initialize Pygame and Serial Port
try:
    pygame.init()
    ser = serial.Serial('COM6', 9600, timeout=0)
    print("Pygame and Serial Port initialized successfully.")
except Exception as e:
    print(f"Initialization Error: {e}")
    exit()

# Screen dimensions
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("PYG GAME CONSOLE")

# Load images
try:
    background_img = pygame.image.load('outerspace.jpg').convert()
    spaceship_img = pygame.image.load('spaceship.png').convert_alpha()
    laser_img = pygame.image.load('laser.png').convert_alpha()
    rock_img = pygame.image.load('rock.png').convert_alpha()
    explosion_img = pygame.image.load('explosion.png').convert_alpha()
    # Remove invincible image loading
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    print("Images loaded successfully.")
except Exception as e:
    print(f"Image Loading Error: {e}")
    exit()

# Spaceship properties
spaceship_speed = 400
spaceship = pygame.Rect(WIDTH // 4 - spaceship_img.get_width() // 2,
                        HEIGHT // 2 - spaceship_img.get_height() // 2,
                        spaceship_img.get_width(),
                        spaceship_img.get_height())

# Laser properties
lasers = []
laser_speed = 15

# Rock properties
rocks = []
rock_spawn_rate = 30
rock_fall_speed = 3

# Score properties
score = 0
font = pygame.font.Font(None, 70)
score_font = pygame.font.Font(None, 140)  # Further enlarge font for score

# Invincibility properties
invincible = False
invincible_timer = 0
invincible_cooldown = 0

def activate_invincibility():
    global invincible, invincible_timer, invincible_cooldown
    invincible = True
    invincible_timer = 300  # 5 seconds at 60 FPS
    invincible_cooldown = 900  # 15 seconds at 60 FPS

# FPS
FPS = 60
clock = pygame.time.Clock()

def reset_game():
    global spaceship, lasers, rocks, rock_timer, laser_cooldown, game_over, score
    spaceship.x = WIDTH // 4 - spaceship_img.get_width() // 2
    spaceship.y = HEIGHT // 2 - spaceship_img.get_height() // 2
    lasers.clear()
    rocks.clear()
    rock_timer = 0
    laser_cooldown = 0
    game_over = False
    score = 0
    print("Game reset.")

def draw_skill_cooldown():
    cooldown_radius = 50
    if invincible_cooldown > 0:
        cooldown_percentage = invincible_cooldown / 900
        # Draw outer circle (gray and transparent)
        pygame.draw.circle(screen, (128, 128, 128, 128), (cooldown_radius + 10, cooldown_radius + 10), cooldown_radius)
        # Draw inner circle (gray and low transparency) representing the cooldown
        pygame.draw.circle(screen, (128, 128, 128, 64), (cooldown_radius + 10, cooldown_radius + 10), int(cooldown_radius * (1 - cooldown_percentage)))
        
        # Draw cooldown countdown
        cooldown_time = invincible_cooldown / 60  # Convert frames to seconds
        cooldown_text = pygame.font.Font(None, 50).render(f"{cooldown_time:.1f}", True, (255, 255, 255))
        text_rect = cooldown_text.get_rect(center=(cooldown_radius + 10, cooldown_radius + 10))
        screen.blit(cooldown_text, text_rect)

running = True
paused = False
rock_timer = 0
laser_cooldown = 0
game_over = False

print("Starting game loop.")
while running:
    try:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read data from serial port
        data = ser.read(ser.inWaiting() or 1).decode('utf-8', errors='ignore')
        if data and not game_over:
            try:
                values = [int(value) for value in data.strip().split(',')]
                if len(values) == 8:
                    joystick_x, joystick_y, button_pressed, WHITE_BUTTON, SHOOT_BUTTON, SKILL_BUTTON, RED_BUTTON, GREEN_BUTTON = values

                    if WHITE_BUTTON == 0:
                        if paused:
                            print("Game Resumed")
                            paused = False
                        else:
                            print("Game Paused")
                            paused = True

                    if SKILL_BUTTON == 0 and invincible_cooldown == 0:
                        activate_invincibility()

                    if not paused:
                        # Movement handling
                        spaceship.x -= joystick_x * (spaceship_speed * 0.05)  # Switch left with right
                        spaceship.y -= joystick_y * (spaceship_speed * 0.05)  # Switch up with down

                        # Limit movement within screen boundaries
                        spaceship.x = max(0, min(WIDTH // 2 - spaceship.width, spaceship.x))
                        spaceship.y = max(0, min(HEIGHT - spaceship.height, spaceship.y))

                        # Shoot laser when yellow button is pressed
                        if SHOOT_BUTTON == 0 and laser_cooldown == 0:
                            lasers.append(pygame.Rect(
                                spaceship.centerx + 10, spaceship.centery + spaceship.height // 15, laser_img.get_width(), laser_img.get_height()))
                            laser_cooldown = 10

            except ValueError as e:
                print(f"ValueError: {e}")

        # Pause loop handling for resuming the game
        while paused and not game_over:
            for pause_event in pygame.event.get():
                if pause_event.type == pygame.QUIT:
                    running = False
                    paused = False

            data = ser.read(ser.inWaiting() or 1).decode('utf-8', errors='ignore')
            if data:
                try:
                    values = [int(value) for value in data.strip().split(',')]
                    if len(values) == 8:
                        _, _, _, WHITE_BUTTON, _, _, _, _ = values

                        if WHITE_BUTTON == 0:
                            print("Game Resumed")
                            paused = False

                except ValueError as e:
                    print(f"ValueError: {e}")

            # Display "PAUSED" text
            font = pygame.font.Font(None, 150)  # Enlarge font size
            text = font.render("PAUSED", True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)

            pygame.display.flip()
            clock.tick(FPS)

        # Laser cooldown management
        if laser_cooldown > 0:
            laser_cooldown -= 1

        # Invincibility management
        if invincible:
            invincible_timer -= 1
            if invincible_timer <= 0:
                invincible = False
        if invincible_cooldown > 0:
            invincible_cooldown -= 1

        # Spawn rocks
        rock_timer += 1
        if rock_timer >= rock_spawn_rate and not game_over:
            rock_timer = 0
            rock_size = random.randint(70, 150)  # Random size for the rock between 70x70 and 150x150
            rock_img_resized = pygame.transform.scale(rock_img, (rock_size, rock_size))
            rock_rect = pygame.Rect(WIDTH, random.randint(70, HEIGHT - 70), rock_size, rock_size)
            rock_angle = random.randint(0, 360)
            rocks.append((rock_rect, rock_img_resized, rock_angle))

        # Move rocks and lasers
        for rock in rocks[:]:
            rock_rect, rock_img_resized, rock_angle = rock
            rock_rect.x -= rock_fall_speed
            if rock_rect.x < -rock_rect.width:
                rocks.remove(rock)
                score += 1  # Increase score when rock goes off screen

        for laser in lasers[:]:
            laser.x += laser_speed
            if laser.x > WIDTH:
                lasers.remove(laser)

        # Collision detection for GAME OVER
        for rock in rocks[:]:
            rock_rect, rock_img_resized, rock_angle = rock
            if not invincible and rock_rect.colliderect(spaceship.inflate(-10, -10)):  # Adjust collision detection
                explosion_x = spaceship.centerx - explosion_img.get_width() // 2
                explosion_y = spaceship.centery - explosion_img.get_height() // 2
                screen.blit(explosion_img, (explosion_x, explosion_y))  # Display explosion
                pygame.display.flip()
                pygame.time.delay(500)  # Delay to show explosion
                game_over = True

        for rock in rocks[:]:
            rock_rect, rock_img_resized, rock_angle = rock
            for laser in lasers[:]:
                if rock_rect.colliderect(laser):
                    rocks.remove(rock)
                    lasers.remove(laser)
                    score += 10  # Increase score when rock is destroyed
                    break

        # Drawing elements
        screen.blit(background_img, (0, 0))
        draw_skill_cooldown()
        for rock in rocks:
            rock_rect, rock_img_resized, rock_angle = rock
            rotated_rock_img = pygame.transform.rotate(rock_img_resized, rock_angle)
            screen.blit(rotated_rock_img, (rock_rect.x, rock_rect.y))
        for laser in lasers:
            screen.blit(laser_img, (laser.x, laser.y))
        if invincible:
            spaceship_img.set_alpha(26)  # 10% opacity
        else:
            spaceship_img.set_alpha(255)  # 100% opacity
        screen.blit(spaceship_img, (spaceship.x, spaceship.y))

        # Display score
        score_text = score_font.render(f"{score}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))

        # Display "GAME OVER" if collision happened
        if game_over:
            # Redraw the explosion at the collision point
            screen.blit(explosion_img, (explosion_x, explosion_y))
            font = pygame.font.Font(None, 150)  # Enlarge font size
            text = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            screen.blit(text, text_rect)

            font_small = pygame.font.Font(None, 50)
            continue_text = font_small.render(
                "Do you want to continue?", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(
                center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(continue_text, continue_rect)

            yes_text = font_small.render("YES", True, (0, 255, 0))  # Green color
            no_text = font_small.render("NO", True, (255, 0, 0))  # Red color
            yes_rect = yes_text.get_rect(center=(WIDTH // 2 - 50, HEIGHT // 2 + 50))
            no_rect = no_text.get_rect(center=(WIDTH // 2 + 50, HEIGHT // 2 + 50))
            screen.blit(yes_text, yes_rect)
            screen.blit(no_text, no_rect)

            pygame.display.flip()

            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting_for_input = False

                data = ser.read(ser.inWaiting() or 1).decode(
                    'utf-8', errors='ignore')
                if data:
                    try:
                        values = [int(value) for value in data.strip().split(',')]
                        if len(values) == 8:
                            _, _, _, _, _, _, RED_BUTTON, GREEN_BUTTON = values

                            if RED_BUTTON == 0:
                                running = False
                                waiting_for_input = False

                            if GREEN_BUTTON == 0:
                                reset_game()
                                waiting_for_input = False

                    except ValueError as e:
                        print(f"ValueError: {e}")

                clock.tick(FPS)

        pygame.display.flip()
        clock.tick(FPS)
    except Exception as e:
        print(f"Exception: {e}")
        running = False

ser.close()
pygame.quit()
