import pygame
import sys
import random

pygame.init()

# --------------------
# SETUP
# --------------------
WIDTH, HEIGHT = 850, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("homeless simulator 1: a cehgames production")
clock = pygame.time.Clock()

GRAVITY = 1300
JUMP_FORCE = -500
MOVE_SPEED = 250
GROUND_Y = 570 # The y position where the ground surface is drawn (600 - 40 approx)

# --- EFFECT CONSTANTS ---
INVERT_DURATION = 120000 # 120 seconds (2 minutes) in milliseconds
SPEED_BOOST = 150 # Extra speed to add when inverted (250 + 150 = 400 total)

# --- STORE CONSTANTS ---
SODA_COST = 2
CHIPS_COST = 3
GEEK_COST = 20 # Cost for Geek Bar
TICKET_COST = 10

# --- NEW: Win Condition and Geek Level Constants ---
WIN_GOAL = 10000 # The amount of money needed to win the game
GEEK_LEVEL_MAX = 20

# --------------------
# LOAD ASSETS
# --------------------
# All file paths now start with "assets/"
sprite_sheet = pygame.image.load("assets/New Piskel.png").convert_alpha()

background = pygame.image.load("assets/background.jpeg").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# --- NEW MINI-GAME SETUP: Load Minigame Background ---
try:
    # Load the requested casino image for the mini-game screen
    minigame_background = pygame.image.load("assets/casino.png").convert()
    minigame_background = pygame.transform.scale(minigame_background, (WIDTH, HEIGHT))
except pygame.error:
    # Placeholder if casino.png is missing (Dark Green)
    minigame_background = pygame.Surface((WIDTH, HEIGHT))
    minigame_background.fill((10, 50, 10))
# ----------------------------------------------------

# --- NEW STORE BACKGROUND PLACEHOLDER ---
try:
    # Corrected path for store background
    store_background = pygame.image.load("assets/store_bg.png").convert()
    store_background = pygame.transform.scale(store_background, (WIDTH, HEIGHT))
except pygame.error:
    # Placeholder if store_bg.png is missing (Dark Blue)
    store_background = pygame.Surface((WIDTH, HEIGHT))
    store_background.fill((10, 10, 50))
try:
    ticket_image = pygame.image.load("assets/ticket.png").convert_alpha()
    ticket_image = pygame.transform.scale(ticket_image, (32,32))
except:
    print("ERROR FAILED TO LOAD ASSET: TICKET.PNG / RELOAD GAME")

tony_img = pygame.image.load("assets/tony.png")
sign_img = pygame.image.load("assets/sign.jpeg")
tony_img = pygame.transform.scale(tony_img, (96, 96)).convert_alpha()
tent_closed_img = pygame.image.load("assets/tent_closed.png").convert_alpha()
tent_open_img = pygame.image.load("assets/tent_open.png").convert_alpha()
tent_closed_img = pygame.transform.scale(tent_closed_img, (96, 96))
tent_open_img = pygame.transform.scale(tent_open_img, (96, 96))
sign_img = pygame.transform.scale(sign_img, (50,50))


# Assuming a dollar image named 'dollar.png' exists.
try:
    dollar_img = pygame.image.load("assets/dollar.png").convert_alpha()
    dollar_img = pygame.transform.scale(dollar_img, (32, 32))
except pygame.error:
    # Placeholder if dollar.png is missing
    dollar_img = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(dollar_img, (34, 139, 34), (16, 16), 16) # Green circle

# --- ITEM ICONS ---
try:
    soda_icon = pygame.image.load("assets/bottle.jpg").convert_alpha()
    soda_icon = pygame.transform.scale(soda_icon, (32, 32))
except pygame.error:
    # Placeholder if bottle.jpg is missing (Blue can)
    soda_icon = pygame.Surface((32, 32))
    soda_icon.fill((0, 0, 150))
    pygame.draw.rect(soda_icon, (150, 150, 255), (0, 0, 32, 8)) # Top detail

try: 
    hotdog_icon = pygame.image.load("assets/fent.png").convert_alpha()
    hotdog_icon = pygame.transform.scale(hotdog_icon, (32,32))
except:
    # Placeholder for Hotdog icon (Creating a red square)
    hotdog_icon = pygame.Surface((32, 32))
    hotdog_icon.fill((180, 0, 0)) # Red square for hotdog (placeholder)
    pygame.draw.rect(hotdog_icon, (255, 255, 255), (8, 0, 16, 32)) # "Bun" detail

try:
    geek_icon = pygame.image.load("assets/bar.png").convert_alpha()
    geek_icon = pygame.transform.scale(geek_icon, (32,32))
except:
    geek_icon = pygame.Surface((32,32))
    geek_icon.fill((180,0,0))
    pygame.draw.rect(geek_icon, (255,255,255), (8,0,16,32))
try: 
    bus_img = pygame.image.load("assets/bus.png").convert_alpha()
    bus_img = pygame.transform.scale(bus_img, (128,128))
except:
    bus_img = pygame.surface((64,64))
    bus_img.fil(180,0,0)
    pygame.draw.rect(bus_img, (255,255,255), (8,0,16,32))

# Placeholder for Chips icon (Keeping the placeholder for the variable if needed elsewhere)
chips_icon = pygame.Surface((32, 32))
chips_icon.fill((255, 200, 0))
pygame.draw.circle(chips_icon, (200, 150, 0), (16, 16), 10) # Detail

# --- NEW: Load the 'fold' image for the effect ---
try:
    fold_img = pygame.image.load("assets/fold.png").convert_alpha()
    # Fixed to use the explicit size (64, 64) the user set
    fold_img = pygame.transform.scale(fold_img, (64, 64)) 
except pygame.error:
    print("Warning: assets/fold.png not found. Using placeholder for effect state.")
    fold_img = pygame.Surface((64, 64), pygame.SRCALPHA) # Use 64x64 for placeholder too
    fold_img.fill((255, 0, 0, 150)) # Red transparent box placeholder

FRAME_W = 32
FRAME_H = 32
SCALE = 3

def get_frame(sheet, x, y, w, h, scale=1):
    frame = pygame.Surface((w, h), pygame.SRCALPHA)
    frame.blit(sheet, (0, 0), (x, y, w, h))
    if scale != 1:
        frame = pygame.transform.scale(frame, (w * scale, h * scale))
    return frame

# Player animation (row 0)
frames = []
for i in range(4):
    frames.append(
        get_frame(sprite_sheet, i * FRAME_W, 0, FRAME_W, FRAME_H, SCALE)
    )
    
# --------------------
# PLAYER
# --------------------
player_original_w = FRAME_W * SCALE # 96
player_original_h = FRAME_H * SCALE # 96
player_rect = pygame.Rect(400, 200, player_original_w, player_original_h)
vel_y = 0
on_ground = False

frame_index = 0
anim_timer = 0
moving = False

# --------------------
# TENT
# --------------------
tent_rect = tent_closed_img.get_rect(topleft=(100, 495))
tent_open = False
#-------------
# dollar
#-------------
playermoney = 0
HOTDOG_COST = 1 # Cost of the safe item

# --- INVENTORY VARIABLES ---
soda_bought = 0
chips_bought = 0 
geek_bought = 0
hotdogs_bought = 0

# --- NEW: Game State Variables ---
geek_level = 0
game_over = False
game_won = False # New state for the win screen
in_minigame = False
minigame_counter = 0 
MINIGAME_INTERACT_COST = 5 
# --- INTRO SCREEN ---
intro_active = True
intro_start_time = pygame.time.get_ticks()
INTRO_DURATION = 10  # 3 seconds
# ----------------------------------------------------


class Dollar(pygame.sprite.Sprite):
    # ... (Dollar class remains unchanged) ...
    def __init__(self, image, ground_y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.ground_y = ground_y
        self.collected = False
        self.respawn_timer = 0
        self.RESPAWN_TIME = 3.0 # seconds
        self.spawn_random()

    def spawn_random(self):
        # Spawns the dollar at a random x position on the ground
        random_x = random.randint(0, WIDTH - self.rect.width)
        # Position it just above the ground line (GROUND_Y)
        self.rect.bottom = self.ground_y - 2 
        self.rect.x = random_x
        self.collected = False
        self.respawn_timer = 0

    def update(self, dt):
        if self.collected:
            self.respawn_timer += dt
            if self.respawn_timer >= self.RESPAWN_TIME:
                self.spawn_random()

    def draw(self, surface):
        if not self.collected:
            surface.blit(self.image, self.rect.topleft)

# --- SIGN RECT FIX: Position the collision box where the image is drawn (480, 440)
sign_rect = sign_img.get_rect(topleft=(480, 440))

# --- Tony NPC ---
tony_rect = tony_img.get_rect(topleft=(650, 475))
#bus sign - CORRECTED POSITIONING (Assumes bus is 128x128)
BUS_X_POS = 250
BUS_Y_POS = GROUND_Y - bus_img.get_height()
bus_rect = bus_img.get_rect(topleft=(BUS_X_POS, BUS_Y_POS))

# State for transaction feedback
tony_message_timer = 0
tony_message_text = ""
TONY_MESSAGE_DURATION = 1.5 # seconds

# --- Effect State Variables ---
effect_active = False
effect_start_time = 0
current_move_speed = MOVE_SPEED

# --- SODA EFFECT ---
soda_active = False
soda_start_time = 0
SODA_DURATION = 10000  # 10 seconds in milliseconds
SODA_SPEED_BOOST = 100


# Initialize the dollar object
dollar = Dollar(dollar_img, GROUND_Y)

# --------------------
# GAME STATE
# --------------------
game_paused = False
sleeping = False
in_store = False 

font = pygame.font.SysFont(None, 64)
small_font = pygame.font.SysFont(None, 24)
money_font = pygame.font.SysFont(None, 36)
inventory_font = pygame.font.SysFont(None, 20)

# --------------------
# GROUND
# --------------------
# The ground rect is kept for collision detection, but it won't be drawn.
ground_rect = pygame.Rect(0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y) 

# --------------------
# FUNCTIONS
# --------------------
def draw_store_ui():
    # Draw Store Background
    screen.blit(store_background, (0, 0))
    
    # Draw Store Title
    title_font = pygame.font.SysFont(None, 72)
    title_text = title_font.render("7/11 Store", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # Draw Exit Prompt
    # Updated text to reflect 'E' key
    exit_text = small_font.render("Press E to Exit", True, (255, 255, 255))
    screen.blit(exit_text, (10, 10))
    
    # Define Item List
    store_items = [
        ("Fent Hotdog", HOTDOG_COST, hotdog_icon, pygame.K_1, hotdogs_bought),
        ("beer", SODA_COST, soda_icon, pygame.K_2, soda_bought),
        ("Geek Bar", GEEK_COST, geek_icon, pygame.K_3, geek_bought)
    ]
    
    start_y = 150
    item_height = 80
    
    for i, (name, cost, icon, key, current_stock) in enumerate(store_items):
        y = start_y + i * item_height
        
        # Draw background rect for the item
        item_rect = pygame.Rect(WIDTH // 4, y, WIDTH // 2, 60)
        pygame.draw.rect(screen, (80, 80, 80), item_rect, border_radius=5)
        
        # Draw icon
        screen.blit(icon, (item_rect.x + 10, item_rect.y + 14))
        
        # Draw name and cost
        name_text = money_font.render(name, True, (255, 255, 255))
        cost_text = money_font.render(f"${cost}", True, (255, 255, 0))
        
        screen.blit(name_text, (item_rect.x + 60, item_rect.y + 10))
        screen.blit(cost_text, (item_rect.right - cost_text.get_width() - 10, item_rect.y + 10))
        
        # Draw buy key prompt (using the key name like '1', '2' or '3')
        key_name = pygame.key.name(key).upper()
        buy_text = small_font.render(f"Press {key_name} to Buy", True, (0, 255, 0))
        screen.blit(buy_text, (item_rect.x + 60, item_rect.y + 35))

# --- MINI-GAME UI ---
def draw_minigame_ui():
    global playermoney, minigame_counter

    # 1. Draw Background
    screen.blit(minigame_background, (0, 0))
    
    # 2. Draw Title and Exit Prompt
    title_font = pygame.font.SysFont(None, 72)
    title_text = title_font.render("fentatini casino", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    
    exit_text = small_font.render("Press E to Exit", True, (255, 255, 255))
    screen.blit(exit_text, (10, 10))

    # 3. Mini-Game Interaction Area (Simple Collection Game)
    
    # Display Player Money
    money_text = money_font.render(f"Money: ${playermoney}", True, (255, 255, 0))
    screen.blit(money_text, (WIDTH - money_text.get_width() - 10, 10))

    # Display Instructions and Status
    status_y = HEIGHT // 2 - 50
    pygame.draw.rect(screen, (50, 50, 50, 180), (WIDTH // 4, status_y, WIDTH // 2, 180), border_radius=10)

    status1 = money_font.render(f"Attempts: {minigame_counter}", True, (255, 255, 255))
    screen.blit(status1, (WIDTH // 2 - status1.get_width() // 2, status_y + 20))
    
    status2 = small_font.render(f"betting 1/8 of your worth good luck!", True, (200, 200, 200))
    screen.blit(status2, (WIDTH // 2 - status2.get_width() // 2, status_y + 70))
    
    # Safe Interaction Prompt (Key A to perform action)
    action_text = font.render("press a to bet", True, (0, 255, 0))
    screen.blit(action_text, (WIDTH // 2 - action_text.get_width() // 2, status_y + 120))

# --- NEW: Win Screen Function ---
def draw_win_screen():
    # Dark transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(240)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Win Title
    win_font = pygame.font.SysFont(None, 96)
    text = win_font.render("YOU WIN!", True, (0, 255, 0))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
    screen.blit(text, rect)

    # Subtext/Achievement
    subtext = font.render(f"You escaped poverty with ${playermoney}!", True, (255, 255, 255))
    sub_rect = subtext.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    
    screen.blit(subtext, sub_rect)
    
    # Quit prompt
    quit_text = small_font.render("Press ESC to Quit", True, (200, 200, 200))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    screen.blit(quit_text, quit_rect)
# ----------------------------------------------------


# --------------------
# GAME LOOP
# --------------------
running = True
while running:
    pygame.display.flip()
    dt = clock.tick(60) / 1000  # 60 FPS, dt in seconds
    # --- WIN CONDITION CHECK (Must be before event processing) ---
    if not game_won and playermoney >= WIN_GOAL:
        game_won = True
        game_paused = True # Effectively pauses the game logic

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Allow quitting on ESC even if game is over or won
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # If game is over or won, stop processing interactive events
        if game_over or game_won: 
            continue 
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL:
                # Debug cheat for testing win
                playermoney = playermoney + 1000
                if playermoney > WIN_GOAL and not game_won:
                    game_won = True
                    game_paused = True
            
            
            # --- WAKE UP LOGIC (Priority) ---
            if event.key == pygame.K_q and sleeping:
                sleeping = False
                game_paused = False
                tent_open = False
                continue 
            
            if event.key == pygame.K_e:
                # --- Store Exit Logic (Priority 1) ---
                if in_store:
                    in_store = False
                    game_paused = False
                    player_rect.x = sign_rect.x + sign_rect.width + 10
                # --- Mini-Game Exit Logic (Priority 2) ---
                elif in_minigame:
                    in_minigame = False
                    game_paused = False
                    player_rect.x = BUS_X_POS - player_rect.width - 10
            
            # --- Game State Interaction (Mini-Game/Store) ---
            if in_minigame:
                
                # Simple Mini-Game Action (Key A)
                if event.key == pygame.K_a:
                    # Bet is 1/4 of total money, rounded to 2 decimals
                    bet = round(playermoney * 0.125, 2)

                    if playermoney >= bet and bet > 0:
                        playermoney = round(playermoney - bet, 2)
                        minigame_counter += 1

                        if random.randint(1, 10) == 1:
                            # Win: double the bet
                            winnings = round(playermoney *2, 2)
                            playermoney = round(playermoney + winnings, 2)
                            tony_message_text = f"Mini-Game: WON ${winnings:.2f}!"
                        else:
                            tony_message_text = f"Mini-Game: Lost ${bet:.2f}..."
                    else:
                        tony_message_text = "Mini-Game: Not enough money to bet."
                        tony_message_timer = TONY_MESSAGE_DURATION

            elif in_store:
                
                # --- STORE BUYING LOGIC (Key 1, 2, 3) ---
                # Buy Fent Hotdog (Key 1)
                if event.key == pygame.K_1:
                    if playermoney >= HOTDOG_COST: 
                        playermoney -= HOTDOG_COST
                        hotdogs_bought += 1 
                        tony_message_text = "Bought Fent Hotdog!"
                    else:
                        tony_message_text = f"Not enough money for Fent Hotdog (${HOTDOG_COST})."
                    tony_message_timer = TONY_MESSAGE_DURATION
                    
                # Buy Soda (Key 2)
                elif event.key == pygame.K_2:
                    if playermoney >= SODA_COST:
                        playermoney -= SODA_COST
                        soda_bought += 1
                        tony_message_text = "Bought Beer!"
                    else:
                        tony_message_text = f"Not enough money for Soda (${SODA_COST})."
                    tony_message_timer = TONY_MESSAGE_DURATION
                
                # Buy Geek Bar (Key 3)
                elif event.key == pygame.K_3:
                    if playermoney >= GEEK_COST:
                        playermoney -= GEEK_COST
                        geek_bought += 1
                        tony_message_text = "Bought Geek Bar!"
                    else:
                        tony_message_text = f"Not enough money for Geek Bar (${GEEK_COST})."
                    tony_message_timer = TONY_MESSAGE_DURATION
                elif event.key == pygame.K_4:
                    if playermoney >= TICKET_COST:
                        playermoney -= TICKET_COST
                        

            # --- WORLD INTERACTION (E & Q) (Only if not paused/in store/in minigame) ---
            elif not game_paused and not in_store and not in_minigame:

                if event.key == pygame.K_q:
                    # Tent interaction (to START sleeping)
                    if player_rect.colliderect(tent_rect):
                        if not effect_active:
                            tent_open = not tent_open
                            sleeping = tent_open
                            game_paused = tent_open
                            
                    # Bus Interaction (to START minigame)
                    elif player_rect.colliderect(bus_rect):
                        in_minigame = True
                        game_paused = True
                        tony_message_text = "Entered Mini-Game Area."
                        tony_message_timer = TONY_MESSAGE_DURATION
                        
                if event.key == pygame.K_e:
                    
                    # ENTER store logic (when near sign)
                    if player_rect.colliderect(sign_rect) and not sleeping:
                        in_store = True
                        game_paused = True
                        
                    # Tony Interaction (Buying Hotdog)
                    elif player_rect.colliderect(tony_rect):
                        if playermoney >= HOTDOG_COST:
                            playermoney -= HOTDOG_COST
                            hotdogs_bought += 1
                            tony_message_text = "you now have fent"
                        else:
                            tony_message_text = f"Tony: Need ${HOTDOG_COST} for a Hotdog."
                            
                        tony_message_timer = TONY_MESSAGE_DURATION
                    
            
                # --- INVENTORY/USE ITEM LOGIC (Key 1, 3) ---
                # EAT HOTDOG LOGIC (Key '1')
                if event.key == pygame.K_1:
                    if hotdogs_bought > 0 and not effect_active:
                        hotdogs_bought -= 1
                        effect_active = True
                        effect_start_time = pygame.time.get_ticks()
                        current_move_speed = MOVE_SPEED + SPEED_BOOST
                        
                        # --- NEW: Increment Geek Level ---
                        geek_level += 1 
                        if geek_level >= GEEK_LEVEL_MAX:
                            game_over = True
                        # ---------------------------------
                        
                        # --- EFFECT START: Change player_rect size to match the new image ---
                        # We save the bottom position to keep the player on the ground
                        old_bottom = player_rect.bottom 
                        player_rect.size = fold_img.get_size()
                        player_rect.bottom = old_bottom
                        # ------------------------------------------------------------------
                        
                    elif effect_active:
                        tony_message_text = "Already under the effect!"
                        tony_message_timer = TONY_MESSAGE_DURATION
                        
                # USE GEEK BAR LOGIC (Key '3')
                if event.key == pygame.K_3:
                    if geek_bought > 0: 
                        geek_bought -= 1 
                        tony_message_text = "Used Geek Bar. Feeling focused."
                        tony_message_timer = TONY_MESSAGE_DURATION

                        # --- NEW: Increment Geek Level ---
                        geek_level += 1
                        if geek_level >= GEEK_LEVEL_MAX:
                            game_over = True
                        # ---------------------------------
                # DRINK SODA LOGIC (Key '2')
                if event.key == pygame.K_2:
                    if soda_bought > 0 and not soda_active:
                        soda_bought -= 1
                        soda_active = True
                        soda_start_time = pygame.time.get_ticks()
                        current_move_speed += SODA_SPEED_BOOST
        
                        tony_message_text = "Drank Soda! Speed Boost!"
                        tony_message_timer = TONY_MESSAGE_DURATION
        
                    elif soda_active:
                        tony_message_text = "Already hyped on soda!"
                        tony_message_timer = TONY_MESSAGE_DURATION
                        


    keys = pygame.key.get_pressed()
    moving = False

    # --------------------
    # GAME LOGIC (only if not paused/over/won)
    # --------------------
    # Check against game_paused, which covers sleeping, minigame, and store
    if not game_paused and not game_over and not game_won:
        
        # --- EFFECT TIMER LOGIC ---
        if effect_active:
            elapsed_time = pygame.time.get_ticks() - effect_start_time
            if elapsed_time >= INVERT_DURATION:
                effect_active = False
                current_move_speed = MOVE_SPEED # Reset speed
                tony_message_text = "Control effect has worn off."
                tony_message_timer = TONY_MESSAGE_DURATION # Give feedback
                
                # --- EFFECT END: Restore player_rect size and position ---
                old_bottom = player_rect.bottom
                player_rect.size = (player_original_w, player_original_h)
                player_rect.bottom = old_bottom
                # --------------------------------------------------------

        # 1. Movement
        move_amount = current_move_speed * dt
        
        if effect_active:
            # Controls are flipped
            if keys[pygame.K_a]: # Press A -> Move Right
                player_rect.x += move_amount
                moving = True
            if keys[pygame.K_d]: # Press D -> Move Left
                player_rect.x -= move_amount
                moving = True
        else:
            # Normal controls
            if keys[pygame.K_a]: # Press A -> Move Left
                player_rect.x -= move_amount
                moving = True
            if keys[pygame.K_d]: # Press D -> Move Right
                player_rect.x += move_amount
                moving = True


        if keys[pygame.K_w] and on_ground:
            vel_y = JUMP_FORCE
            on_ground = False

        # 2. Gravity and Vertical Movement
        vel_y += GRAVITY * dt
        player_rect.y += vel_y * dt

        # 3. Ground Collision
        # This keeps the player on the ground at GROUND_Y
        if player_rect.colliderect(ground_rect):
            player_rect.bottom = ground_rect.top
            vel_y = 0
            on_ground = True
            
        # 4. Dollar Collection
        if not dollar.collected and player_rect.colliderect(dollar.rect):
            dollar.collected = True
            playermoney += 1
            
        # 5. Dollar Update (Respawn Timer)
        dollar.update(dt)
        
    # --- Shared Timer Update (for messages to work in store/minigame) ---
    if tony_message_timer > 0:
        tony_message_timer -= dt
    if tony_message_timer <= 0 and not effect_active:
        tony_message_text = ""


    # 7. Animation Logic (Only if not paused/over/won)
    if not game_paused and not game_over and not game_won:
        # Only cycle frames if the effect is NOT active (i.e., when using the sprite sheet)
        if not effect_active:
            frame_index = 0 
            if moving:
                anim_timer += 10 * dt
                if anim_timer >= 1:
                    anim_timer = 0
                    frame_index = (frame_index + 1) % 4
            else:
                frame_index = 0


    # --------------------
    # DRAW
    # --------------------
    # --- INTRO DRAW ---
    
    if in_minigame:
        draw_minigame_ui()

        # Display Mini-Game Feedback Message
        if tony_message_text and tony_message_timer > 0:
            message = small_font.render(tony_message_text, True, (255, 255, 255))
            message_rect = message.get_rect(center=(WIDTH // 2, HEIGHT - 100))
            screen.blit(message, message_rect)

    elif in_store:
        draw_store_ui()
        
        # Money Stat (Top Right)
        money_text = money_font.render(f"Money: ${playermoney}", True, (255, 255, 0))
        screen.blit(money_text, (WIDTH - money_text.get_width() - 10, 10))
        
        # Display Transaction Feedback Message
        if tony_message_text and tony_message_timer > 0:
            message = small_font.render(tony_message_text, True, (255, 255, 255))
            message_rect = message.get_rect(center=(WIDTH // 2, HEIGHT - 100))
            screen.blit(message, message_rect)
        
    else:
        # --- NORMAL GAME DRAWING ---
        screen.blit(background, (0, 00))

        # Tent
        if tent_open:
            screen.blit(tent_open_img, tent_rect.topleft)
        else:
            screen.blit(tent_closed_img, tent_rect.topleft)
            
        # Sign 
        screen.blit(sign_img, sign_rect.topleft)

        # Tony
        screen.blit(tony_img, tony_rect.topleft) 
        
        #bus
        screen.blit(bus_img, bus_rect.topleft)

        # Dollar
        dollar.draw(screen)

        # Player Drawing Logic
        if effect_active:
            screen.blit(fold_img, player_rect.topleft)
        elif not game_over:
            current_frame = frames[frame_index].copy()
            screen.blit(current_frame, player_rect.topleft)
        
        # Prompts
        if player_rect.colliderect(tent_rect) and not sleeping:
            if not effect_active:
                prompt = small_font.render("Press Q to sleep", True, (255, 255, 255))
            else:
                 prompt = small_font.render("Can't sleep you high as shit", True, (255, 0, 0))
            screen.blit(prompt, (tent_rect.x - 10, tent_rect.y - 20))

        if player_rect.colliderect(bus_rect) and not sleeping:
            bus_prompt = small_font.render(f"Press Q to enter casino Area.", True, (255, 255, 255))
            screen.blit(bus_prompt, (bus_rect.x - 30, bus_rect.y - 20))

        if player_rect.colliderect(tony_rect) and not sleeping:
            tony_prompt = small_font.render(f"Press E to buy fent (${HOTDOG_COST})", True, (255, 255, 255))
            screen.blit(tony_prompt, (tony_rect.x - 30, tony_rect.y - 20))

        # Tony Message (Feedback)
        if tony_message_text and not in_store and not in_minigame:
            message = small_font.render(tony_message_text, True, (255, 255, 255))
            screen.blit(message, (tony_rect.x - 20, tony_rect.y - 40))
        
        if player_rect.colliderect(sign_rect) and not sleeping:
            prompt = small_font.render(f"Press E to enter 7/11", True, (255, 255, 255))
            screen.blit(prompt, (sign_rect.x - 20, sign_rect.y - 20))


        # Money Stat (Top Right)
        money_text = money_font.render(f"Money: ${playermoney}", True, (255, 255, 0))
        screen.blit(money_text, (WIDTH - money_text.get_width() - 10, 10))
        
        # Geek Level Stat (Top Left)
        level_text = money_font.render(f"Geek Level: {geek_level}/{GEEK_LEVEL_MAX}", True, (255, 0, 255))
        screen.blit(level_text, (10, 10))
        
        # --- ITEM BAR (INVENTORY) ---
        ITEM_BAR_HEIGHT = 45
        ITEM_BAR_Y = HEIGHT - ITEM_BAR_HEIGHT
        
        pygame.draw.rect(screen, (50, 50, 50), (0, ITEM_BAR_Y, WIDTH, ITEM_BAR_HEIGHT))
        
        inventory_slots = [
            (hotdog_icon, hotdogs_bought, pygame.K_1, "Use"),
            (soda_icon, soda_bought, pygame.K_2, "Use"),
            (geek_icon, geek_bought, pygame.K_3, "Use") 
        ]
        
        start_x = WIDTH // 2 - (len(inventory_slots) * 50) 
        
        for i, (icon, quantity, key, action) in enumerate(inventory_slots):
            slot_x = start_x + i * 100
            slot_y = ITEM_BAR_Y + 0
            
            border_color = (255, 0, 0) if i == 0 and effect_active else (100, 100, 100)
            pygame.draw.rect(screen, border_color, (slot_x - 2, slot_y - 2, 36, 36), 2)
            
            screen.blit(icon, (slot_x, slot_y))
            
            qty_text = inventory_font.render(f"x{quantity}", True, (255, 255, 255))
            screen.blit(qty_text, (slot_x + 32 + 5, slot_y + 10))
            
            key_name = pygame.key.name(key).upper()
            use_prompt = inventory_font.render(f"Press {key_name} to {action}", True, (255, 255, 255))
            screen.blit(use_prompt, (slot_x - 10, slot_y + 25 + 5))


        # --- EFFECT STATUS OVERLAY ---
        if effect_active:
            elapsed_time = pygame.time.get_ticks() - effect_start_time
            remaining_ms = INVERT_DURATION - elapsed_time
            remaining_s = max(0, remaining_ms // 1000)
            
            effect_text = font.render("FENT HIGH", True, (255, 0, 0))
            timer_text = small_font.render(f"Time Remaining: {remaining_s}s", True, (255, 0, 0))
            
            text_rect = effect_text.get_rect(center=(WIDTH // 2, 50))
            timer_rect = timer_text.get_rect(center=(WIDTH // 2, 85))
            
            screen.blit(effect_text, text_rect)
            screen.blit(timer_text, timer_rect)
        # --- SODA TIMER LOGIC ---
        if soda_active:
            soda_text = small_font.render("you lowkey drunk bro", True, (0, 200, 255))
            screen.blit(soda_text, (WIDTH // 2 - soda_text.get_width() // 2, 110))
            elapsed_soda = pygame.time.get_ticks() - soda_start_time
            if elapsed_soda >= SODA_DURATION:
                soda_active = False
                current_move_speed -= SODA_SPEED_BOOST
                tony_message_text = "drunk is gone"
                tony_message_timer = TONY_MESSAGE_DURATION
    # Sleeping overlay
    if sleeping:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        text = font.render("Sleeping", True, (255, 255, 255))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, rect)

        wake = small_font.render("Press Q to wake up", True, (200, 200, 200))
        wake_rect = wake.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(wake, wake_rect)

    # --- GAME OVER OVERLAY ---
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(230)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        text = font.render("GAME OVER", True, (255, 0, 0))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(text, rect)

        level_reached_text = small_font.render(f"Geek Level Reached: {geek_level}", True, (255, 255, 255))
        level_rect = level_reached_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(level_reached_text, level_rect)

        quit_text = small_font.render("Press ESC to Quit", True, (200, 200, 200))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(quit_text, quit_rect)
    
    # --- NEW: WIN SCREEN OVERLAY ---
    if game_won:
        draw_win_screen()
    # -----------------------------
pygame.display.flip()
pygame.quit()
sys.exit()