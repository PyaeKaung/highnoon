import pygame
import random

# Constants
WIDTH, HEIGHT = 1600, 800
PLAYER_WIDTH, PLAYER_HEIGHT = 152, 128
MAX_SPEED = 14
ACCELERATION = 10
FRICTION = 1
JUMP = 30
GRAVITY = 2
DASH_SPEED = 38
DASH_DURATION = 0.2
DASH_COOLDOWN = 1.5
ANIMATION_SPEED = 77
PROJECTILE_COOLDOWN = 0.30 

# Initializing Pygame
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("High Noon")

# Loading background and gameover
BG = pygame.transform.scale(pygame.image.load("bg.png"), (WIDTH, HEIGHT))
GAME_OVER_IMAGE = pygame.image.load("gameover.png")
SPLASH_IMAGE = pygame.transform.scale(pygame.image.load("Flash.png"), (WIDTH, HEIGHT))

# Loading in Sprites
PLAYER_SPRITES = [
    pygame.image.load(f"playeranims\\sp{i}.png")
    for i in range(1, 7)
]

ENEMY_SPRITES = [
    pygame.transform.scale(pygame.image.load(f"zombieanim\\z{i}.png"), (80, 180))
    for i in range(1, 10)
]

RUNNING_SPRITES = [
    pygame.image.load(f"Runanimation\\run{i}.png")
    for i in range(1, 12)
]

PROJECTILE_SPRITE = pygame.transform.scale(pygame.image.load("Bullet.png"), (60, 30))

# Bringing to life the zombies
class Enemy:
    def __init__(self, x, y, enemy_speed):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 180
        self.max_speed = enemy_speed
        self.acceleration = 0.5 
        self.velocity = 0  
        self.y_velocity = 0  
        self.on_ground = True 
        self.jump_timer = random.uniform(0.5, 2)  
        self.animation_frame = 0  
        self.last_frame_time = pygame.time.get_ticks()  
        self.ANIMATION_SPEED = 100  
        self.facing_right = False  

    def move_towards_player(self, player, clock):
        self.jump_timer -= clock.get_time() / 1000

        # Jump logic
        if self.jump_timer <= 0 and self.on_ground:
            self.y_velocity = -JUMP
            self.on_ground = False
            self.jump_timer = random.uniform(1, 2)

        # Apply gravity
        if not self.on_ground:
            self.y_velocity += GRAVITY
            
        self.y += self.y_velocity

        # Ground collision
        if self.y >= (HEIGHT - PLAYER_HEIGHT) - 130:
            self.y = (HEIGHT - PLAYER_HEIGHT) - 130
            self.on_ground = True
            self.y_velocity = 0

        # Moving towards player
        if self.x < player.x:
            self.velocity += self.acceleration
            self.facing_right = True
        elif self.x > player.x:
            self.velocity -= self.acceleration
            self.facing_right = False

        self.velocity = max(-self.max_speed, min(self.max_speed, self.velocity))
        self.x += self.velocity

        # Animation
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_time >= self.ANIMATION_SPEED:
            self.animation_frame = (self.animation_frame + 1) % len(ENEMY_SPRITES)
            self.last_frame_time = current_time

    def draw(self, surface):
        sprite = ENEMY_SPRITES[self.animation_frame]
        if self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (self.x, self.y))

# Bullet properties
class Projectile:
    def __init__(self, x, y, facing_left):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 15
        self.speed = 30  
        self.facing_left = facing_left
        self.image = PROJECTILE_SPRITE

    def move(self):
        if self.facing_left:
            self.x -= self.speed
        else:
            self.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

def draw_hp_bar(surface, hp, max_hp):
    bar_width = 400
    bar_height = 40
    x = 50
    y = 30

    pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))

    hp_ratio = hp / max_hp
    pygame.draw.rect(surface, (0, 255, 0), (x, y, bar_width * hp_ratio, bar_height))
    
# Draw
def draw(player, current_sprite, facing_left, enemies, projectiles, player_hp, score, font):
    WIN.blit(BG, (0, 0))
    flipped_sprite = pygame.transform.flip(current_sprite, True, False) if not facing_left else current_sprite
    WIN.blit(flipped_sprite, (player.x, player.y))
    for enemy in enemies:
        enemy.draw(WIN)

    # Projectiles
    for projectile in projectiles:
        projectile.draw(WIN)

    # Hp bar
    draw_hp_bar(WIN, player_hp, 150)

    # Score
    score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
    WIN.blit(score_surface, (WIDTH - score_surface.get_width() - 50, 10))

    pygame.display.update()

def game_over():
    while True:
        WIN.blit(GAME_OVER_IMAGE, (0, 0))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()  # Restart the game

def main():
    run = True
    player = pygame.Rect(700, (HEIGHT - PLAYER_HEIGHT) - 80, PLAYER_WIDTH, PLAYER_HEIGHT)
    pygame.font.init()
    font = pygame.font.Font(None, 36)
    score = 0
    enemies = []

    clock = pygame.time.Clock()

    # Brief manual
    def show_splash_screen():
        start_time = pygame.time.get_ticks()
        splash_duration = 5000

        while pygame.time.get_ticks() - start_time < splash_duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            WIN.blit(SPLASH_IMAGE, (0, 0))
            pygame.display.update()
            clock.tick(60)

    show_splash_screen()

    # Zombie spawns
    time_since_last_spawn = 0
    enemy_spawn_interval = 2
    max_enemies = 100
    spawn_interval_adjustment_time = 0
    adjustment_interval = 2.0
    min_spawn_interval = 0.30
    max_spawn_interval = 2

    # Spawn initial enemies
    for _ in range(3):
        x = random.choice([-50, WIDTH + 50])
        enemy_y = (HEIGHT - PLAYER_HEIGHT) - 130
        enemy_speed = random.uniform(5, 9)
        enemies.append(Enemy(x, enemy_y, enemy_speed))

    
    # For player movement
    y_velocity = 0
    x_velocity = 0
    on_ground = True
    facing_left = True

    # For dash ability
    is_dashing = False
    dash_timer = 0
    dash_cooldown_timer = 0

    # Player animations
    current_frame = 0
    last_frame_time = pygame.time.get_ticks()
    last_running_frame_time = pygame.time.get_ticks()
    RUNNING_ANIMATION_SPEED = 40

    # Bullets
    projectiles = []
    projectile_cooldown_timer = 0

    # Health
    player_hp = 150

    while run:
        clock.tick(70)
        
        # Update timers
        time_since_last_spawn += clock.get_time() / 1000
        spawn_interval_adjustment_time += clock.get_time() / 1000

        # Update cooldown timers
        projectile_cooldown_timer -= clock.get_time() / 1000
        dash_cooldown_timer -= clock.get_time() / 1000
        

        # Spawn Zombies
        if len(enemies) < max_enemies:
            if time_since_last_spawn >= enemy_spawn_interval:
                x = random.choice([-50, WIDTH + 50])
                enemy_y = (HEIGHT - PLAYER_HEIGHT) - 130
                enemy_speed = random.uniform(5, 9)
                enemies.append(Enemy(x, enemy_y, enemy_speed))
                time_since_last_spawn = 0

        if spawn_interval_adjustment_time >= adjustment_interval:
            enemy_spawn_interval = max(min_spawn_interval, min(max_spawn_interval, enemy_spawn_interval - 0.5))
            spawn_interval_adjustment_time = 0 

        # Move enemies towards player
        for enemy in enemies:
            enemy.move_towards_player(player, clock)

        # Enemy damage
        for enemy in enemies[:]:
            if pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height).colliderect(player):
                player_hp -= 15
                enemies.remove(enemy)
                if player_hp <= 0:
                    game_over()
                    

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        # Player input for movement and dash ability
        if keys[pygame.K_q] and dash_cooldown_timer <= 0:
            if not is_dashing:
                is_dashing = True
                dash_timer = DASH_DURATION
                dash_cooldown_timer = DASH_COOLDOWN
                x_velocity = DASH_SPEED if not facing_left else -DASH_SPEED

        if is_dashing:
            dash_timer -= clock.get_time() / 1000
            if dash_timer <= 0:
                is_dashing = False
            
            
        else:
            if keys[pygame.K_a]:
                x_velocity -= ACCELERATION
                facing_left = True
            if keys[pygame.K_d]:
                x_velocity += ACCELERATION
                facing_left = False

            if not (keys[pygame.K_a] or keys[pygame.K_d]):
                if x_velocity > 0:
                    x_velocity -= FRICTION
                elif x_velocity < 0:
                    x_velocity += FRICTION

            x_velocity = max(-MAX_SPEED, min(MAX_SPEED, x_velocity))

        # Move player
        player.x += x_velocity
        player.x = max(0, min(player.x, WIDTH - PLAYER_WIDTH))

        # Jumping
        if keys[pygame.K_SPACE] and on_ground:
            y_velocity = -JUMP
            on_ground = False

        if not on_ground:
            y_velocity += GRAVITY
        player.y += y_velocity

        # Ground collision
        if player.y >= (HEIGHT - PLAYER_HEIGHT) - 80:
            player.y = (HEIGHT - PLAYER_HEIGHT) - 80
            on_ground = True
            y_velocity = 0

        
        # GUN
        if keys[pygame.K_e]:
            if len(projectiles) < 10 and projectile_cooldown_timer <= 0:
                projectile_x = player.x + PLAYER_WIDTH // 2 - 5
                projectile_y = player.y + PLAYER_HEIGHT // 4
                projectiles.append(Projectile(projectile_x, projectile_y, facing_left))
                projectile_cooldown_timer = PROJECTILE_COOLDOWN

        # Move projectiles and check for collisions with enemies
        for projectile in projectiles[:]:
            projectile.move()
            for enemy in enemies[:]:
                if projectile.get_rect().colliderect(pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)):
                    projectiles.remove(projectile)
                    enemies.remove(enemy)
                    score += 1
                    break

        # Remove off-screen projectiles
        projectiles = [p for p in projectiles if 0 <= p.x <= WIDTH]

        # Idle and movement animation
        is_moving = keys[pygame.K_a] or keys[pygame.K_d]
        
        if is_moving:
            current_time = pygame.time.get_ticks()
            if current_time - last_running_frame_time >= RUNNING_ANIMATION_SPEED:
                current_frame = (current_frame + 1) % len(RUNNING_SPRITES)
                last_running_frame_time = current_time
        else:
            current_time = pygame.time.get_ticks()
            if current_time - last_frame_time >= ANIMATION_SPEED:
                current_frame = (current_frame + 1) % len(PLAYER_SPRITES)
                last_frame_time = current_time

        # Determine current sprite based on movement
        if is_moving:
            current_sprite = RUNNING_SPRITES[current_frame % len(RUNNING_SPRITES)]
        else:
            current_sprite = PLAYER_SPRITES[current_frame % len(PLAYER_SPRITES)]

        # Draw everything
        draw(player, current_sprite, facing_left, enemies, projectiles, player_hp, score, font)

    pygame.quit()

if __name__ == "__main__":
    main()
