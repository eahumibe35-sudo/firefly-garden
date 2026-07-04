import pygame
import random
import sys

# -----------------------------
# Initialize pygame and mixer
# -----------------------------
pygame.init()
pygame.mixer.init()

# Load and play background music
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.025)

# -----------------------------
# Window setup (FULLSCREEN)
# -----------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Firefly Garden")

clock = pygame.time.Clock()

# -----------------------------
# Colours
# -----------------------------
DARK = (10, 10, 30)
WHITE = (255, 255, 255)

font = pygame.font.SysFont("Arial", 40)

# -----------------------------
# Glow colours for each level
# -----------------------------
GLOW_COLOURS = [
    (255, 255, 150),
    (150, 200, 255),
    (255, 150, 200),
    (150, 255, 180),
    (220, 150, 255),
]

colour_mode = 0  # 0 = manual, 1 = cycle

# -----------------------------
# Load images
# -----------------------------
glow_bead_img = pygame.image.load("glow_bead.png").convert_alpha()
glow_bead_img = pygame.transform.scale(glow_bead_img, (40, 40))

glow_bead_unlit = glow_bead_img.copy()
dark_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
dark_surface.fill((0, 0, 0, 150))
glow_bead_unlit.blit(dark_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

# Load semi-transparent landscape background
background_overlay = pygame.image.load("dark_firefly_landscape.png").convert_alpha()
background_overlay.set_alpha(160)  # slightly opaque

# -----------------------------
# Game states
# -----------------------------
STATE_MENU = 0
STATE_RULES = 1
STATE_GAME = 2
STATE_COLOUR = 3
game_state = STATE_MENU

# -----------------------------
# Button function
# -----------------------------
def draw_button(text, x, y, w, h):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    rect = pygame.Rect(x, y, w, h)

    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, (180, 180, 255), rect)
        if click:
            return True
    else:
        pygame.draw.rect(screen, (140, 140, 200), rect)

    label = font.render(text, True, WHITE)
    screen.blit(label, (x + 20, y + 10))
    return False

# -----------------------------
# Home screen
# -----------------------------
def home_screen():
    screen.fill(DARK)
    screen.blit(background_overlay, (0, 0))  # overlay under buttons

    title = font.render("Firefly Garden", True, WHITE)
    screen.blit(title, (WIDTH//2 - 150, 100))

    if draw_button("Play", WIDTH//2 - 100, 250, 200, 60):
        return STATE_GAME
    if draw_button("Rules", WIDTH//2 - 100, 350, 200, 60):
        return STATE_RULES
    if draw_button("Colours", WIDTH//2 - 100, 450, 200, 60):
        return STATE_COLOUR
    return STATE_MENU

# -----------------------------
# Rules screen
# -----------------------------
def rules_screen():
    screen.fill(DARK)
    screen.blit(background_overlay, (0, 0))

    lines = [
        "Move with arrow keys",
        "Touch glow beads to light them",
        "Lighting beads makes you brighter",
        "If your light fades too low, you lose a level",
        "Light all beads to level up!",
        "Press H anytime to return home",
        "Press ESC to close the game"
    ]

    y = 150
    for line in lines:
        label = font.render(line, True, WHITE)
        screen.blit(label, (80, y))
        y += 50

    if draw_button("X", WIDTH - 80, 20, 50, 40):
        return STATE_MENU
    return STATE_RULES

# -----------------------------
# Colour Picker
# -----------------------------
def colour_picker_screen():
    global colour_mode
    screen.fill(DARK)
    screen.blit(background_overlay, (0, 0))

    title = font.render("Choose Glow Colour", True, WHITE)
    screen.blit(title, (WIDTH//2 - 180, 80))

    colour_buttons = [
        ("Yellow", (255, 255, 150)),
        ("Blue",   (150, 200, 255)),
        ("Pink",   (255, 150, 200)),
        ("Green",  (150, 255, 180)),
        ("Purple", (220, 150, 255)),
        ("Random", None),
        ("All Colours", None),
    ]

    cols = 2
    button_w = 200
    button_h = 50
    start_x = WIDTH//2 - 220
    start_y = 200
    gap_x = 240
    gap_y = 70

    for index, (name, colour) in enumerate(colour_buttons):
        row = index // cols
        col = index % cols
        x = start_x + col * gap_x
        y = start_y + row * gap_y

        if draw_button(name, x, y, button_w, button_h):
            if colour is not None:
                colour_mode = 0
                for i in range(len(GLOW_COLOURS)):
                    GLOW_COLOURS[i] = colour
            elif name == "Random":
                colour_mode = 0
                random_colour = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
                for i in range(len(GLOW_COLOURS)):
                    GLOW_COLOURS[i] = random_colour
            elif name == "All Colours":
                colour_mode = 1

    if draw_button("X", WIDTH - 80, 20, 50, 40):
        return STATE_MENU
    return STATE_COLOUR

# -----------------------------
# Firefly Sprite
# -----------------------------
class Firefly(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("firefly.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 70))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 4
        self.light = 255
        self.fade_rate = 0.15

    def reset_light(self):
        self.light = 255

    def update(self, keys):
        if keys[pygame.K_LEFT]:  self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.rect.x += self.speed
        if keys[pygame.K_UP]:    self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:  self.rect.y += self.speed
        self.light -= self.fade_rate
        if self.light < 0:
            self.light = 0

    def draw_glow(self, surface):
        if self.light > 0:
            if colour_mode == 1:
                base_r, base_g, base_b = GLOW_COLOURS[(current_level - 1) % len(GLOW_COLOURS)]
            else:
                base_r, base_g, base_b = GLOW_COLOURS[0]
            glow_radius = int(self.light / 2)
            glow_color = (base_r, base_g, base_b, int(self.light))
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (self.rect.centerx - glow_radius,self.rect.centery - glow_radius))

# -----------------------------
# Level system
# -----------------------------
def generate_beads(amount):
    return [{"x": random.randint(50, WIDTH - 50),
            "y": random.randint(50, HEIGHT - 50),
            "lit": False} for _ in range(amount)]

current_level = 1
beads = generate_beads(6)
player = Firefly(WIDTH // 2, HEIGHT // 2)
all_sprites = pygame.sprite.Group(player)

def show_well_done():
    text = font.render("Well done!", True, WHITE)
    for alpha in range(0, 255, 5):
        text.set_alpha(alpha)
        screen.fill(DARK)
        screen.blit(background_overlay, (0, 0))
        screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 20))
        pygame.display.update()
        clock.tick(60)
    for alpha in range(255, 0, -5):
        text.set_alpha(alpha)
        screen.fill(DARK)
        screen.blit(background_overlay, (0, 0))
        screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 20))
        pygame.display.update()
        clock.tick(60)

# -----------------------------
# Level transitions
# -----------------------------
def next_level():
    global current_level, beads
    current_level += 1
    beads = generate_beads(6 + (current_level - 1) * 4)
    player.reset_light()
    player.rect.center = (WIDTH // 2, HEIGHT // 2)

def previous_level():
    global current_level, beads
    if current_level > 1:
        current_level -= 1
    beads = generate_beads(6 + (current_level - 1) * 4)
    player.reset_light()
    player.rect.center = (WIDTH // 2, HEIGHT // 2)

# -----------------------------
# Main Game Loop
# -----------------------------
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # ESC closes the game
    if keys[pygame.K_ESCAPE]:
        running = False

    # -----------------------------
    # HOME SCREEN
    # -----------------------------
    if game_state == STATE_MENU:
        game_state = home_screen()

    # -----------------------------
    # RULES SCREEN
    # -----------------------------
    elif game_state == STATE_RULES:
        game_state = rules_screen()

    # -----------------------------
    # COLOUR PICKER SCREEN
    # -----------------------------
    elif game_state == STATE_COLOUR:
        game_state = colour_picker_screen()

    # -----------------------------
    # GAME SCREEN
    # -----------------------------
    elif game_state == STATE_GAME:

        # Bottom layer (black)
        screen.fill(DARK)

        # Middle layer (semi-transparent forest)
        screen.blit(background_overlay, (0, 0))

        # Update player
        all_sprites.update(keys)

        # Press H to return home
        if keys[pygame.K_h]:
            game_state = STATE_MENU
            continue

        all_lit = True

        # Draw beads
        for bead in beads:
            dist = ((player.rect.centerx - bead["x"])**2 +
                    (player.rect.centery - bead["y"])**2)**0.5

            if dist < 40 and not bead["lit"]:
                bead["lit"] = True
                player.light += 40
                if player.light > 255:
                    player.light = 255

            if not bead["lit"]:
                all_lit = False

            # Draw tinted or bright bead
            if bead["lit"]:
                screen.blit(glow_bead_img, (bead["x"] - 20, bead["y"] - 20))
            else:
                screen.blit(glow_bead_unlit, (bead["x"] - 20, bead["y"] - 20))

        # Glow + sprite
        player.draw_glow(screen)
        all_sprites.draw(screen)

        # Level text
        level_text = font.render(f"Level: {current_level}", True, WHITE)
        screen.blit(level_text, (20, 20))

        # Level up
        if all_lit:
            show_well_done()
            next_level()

        # Level down
        if player.light <= 5:
            previous_level()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
