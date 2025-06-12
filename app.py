import pygame
import sys
import random

pygame.init()
pygame.mixer.init()

class SoundController:
    def __init__(self):
        self.current_sound = None
        self.current_channel = None

    def play(self, sound):
        if self.current_sound == sound:
            if self.current_channel and self.current_channel.get_busy():
                return
        if self.current_channel:
            self.current_channel.stop()
        self.current_channel = sound.play()
        self.current_sound = sound

try:
    pygame.mixer.music.load("sounds/bg_music_quiet.mp3")
    pygame.mixer.music.set_volume(0.07)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Error loading music: {e}")

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("I Can't Breathe")

def load_scaled_image(path, width=96):
    img = pygame.image.load(path).convert_alpha()
    height = int(img.get_height() * (width / img.get_width()))
    return pygame.transform.scale(img, (width, height))

def load_image_fullscreen(path):
    img = pygame.image.load(path).convert()
    return pygame.transform.scale(img, (WIDTH, HEIGHT))

background_img = load_image_fullscreen("images/background.jpg")
player_img_idle = load_scaled_image("images/player.png")
player_img_left = pygame.transform.flip(player_img_idle, True, False)
player_img_right = player_img_idle
banana_img = load_scaled_image("images/banana.png")
coconut_img = load_scaled_image("images/coconut.png")
capsule_img = load_scaled_image("images/capsule.png")
enemy_img = load_scaled_image("images/enemy.png")

def load_sound(path, volume=0.3):
    try:
        snd = pygame.mixer.Sound(path)
        snd.set_volume(volume)
        return snd
    except:
        return None

banana_sound = load_sound("sounds/banana.wav")
coconut_sound = load_sound("sounds/coconut.wav")
capsule_sound = load_sound("sounds/capsule.wav")
hit_sound = load_sound("sounds/hit.wav", volume=0.6)

sound_player = SoundController()

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 72)

player_rect = player_img_idle.get_rect()
player_rect.midbottom = (WIDTH // 2, HEIGHT - 10)
player_speed = 5

score = 0
combo = 0
breath = 30 * 60
health = 3
items = []

item_types = [
    ("banana", banana_img, 3, 1, 5),
    ("coconut", coconut_img, 9, 10, 1),
    ("capsule", capsule_img, 4, 0, 3),
    ("enemy", enemy_img, 4, 0, 2)
]

weights = [i[4] for i in item_types]
frame_counter = 0
game_state = "menu"
player_direction = "idle"

def spawn_item():
    item = random.choices(item_types, weights=weights)[0]
    rect = item[1].get_rect()
    rect.x = random.randint(0, WIDTH - rect.width)
    rect.y = -rect.height
    items.append({"type": item[0], "img": item[1], "rect": rect, "speed": item[2], "score": item[3]})

def draw_breath_bar():
    breath_icon = pygame.transform.scale(capsule_img, (32, 32))
    screen.blit(breath_icon, (10, 10))
    pygame.draw.rect(screen, (200, 0, 0), (50, 20, 200, 20))
    pygame.draw.rect(screen, (0, 200, 0), (50, 20, max(0, int(200 * breath / (60 * 30))), 20))

def draw_health():
    heart = pygame.transform.scale(enemy_img, (24, 24))
    for i in range(health):
        screen.blit(heart, (WIDTH - (i+1)*30, 20))

def draw_menu():
    screen.blit(background_img, (0, 0))
    text = large_font.render("SHAHID George Floyd!", True, (0, 0, 0))
    prompt = font.render("Press SPACE to Start", True, (0, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

def draw_gameover():
    screen.blit(background_img, (0, 0))
    text = large_font.render("Game Over", True, (255, 0, 0))
    final_score = font.render(f"Score: {score}", True, (255, 255, 255))
    prompt = font.render("Press R to Restart", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
    screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 40))
    pygame.display.flip()

def reset_game():
    global player_rect, score, breath, health, items, frame_counter, combo
    player_rect.midbottom = (WIDTH // 2, HEIGHT - 10)
    score = 0
    combo = 0
    breath = 30 * 60
    health = 3
    items.clear()
    frame_counter = 0

running = True
while running:
    if game_state == "menu":
        draw_menu()
    elif game_state == "gameover":
        draw_gameover()
    else:
        screen.blit(background_img, (0, 0))

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player_rect.left > 0:
            player_rect.x -= player_speed
            player_direction = "left"
        elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player_rect.right < WIDTH:
            player_rect.x += player_speed
            player_direction = "right"
        else:
            player_direction = "idle"

        if frame_counter % 60 == 0:
            spawn_item()

        for item in items[:]:
            item["rect"].y += item["speed"]
            screen.blit(item["img"], item["rect"])

            if player_rect.colliderect(item["rect"]):
                if item["type"] == "banana" and banana_sound: sound_player.play(banana_sound)
                elif item["type"] == "coconut" and coconut_sound: sound_player.play(coconut_sound)
                elif item["type"] == "capsule" and capsule_sound:
                    sound_player.play(capsule_sound)
                    breath += 10 * 60
                    breath = min(breath, 30 * 60)
                elif item["type"] == "enemy":
                    if hit_sound: sound_player.play(hit_sound)
                    health -= 1
                    combo = 0
                    if health <= 0:
                        game_state = "gameover"
                score += item["score"] * (1 + combo // 5)
                combo += 1
                items.remove(item)
            elif item["rect"].top > HEIGHT:
                combo = 0
                items.remove(item)

        breath -= 1
        if breath <= 0:
            if hit_sound: sound_player.play(hit_sound)
            game_state = "gameover"

        if player_direction == "left":
            screen.blit(player_img_left, player_rect)
        elif player_direction == "right":
            screen.blit(player_img_right, player_rect)
        else:
            screen.blit(player_img_idle, player_rect)

        draw_breath_bar()
        draw_health()
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (400, 10))

        pygame.display.flip()
        frame_counter += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == "menu" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game_state = "playing"
            reset_game()
        elif game_state == "gameover" and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            game_state = "playing"
            reset_game()

    clock.tick(60)

pygame.quit()
sys.exit()
