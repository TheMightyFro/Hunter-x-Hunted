import pygame
import datetime
import time
import random
import math

pygame.init()
pygame.mixer.init()

MENU_MUSIC = "menu_music.mp3"
GAME_MUSIC = "music_game.ogg"

MUSIC_VOLUME = 0.45
music_muted = False
current_music_volume = MUSIC_VOLUME

sfx_muted = False

show_controls = False

BLINK_INTERVAL = 1.0
shake_timer = 0.0
shake_intensity = 8

flash_timer = 0.0
FLASH_DURATION = 0.15

slowmo_timer = 0.0
SLOWMO_DURATION = 0.25
SLOWMO_SCALE = 0.25

info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
FULL_WIDTH,FULL_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
WINDOWED_WIDTH, WINDOWED_HEIGHT = 1200, 600
is_fullscreen = True

def play_sfx(sound):
	if not sfx_muted:
	  sound.play()

def play_menu_music():
	global current_music_volume
	pygame.mixer.music.stop()
	pygame.mixer.music.load(MENU_MUSIC)
	pygame.mixer.music.set_volume(current_music_volume)
	pygame.mixer.music.play(-1)

def play_game_music():
	global current_music_volume
	pygame.mixer.music.stop()
	pygame.mixer.music.load(GAME_MUSIC)
	pygame.mixer.music.set_volume(current_music_volume)
	pygame.mixer.music.play(-1)

HUD_HEIGHT = 80

MENU_BUTTON_WIDTH = 140
MENU_BUTTON_HEIGHT = 40
BUTTON_SPACING = 10

menu_button_rect = pygame.Rect(0, 0, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
restart_button_rect = pygame.Rect(0,0, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
controls_button_rect = pygame.Rect(0, 0, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)

ICON_BUTTON_SIZE = 40
music_button_rect = pygame.Rect(0, 0, ICON_BUTTON_SIZE, ICON_BUTTON_SIZE)
sfx_button_rect = pygame.Rect(0, 0, ICON_BUTTON_SIZE, ICON_BUTTON_SIZE)
fullscreen_button_rect = pygame.Rect(0, 0, ICON_BUTTON_SIZE, ICON_BUTTON_SIZE)

MIN_OBSTACLE_SPEED = 0.6

ARENA_LEFT = 0
ARENA_TOP = HUD_HEIGHT
ARENA_RIGHT = SCREEN_WIDTH
ARENA_BOTTOM = SCREEN_HEIGHT

BASE_HUNTER_SPEED = 2
BASE_HUNTER_SPRINT = 4

BASE_HUNTED_SPEED = 2
BASE_HUNTED_SPRINT = 4

FAST_HUNTER_SPEED = 4
FAST_HUNTER_SPRINT = 6

FAST_HUNTED_SPEED = 4
FAST_HUNTED_SPRINT = 6

P1_STAMINA_MAX = 100
P2_STAMINA_MAX = 100
p1_stamina = P1_STAMINA_MAX
p2_stamina = P2_STAMINA_MAX

P1_DASH_KEY = pygame.K_LALT
P2_DASH_KEY = pygame.K_RALT

DASH_DURATION = 0.18
DASH_COOLDOWN = 4.0
DASH_SPEED_MULTIPLIER = 5.0

p1_dashing = False
p2_dashing = False
p1_dash_timer = 0.0
p2_dash_timer = 0.0
p1_dash_cooldown = 0.0
p2_dash_cooldown = 0.0

p1_dash_trail = []
p2_dash_trail = []
DASH_TRAIL_LIFETIME = 0.25

STAMINA_DRAIN = 40.0
STAMINA_REGEN = 25.0

ROUND_TIME = 60
INTRO_DURATION = 3
HALF_TIME_THRESHOLD = 30

ARENA_COLOR = (50, 50, 50) 

state = "menu"
intro_start_time = None

pygame.display.set_caption("Hunter x Hunted")


start_image_original = pygame.image.load("start_screen.png")
start_image = start_image_original

frame_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

def apply_display_mode():
	global screen, frame_surface, SCREEN_WIDTH, SCREEN_HEIGHT, start_image, ARENA_RIGHT, ARENA_BOTTOM 

	if is_fullscreen:
	  SCREEN_WIDTH, SCREEN_HEIGHT = FULL_WIDTH, FULL_HEIGHT
	  flags = pygame.FULLSCREEN
	else:
	  SCREEN_WIDTH, SCREEN_HEIGHT = WINDOWED_WIDTH, WINDOWED_HEIGHT
	  flags = 0

	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
	frame_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

	ARENA_RIGHT = SCREEN_WIDTH
	ARENA_BOTTOM = SCREEN_HEIGHT

	start_image = pygame.transform.scale(start_image_original, (SCREEN_WIDTH, SCREEN_HEIGHT)).convert()

	y = (HUD_HEIGHT - MENU_BUTTON_HEIGHT) // 2
	x = 20

	menu_button_rect.x = x
	menu_button_rect.y = y

	x += MENU_BUTTON_WIDTH + BUTTON_SPACING
	restart_button_rect.x = x
	restart_button_rect.y = y

	x += MENU_BUTTON_WIDTH + BUTTON_SPACING
	controls_button_rect.x = x
	controls_button_rect.y = y

	icon_y = (HUD_HEIGHT - ICON_BUTTON_SIZE) // 2
	x_right = SCREEN_WIDTH - ICON_BUTTON_SIZE - 20

	fullscreen_button_rect.x = x_right
	fullscreen_button_rect.y = icon_y

	x_right -= ICON_BUTTON_SIZE + BUTTON_SPACING
	sfx_button_rect.x = x_right
	sfx_button_rect.y = icon_y

	x_right -= ICON_BUTTON_SIZE + BUTTON_SPACING
	music_button_rect.x = x_right
	music_button_rect.y = icon_y

apply_display_mode()
play_menu_music()

def toggle_fullscreen():
	global is_fullscreen
	is_fullscreen = not is_fullscreen
	apply_display_mode()


clock = pygame.time.Clock()

arena_center_y = ARENA_TOP + (ARENA_BOTTOM - ARENA_TOP) // 2

P1_START = (50, arena_center_y)
P2_START = (SCREEN_WIDTH -75, arena_center_y)

P1_INTRO_START = (-100, arena_center_y)
P2_INTRO_START = (SCREEN_WIDTH + 100, arena_center_y)

p1_rect = pygame.Rect((*P1_INTRO_START, 50, 50))
p2_rect = pygame.Rect((*P2_INTRO_START, 25, 25))

title_font = pygame.font.SysFont('Vivaldi', 80)
menu_font = pygame.font.SysFont('msgothic', 32)
timer_font = pygame.font.SysFont('msgothic', 45)
clock_font = pygame.font.SysFont('msgothic', 20)
flavor_font = pygame.font.SysFont('Vivaldi', 30)
intro_font = pygame.font.SysFont('Vivaldi', 50)
result_font = pygame.font.SysFont('Vivaldi', 45)
score_font = pygame.font.SysFont('msgothic', 26)
hud_small_font = pygame.font.SysFont("msgothic", 18)
hunger_font = pygame.font.SysFont("Vivaldi", 70)

p1_score = 0
p2_score = 0
current_round = 1
MAX_ROUNDS = 3
p1_is_hunter = True
round_winner_text = ""
match_winner_text = ""
timer_start = 0

round_end_time_left = 0
round_end_was_catch = False

sfx_menu = pygame.mixer.Sound("sfx_menu.wav")
sfx_hit = pygame.mixer.Sound("sfx_hit.wav")
sfx_powerup = pygame.mixer.Sound("sfx_powerup.wav")
sfx_slow = pygame.mixer.Sound("sfx_slow.wav")

sfx_menu.set_volume(0.6)
sfx_hit.set_volume(0.8)
sfx_powerup.set_volume(0.7)
sfx_slow.set_volume(0.7)

pending_hit = False
particles = []

HUNGER_TEXT = "The Hunger Grows!"
HUNGER_POPUP_DURATION = 2.5

hunger_popup_timer = 0.0
hunger_was_active = False

POWERUP_SIZE = 24
POWERUP_DURATION = 2.0
POWERUP_MULTIPLIER = 1.7

SLOW_MULTIPLIER = 0.6

POWERUP_TYPE_SPEED = "speed"
POWERUP_TYPE_SLOW = "slow"

powerup_rect = None
powerup_type = None

powerup_dx = 0.0
powerup_dy = 0.0

POWERUP_MIN_SPEED = 0.8
POWERUP_MAX_SPEED = 1.6

POWERUP_MIN_COMPONENT = 0.4

p1_speed_timer = 0.0
p2_speed_timer = 0.0
p1_slow_timer = 0.0
p2_slow_timer = 0.0

POWERUP_LIFETIME = 8.0
powerup_timer = 0.0

POWERUP_SPAWN_INTERVAL_MIN = 4.0
POWERUP_SPAWN_INTERVAL_MAX = 9.0
powerup_spawn_cooldown = 0.0

NUM_OBSTACLES = 4
OBSTACLE_MIN_SIZE = 60
OBSTACLE_MAX_SIZE = 130
OBSTACLE_MIN_SPEED = 0.8
OBSTACLE_MAX_SPEED = 1.8

obstacles = []

def setup_round_intro_rects():
	global p1_rect, p2_rect
	if p1_is_hunter:
	  p1_size = (50, 50)
	  p2_size = (25, 25)
	else:
	   p1_size = (25, 25)
	   p2_size = (50, 50)

	p1_rect = pygame.Rect(P1_INTRO_START[0], P1_INTRO_START[1], *p1_size)
	p2_rect = pygame.Rect(P2_INTRO_START[0], P2_INTRO_START[1], *p2_size)

def draw_hud(surface):
	pygame.draw.rect(surface, (20, 20, 20), (0, 0, SCREEN_WIDTH, HUD_HEIGHT))

	draw_button(surface, menu_button_rect, "Menu")
	draw_button(surface, restart_button_rect, "Restart")
	draw_button(surface, controls_button_rect, "Controls", toggled=show_controls)

	draw_button(surface, music_button_rect, "M", toggled=music_muted)
	draw_button(surface, sfx_button_rect, "S", toggled=sfx_muted)
	draw_button(surface, fullscreen_button_rect, "F")

	draw_stamina_bars(surface)

def draw_glow(surface, rect, color):
	glow_rect = rect.inflate(20, 20)
	pygame.draw.rect(surface, color, glow_rect, border_radius=12)

def draw_dash_status(surface, rect, dash_ready, is_dashing, color):
  if is_dashing:
    aura_rect = rect.inflate(16, 16)
    pygame.draw.rect(surface, color, aura_rect, width=3, border_radius=14)
  elif dash_ready:
    aura_rect = rect.inflate(10, 10)
    pygame.draw.rect(surface, (220, 220, 220), aura_rect, width=2, border_radius=12)

def draw_button(surface, rect, label, toggled=False):

	base_color = (60, 60, 60) if not toggled else (90, 90, 90)
	border_color = (200, 200, 200)

	pygame.draw.rect(surface, base_color, rect, border_radius=8)
	
	pygame.draw.rect(surface, border_color, rect, 2, border_radius=8)

	label_surf = menu_font.render(label, True, (255, 255, 255,))
	label_rect = label_surf.get_rect(center=rect.center)
	surface.blit(label_surf, label_rect)



def get_arena_rect():
	return pygame.Rect(ARENA_LEFT, ARENA_TOP, ARENA_RIGHT - ARENA_LEFT, ARENA_BOTTOM - ARENA_TOP)

def draw_grid(surface, spacing=50, color=(40, 40, 40)):
	arena = get_arena_rect()
	
	for x in range(arena.left, arena.right, spacing):
		pygame.draw.line(surface, color, (x, arena.top), (x, arena.bottom))
	for y in range(arena.top, arena.bottom, spacing):
		pygame.draw.line(surface, color, (arena.left, y), (arena.right, y))

def start_round():
	global p1_rect, p2_rect, timer_start
	global powerup_rect, powerup_type, pending_hit, slowmo_timer
	global p1_speed_timer, p2_speed_timer, p1_slow_timer, p2_slow_timer
	global powerup_timer, powerup_spawn_cooldown
	global p1_stamina, p2_stamina
	global p1_dashing, p2_dashing, p1_dash_timer, p2_dash_timer, p1_dash_cooldown, p2_dash_cooldown
	global p1_dash_trail, p2_dash_trail
	global powerup_dx, powerup_dy

	timer_start = time.time()

	p1_speed_timer = 0.0
	p2_speed_timer = 0.0
	p1_slow_timer = 0.0
	p2_slow_timer = 0.0

	p1_stamina = P1_STAMINA_MAX
	p2_stamina = P2_STAMINA_MAX

	pending_hit = False
	slowmo_timer = 0.0
	powerup_rect = None
	powerup_type = None
	powerup_timer = 0.0
	powerup_dx = 0.0
	powerup_dy = 0.0

	powerup_spawn_cooldown = random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)

	p1_dashing = False
	p2_dashing = False
	p1_dash_timer = 0.0
	p2_dash_timer = 0.0
	p1_dash_cooldown = 0.0
	p2_dash_cooldown = 0.0
	p1_dash_trail = []
	p2_dash_trail = []

	if p1_is_hunter:
	  p1_size = (50, 50)
	  p2_size = (25, 25)
	else:
	  p1_size = (25, 25)
	  p2_size = (50, 50)

	p1_rect = pygame.Rect(P1_START[0], P1_START[1], *p1_size)
	p2_rect = pygame.Rect(P2_START[0], P2_START[1], *p2_size)

	create_obstacles()

def end_round(hunter_won: bool, time_left: int):
	global p1_score, p2_score, current_round, p1_is_hunter
	global state, round_winner_text, match_winner_text
	global shake_timer, flash_timer, slowmo_timer
	global round_end_time_left, round_end_was_catch

	round_end_time_left = time_left
	round_end_was_catch = hunter_won

	if hunter_won:
	  shake_timer = 0.4
	  flash_timer = FLASH_DURATION
	  if p1_is_hunter:
		  p1_score += 1
		  round_winner_text = "Hunter (P1) catches Hunted (P2)!"
	  else:
		    p2_score += 1
		    round_winner_text = "Hunter (P2) catches Hunted!(P1)"
	else:
		if p1_is_hunter:
		  p2_score += 1
		  round_winner_text = "Hunted (P2) survives the round!"
		else:
		  p1_score += 1
		  round_winner_text = "Hunted (P1) survives the round!"

	if p1_score == 2 or p2_score == 2 or current_round == MAX_ROUNDS:
		if p1_score > p2_score:
		  match_winner_text = "Player 1 Wins the Match!"
		elif p2_score > p1_score:
		  match_winner_text = "Player 2 Wins the Match!"
		else:
		  match_winner_text = "The Match is a Draw!"

		state = "match_over"
	else:
	  current_round += 1
	  p1_is_hunter = not p1_is_hunter
	  state = "round_end"

def reset_match():
	global p1_score, p2_score, current_round, p1_is_hunter
	p1_score = 0
	p2_score = 0
	current_round = 1
	p1_is_hunter = True
	setup_round_intro_rects()

def draw_scoreboard(surface):

	left_limit = controls_button_rect.right
	right_limit = music_button_rect.left
	available = right_limit - left_limit
	if available <= 0:
	  return

	mid = (left_limit + right_limit) // 2
	center_x = (left_limit + right_limit) // 2
	center_y = int(HUD_HEIGHT * 0.60)

	badge_width = min(220, available - 20)
	badge_width = max(140, badge_width)
	badge_height = 34

	badge_rect = pygame.Rect(0, 0, badge_width, badge_height)
	badge_rect.center = (center_x, center_y)

	pygame.draw.rect(surface, (25, 25, 25), badge_rect, border_radius=12)
	pygame.draw.rect(surface, (140, 140, 140), badge_rect, 2, border_radius=12)

	num_rounds = MAX_ROUNDS
	spacing = 36
	total_width = spacing * (num_rounds - 1)
	start_x = badge_rect.centerx - total_width // 2
	cy = badge_rect.centery

	for i in range(num_rounds):
	  round_index = i + 1
	  cx = start_x + i * spacing
	  radius = 12


	  if round_index < current_round:
	    base_color = (80, 80, 80)
	  elif round_index == current_round:
	    base_color = (0, 200, 0)
	  else:
	    base_color = (120, 120, 120)

	  if (i + 1) < current_round:
	    color = (200, 200, 200)

	  pygame.draw.circle(surface, base_color, (cx, cy), radius)
	  pygame.draw.circle(surface, (255, 255, 255), (cx, cy), radius, 1)

	  label_surf = hud_small_font.render(str(round_index), True, (0, 0, 0))
	  label_rect = label_surf.get_rect(center=(cx, cy))
	  surface.blit(label_surf, label_rect)

	  if round_index < current_round:
	    offset = radius - 2
	    pygame.draw.line(surface, (255, 255, 255), (cx - offset, cy - offset), (cx + offset, cy + offset), 2,)
	    pygame.draw.line(surface, (255, 255, 255), (cx - offset, cy + offset), (cx + offset, cy - offset), 2,)

def draw_circle_timer(surface, center, radius, fraction, remaining_seconds, hunger_active=False):

	fraction = max(0.0, min(1.0, fraction))

	cx, cy = center

	bg_color = (40, 40, 40)
	
	if hunger_active:
	  fill_color = (220, 40, 40)
	else:
	  fill_color = (0, 200, 0)
	
	border_color = (255, 255, 255)

	if fraction > 0.0:
	  points = [(cx, cy)]
	  start_angle = -90.0
	  end_angle = start_angle + 360.0 * fraction
	  step = 6.0

	  angle = start_angle
	  while angle <= end_angle + 0.001:
	    rad = math.radians(angle)
	    x = cx + radius * math.cos(rad)
	    y = cy + radius * math.sin(rad)
	    points.append((x, y))
	    angle += step

	  pygame.draw.polygon(surface, fill_color, points)

	pygame.draw.circle(surface, border_color, (cx, cy), radius, 2)

	timer_text = hud_small_font.render(str(remaining_seconds), True, (255, 255, 255))
	text_rect = timer_text.get_rect(center=(cx, cy))
	surface.blit(timer_text, text_rect)

def draw_stamina_bars(surface):
	global p1_score, p2_score

	left_limit = controls_button_rect.right
	right_limit = music_button_rect.left

	total_available = right_limit - left_limit
	if total_available <= 0:
	  return
	
	margin_side = 16
	margin_between = 32
	max_bar_width = 220
	bar_height = 12

	bar_width = (total_available - margin_side * 2 - margin_between) // 2
	bar_width = max(80, min(bar_width, max_bar_width))

	y_bar = HUD_HEIGHT - bar_height - 8

	x1 = left_limit + margin_side
	bg1 = pygame.Rect(x1, y_bar, bar_width, bar_height)
	pygame.draw.rect(surface, (60, 60, 60), bg1)

	p1_ratio = p1_stamina / P1_STAMINA_MAX if P1_STAMINA_MAX > 0 else 0
	pygame.draw.rect(surface, (255, 80, 80), (x1, y_bar, int(bar_width * p1_ratio), bar_height))

	label1 = score_font.render("P1", True, (255, 255, 255))
	label1_rect = label1.get_rect()
	label1_rect.centery = bg1.centery
	label1_rect.left = bg1.left - 6
	surface.blit(label1, label1_rect)

	x2 = right_limit - margin_side - bar_width
	bg2 = pygame.Rect(x2, y_bar, bar_width, bar_height)
	pygame.draw.rect(surface, (60, 60, 60), bg2)

	p2_ratio = p2_stamina / P2_STAMINA_MAX if P2_STAMINA_MAX > 0 else 0
	pygame.draw.rect(surface, (80, 160, 255), (x2, y_bar, int(bar_width * p2_ratio), bar_height))

	label2 = score_font.render("P2", True, (255, 255, 255))
	label2_rect = label2.get_rect()
	label2_rect.centery = bg2.centery
	label2_rect.left = bg2.left + 6
	surface.blit(label2, label2_rect)

	pip_radius = 4
	pip_spacing = 14
	pip_offset_y = 6

	total_width_pips = (MAX_ROUNDS - 1) * pip_spacing
	start_x_p1 = bg1.centerx - total_width_pips / 2
	y_p1 = bg1.bottom + pip_offset_y

	for i in range(MAX_ROUNDS):
		cx = int(start_x_p1 + i * pip_spacing)
		color = (255, 255, 255) if p1_score > i else (80, 80, 80)
		pygame.draw.circle(surface, color, (cx, int(y_p1)), pip_radius)

		total_width_pips = (MAX_ROUNDS - 1) * pip_spacing
	start_x_p2 = bg2.centerx - total_width_pips / 2
	y_p2 = bg2.bottom + pip_offset_y

	for i in range(MAX_ROUNDS):
		cx = int(start_x_p2 + i * pip_spacing)
		color = (255, 255, 255) if p2_score > i else (80, 80, 80)
		pygame.draw.circle(surface, color, (cx, int(y_p2)), pip_radius)

	dash_radius = 6
	p1_dash_ready = (p1_dash_cooldown <= 0.0 and not p1_dashing)
	p1_dash_color = (255, 255, 255) if p1_dash_ready else (80, 80, 80)
	p1_dash_cx = bg1.centerx
	p1_dash_cy = bg1.top - 10
	pygame.draw.circle(surface, p1_dash_color, (p1_dash_cx, p1_dash_cy), dash_radius)
	pygame.draw.circle(surface, (0, 0, 0), (p1_dash_cx, p1_dash_cy), dash_radius, 1)

	p2_dash_ready = (p2_dash_cooldown <= 0.0 and not p2_dashing)
	p2_dash_color = (255, 255, 255) if p2_dash_ready else (80, 80, 80)
	p2_dash_cx = bg2.centerx
	p2_dash_cy = bg2.top - 10
	pygame.draw.circle(surface, p2_dash_color, (p2_dash_cx, p2_dash_cy), dash_radius)
	pygame.draw.circle(surface, (0, 0, 0), (p2_dash_cx, p2_dash_cy), dash_radius, 1)

def spawn_powerup():
	global powerup_rect, powerup_timer, powerup_type, powerup_dx, powerup_dy

	margin = 80
	arena_rect = get_arena_rect()

	max_attempts = 50
	rect = None

	for _ in range(max_attempts):
	  x = random.randint(arena_rect.left + margin, arena_rect.right - margin - POWERUP_SIZE)
	  y = random.randint(arena_rect.top + margin, arena_rect.bottom - margin - POWERUP_SIZE)

	  candidate = pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE)

	  if any(candidate.colliderect(o["rect"]) for o in obstacles):
	    continue

	  rect = candidate
	  break

	if rect is None:
	  powerup_rect = None
	  powerup_type = None
	  powerup_timer = 0.0
	  powerup_dx = 0.0
	  powerup_dy = 0.0
	  return

	powerup_rect = rect
	powerup_type = random.choice([POWERUP_TYPE_SPEED, POWERUP_TYPE_SLOW])
	powerup_timer = POWERUP_LIFETIME

	speed = random.uniform(POWERUP_MIN_SPEED, POWERUP_MAX_SPEED)
	
	while True:
	  angle = random.uniform(0, 2 * math.pi)
	  dx = math.cos(angle) * speed
	  dy = math.sin(angle) * speed

	  if abs(dx) >= POWERUP_MIN_COMPONENT and abs(dy) >= POWERUP_MIN_COMPONENT:
	    powerup_dx = dx
	    powerup_dy = dy
	    break


def spawn_particles(x, y, count=40):
	for _ in range(count):
	  particles.append({
	  "x": x,
	  "y": y,
	  "dx": random.uniform(-5, 5),
	  "dy": random.uniform(-5, 5),
	  "life": random.uniform(0.3, 0.6)
	  })

def create_obstacles():
  global obstacles
  obstacles = []

  margin = 80
  arena_rect = get_arena_rect()

  for _ in range(NUM_OBSTACLES):
      w = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
      h = random.randint(OBSTACLE_MIN_SIZE // 2, OBSTACLE_MAX_SIZE)

      x = random.randint(arena_rect.left + margin, arena_rect.right - margin - w)
      y = random.randint(arena_rect.top + margin, arena_rect.bottom - margin - h)

      dx = random.choice([-1, 1]) * random.uniform(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)
      dy = random.choice([-1, 1]) * random.uniform(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)

      obstacles.append({
      "rect": pygame.Rect(x, y, w, h),
      "dx": dx,
      "dy": dy,
      })


def update_and_draw_dash_trail(surface, trail_list, color):
  for t in trail_list[:]:
    t["life"] -= 1 / 60.0
    if t["life"] <= 0:
      trail_list.remove(t)
      continue

    alpha = int(255 * (t["life"] / DASH_TRAIL_LIFETIME))
    if alpha < 0:
      alpha = 0

    ghost_rect = t["rect"].inflate(10, 10)
    ghost_surf = pygame.Surface(ghost_rect.size, pygame.SRCALPHA)
    ghost_surf.fill((*color, alpha))
    surface.blit(ghost_surf, ghost_rect.topleft)

def update_and_draw_particles(surface):
	for p in particles[:]:
	  p["x"] += p["dx"]
	  p["y"] += p["dy"]
	  p["life"] -= 1 / 60.0

	  if p["life"] <= 0:
	    particles.remove(p)
	    continue

	  alpha = int(255 * p["life"])
	  if alpha < 0:
	    alpha = 0

	  size = int(10 * p["life"]) + 2

	  particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
	  particle_surface.fill((255, 200, 50, alpha))
	  surface.blit(particle_surface, (p["x"], p["y"]))

def enforce_min_powerup_components():
  global powerup_dx, powerup_dy

  speed = math.hypot(powerup_dx, powerup_dy)
  if speed <= 0:
    return

  nx = powerup_dx / speed
  ny = powerup_dy / speed

  powerup_dx = nx * speed
  powerup_dy = ny * speed

  if abs(powerup_dx) < POWERUP_MIN_COMPONENT:
    powerup_dx = POWERUP_MIN_COMPONENT * (1 if powerup_dx >= 0 else -1)
  if abs(powerup_dy) < POWERUP_MIN_COMPONENT:
    powerup_dy = POWERUP_MIN_COMPONENT * (1 if powerup_dy >= 0 else -1)

font = pygame.font.SysFont('Vivaldi', 45)

text_p1_loss = "Hunter Wins!"
text_color = (0, 0, 0)
text_surface = font.render(text_p1_loss, True, text_color)
text_rect = text_surface.get_rect()
text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

run = True
while run:


	for event in pygame.event.get():
	  if event.type == pygame.QUIT:
	    run = False

	  if event.type == pygame.KEYDOWN:
	    if event.key == pygame.K_ESCAPE:
	      toggle_fullscreen()

	    elif event.key == pygame.K_RETURN:
	      if state == "menu":
	        play_sfx(sfx_menu)
	        play_game_music()
	        hit_x = SCREEN_WIDTH // 2
	        hit_y = int(SCREEN_HEIGHT * 0.80)
	        reset_match()
	        intro_start_time = time.time()
	        state = "intro"
	      elif state == "round_end":
	        play_sfx(sfx_menu)
	        setup_round_intro_rects()
	        intro_start_time = time.time()
	        state = "intro" 
	      elif state == "match_over":
	        play_sfx(sfx_menu)
	        reset_match()
	        intro_start_time = time.time()
	        state = "intro"
	    elif event.key == pygame.K_m and state == "match_over":
	      reset_match()
	      intro_start_time = None
	      state = "menu"
	      play_menu_music()

	    if state == "game":
	      if event.key == P1_DASH_KEY:
	        if (not p1_dashing) and p1_dash_cooldown <= 0.0:
	          p1_dashing = True
	          p1_dash_timer = DASH_DURATION
	          p1_dash_cooldown = DASH_COOLDOWN

	      if event.key == P2_DASH_KEY:
	        if (not p2_dashing) and p2_dash_cooldown <= 0.0:
	          p2_dashing = True
	          p2_dash_timer = DASH_DURATION
	          p2_dash_cooldown = DASH_COOLDOWN

	  if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
	    mx, my = event.pos

	    if state in ("intro", "game", "round_end", "match_over"):
	      if menu_button_rect.collidepoint((mx, my)):
	        reset_match()
	        intro_start_time = None
	        state = "menu"
	        play_menu_music()

	    if state in ("game", "round_end", "match_over"):
	      if restart_button_rect.collidepoint((mx, my)):
	        reset_match()
	        intro_start_time = time.time()
	        state = "intro"
	        play_game_music()

	    if controls_button_rect.collidepoint((mx, my)):
	      show_controls = not show_controls

	    if music_button_rect.collidepoint((mx, my)):
	      music_muted = not music_muted
	      if music_muted:
	        current_music_volume = 0.0
	      else:
	        current_music_volume = MUSIC_VOLUME
	      pygame.mixer.music.set_volume(current_music_volume)

	    if sfx_button_rect.collidepoint((mx, my)):
	    	sfx_muted = not sfx_muted

	    if fullscreen_button_rect.collidepoint((mx, my)):
	      toggle_fullscreen()


	if state == "menu":
		frame_surface.blit(start_image, (0, 0))
		
		prompt_surf = menu_font.render ("Press ENTER to start", True, (2, 97, 23))
		prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.80)))

		t = time.time() % BLINK_INTERVAL
		if t < BLINK_INTERVAL / 2:
		  frame_surface.blit(prompt_surf, prompt_rect)

	elif state == "intro":
		frame_surface.fill((ARENA_COLOR))
		draw_grid(frame_surface)
		draw_hud(frame_surface)
		draw_scoreboard(frame_surface)

		pygame.draw.rect(frame_surface, (20, 20, 20), (0, 0, SCREEN_WIDTH, HUD_HEIGHT))
		draw_hud(frame_surface)
		draw_scoreboard(frame_surface)

		t = (time.time() - intro_start_time) / INTRO_DURATION
		if t> 1:
			t = 1
	    
		p1_x = P1_INTRO_START[0] + (P1_START[0] - P1_INTRO_START[0]) * t
		p1_y = P1_INTRO_START[1]
		p1_rect.topleft = (int(p1_x), int(p1_y))

		p2_x = P2_INTRO_START[0] + (P2_START[0] - P2_INTRO_START[0]) * t
		p2_y = P2_INTRO_START[1]
		p2_rect.topleft = (int(p2_x), int(p2_y))

		p1_glow_color = (255, 80, 80)
		p2_glow_color = (80, 80, 255)

		if p1_is_hunter:
		    draw_glow(frame_surface, p1_rect, p1_glow_color)
		    draw_glow(frame_surface, p2_rect, p2_glow_color)
		else:
		    draw_glow(frame_surface, p1_rect, p2_glow_color)
		    draw_glow(frame_surface, p2_rect, p1_glow_color)

		if p1_is_hunter:
			pygame.draw.rect(frame_surface, (255, 0, 0), p1_rect)
			pygame.draw.rect(frame_surface, (0, 0, 255), p2_rect)
			roles_text = f"Round {current_round}: P1 = Hunter, P2 = Hunted"
		else:
			pygame.draw.rect(frame_surface, (0, 0, 255), p1_rect)
			pygame.draw.rect(frame_surface, (255, 0, 0), p2_rect)
			roles_text = f"Round {current_round}: P1 = Hunted, P2 = Hunter"

		intro_text = intro_font.render("Prepare for the Hunt!", True, (255, 255, 255))
		intro_rect = intro_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
		frame_surface.blit(intro_text, intro_rect)

		roles_surf = menu_font.render(roles_text, True, (200, 200, 200))
		roles_rect = roles_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 60))
		frame_surface.blit(roles_surf, roles_rect)

		if t >= 1.0:
		  start_round()
		  state = "game"

		intro_text = intro_font.render("Prepare for the Hunt!", True, (255, 255, 255))
		intro_rect = intro_text.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
		frame_surface.blit(intro_text, intro_rect)

		roles_surf = menu_font.render(roles_text, True, (200, 200, 200))
		roles_rect = roles_surf.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 60))
		frame_surface.blit(roles_surf, roles_rect)

		draw_scoreboard(frame_surface)


		if t >= 1.0:
			start_round()
			state = "game"

	elif state == "game":
	  frame_surface.fill((ARENA_COLOR))
	  draw_grid(frame_surface)

	  draw_hud(frame_surface)

	  dt = 1/60
	  if slowmo_timer > 0:
	    slowmo_timer -= dt
	    dt *= SLOWMO_SCALE

	  if p1_dashing:
	    p1_dash_timer -= dt
	    if p1_dash_timer <= 0.0:
	      p1_dashing = False

	  if p2_dashing:
	    p2_dash_timer -= dt
	    if p2_dash_timer <= 0.0:
	      p2_dashing = False

	  if p1_dash_cooldown > 0.0 and not p1_dashing:
	    p1_dash_cooldown -= dt
	    if p1_dash_cooldown < 0.0:
	      p1_dash_cooldown = 0.0

	  if p2_dash_cooldown > 0.0 and not p2_dashing:
	    p2_dash_cooldown -= dt
	    if p2_dash_cooldown < 0.0:
	      p2_dash_cooldown = 0.0

	  keys = pygame.key.get_pressed()

	  p1_sprinting = keys[pygame.K_LSHIFT]
	  p2_sprinting = keys[pygame.K_SPACE]

	  if p1_sprinting and p1_stamina > 0:
	    p1_stamina -= STAMINA_DRAIN * dt
	    if p1_stamina < 0:
	      p1_stamina = 0
	      p1_sprinting = False

	  else:
	    p1_stamina += STAMINA_REGEN * dt
	    if p1_stamina > P1_STAMINA_MAX:
	      p1_stamina = P1_STAMINA_MAX

	  if p2_sprinting and p2_stamina > 0:
	    p2_stamina -= STAMINA_DRAIN * dt
	    if p2_stamina < 0:
	      p2_stamina = 0
	      p2_sprinting = False

	  else:
	    p2_stamina += STAMINA_REGEN * dt
	    if p2_stamina > P2_STAMINA_MAX:
	      p2_stamina = P2_STAMINA_MAX

	  arena_rect = get_arena_rect()

	  for o in obstacles:
	    r = o["rect"]

	    r.x += o["dx"] * dt * 60
	    r.y += o["dy"] * dt * 60

	    if r.left < arena_rect.left:
	      r.left = arena_rect.left
	      o["dx"] *= -1
	      if 0 < abs(o["dx"]) < MIN_OBSTACLE_SPEED:
	        o["dx"] = MIN_OBSTACLE_SPEED * (1 if o["dx"] > 0 else -1)
	    elif r.right > arena_rect.right:
	      r.right = arena_rect.right
	      o["dx"] *= -1

	    if r.top < arena_rect.top:
	      r.top = arena_rect.top
	      o["dy"] *= -1
	      if 0 < abs(o["dy"]) < MIN_OBSTACLE_SPEED:
	        o["dy"] = MIN_OBSTACLE_SPEED * (1 if o["dy"] > 0 else -1)
	    elif r.bottom > arena_rect.bottom:
	      r.bottom = arena_rect.bottom
	      o["dy"] *= -1

	  if powerup_rect:
	    powerup_rect.x += powerup_dx * dt * 60

	    if powerup_rect.left < arena_rect.left:
	      powerup_rect.left = arena_rect.left
	      powerup_dx *= -1
	      enforce_min_powerup_components()
	    elif powerup_rect.right > arena_rect.right:
	      powerup_rect.right = arena_rect.right
	      powerup_dx *= -1
	      enforce_min_powerup_components()

	    for o in obstacles:
	      r = o["rect"]
	      if powerup_rect.colliderect(r):
	        if powerup_dx > 0:
	          powerup_rect.right = r.left

	        elif powerup_dx < 0:
	          powerup_rect.left = r.right
	        powerup_dx *= -1
	        enforce_min_powerup_components()

	    powerup_rect.y += powerup_dy * dt * 60

	    if powerup_rect.top < arena_rect.top:
	      powerup_rect.top = arena_rect.top
	      powerup_dy *= -1
	      enforce_min_powerup_components()
	    elif powerup_rect.bottom > arena_rect.bottom:
	      powerup_rect.bottom = arena_rect.bottom
	      powerup_dy *= -1
	      enforce_min_powerup_components()

	    for o in obstacles:
	      r = o["rect"]
	      if powerup_rect.colliderect(r):
	        if powerup_dy > 0:
	          powerup_rect.bottom = r.top
	        elif powerup_dy < 0:
	          powerup_rect.top = r.bottom
	        powerup_dy *= -1
	        enforce_min_powerup_components()

	  for o in obstacles:
	    r = o["rect"]
	    pygame.draw.rect(frame_surface, (30, 30, 30), r, border_radius=8)
	    pygame.draw.rect(frame_surface, (90, 90, 90), r, 2, border_radius=8)

	  elapsed_time = time.time() - timer_start
	  remaining_time = max(0, ROUND_TIME - int(elapsed_time))

	  if remaining_time > HALF_TIME_THRESHOLD:
	    hunter_speed = BASE_HUNTER_SPEED
	    hunter_sprint = BASE_HUNTER_SPRINT
	    hunted_speed = BASE_HUNTED_SPEED
	    hunted_sprint = BASE_HUNTED_SPRINT
	    hunger_active = False

	  else:
	    hunter_speed = FAST_HUNTER_SPEED
	    hunter_sprint = FAST_HUNTER_SPRINT
	    hunted_speed = FAST_HUNTED_SPEED
	    hunted_sprint = FAST_HUNTED_SPRINT
	    hunger_active = True

	  if hunger_active and not hunger_was_active:
	    hunger_popup_timer = HUNGER_POPUP_DURATION

	  hunger_was_active = hunger_active

	  if p1_is_hunter:
	    p1_base_speed = hunter_speed
	    p1_sprint_speed = hunter_sprint
	    p2_base_speed = hunted_speed
	    p2_sprint_speed = hunted_sprint
	    hunter_rect = p1_rect
	    hunted_rect = p2_rect

	  else:
	    p1_base_speed = hunted_speed
	    p1_sprint_speed = hunted_sprint
	    p2_base_speed = hunter_speed
	    p2_sprint_speed = hunter_sprint
	    hunter_rect = p2_rect
	    hunted_rect = p1_rect    	

	  p1_glow_color = (255, 80, 80)
	  p2_glow_color = (8, 80, 225)

	  if p1_is_hunter:
		  draw_glow(frame_surface, p1_rect, p1_glow_color)
		  draw_glow(frame_surface, p2_rect, p2_glow_color)
	  else:
		  draw_glow(frame_surface, p1_rect, p2_glow_color)
		  draw_glow(frame_surface, p2_rect, p1_glow_color)

	  if p1_is_hunter:
	    pygame.draw.rect(frame_surface, (255, 0, 0), p1_rect)
	    pygame.draw.rect(frame_surface, (0, 0, 255), p2_rect)

	  else:
	    pygame.draw.rect(frame_surface, (0, 0, 255), p1_rect)
	    pygame.draw.rect(frame_surface, (255, 0, 0), p2_rect)

	  if p1_is_hunter:
	    p1_color = (255, 0, 0)
	    p2_color = (0, 0, 255)
	  else:
	    p1_color = (0, 0, 255)
	    p2_color = (255, 0, 0)

	  p1_dash_ready = (p1_dash_cooldown <= 0.0 and not p1_dashing)
	  p2_dash_ready = (p2_dash_cooldown <= 0.0 and not p2_dashing)

	  draw_dash_status(frame_surface, p1_rect, p1_dash_ready, p1_dashing, p1_color)
	  draw_dash_status(frame_surface, p2_rect, p2_dash_ready, p2_dashing, p2_color)

	  update_and_draw_dash_trail(frame_surface, p1_dash_trail, p1_color)
	  update_and_draw_dash_trail(frame_surface, p2_dash_trail, p2_color)

	  left_limit = controls_button_rect.right
	  right_limit = music_button_rect.left
	  mid = (left_limit + right_limit) // 2

	  timer_center_x = (left_limit + mid) // 2
	  timer_center_y = int(HUD_HEIGHT * 0.30)

	  time_fraction = remaining_time / float(ROUND_TIME) if ROUND_TIME > 0 else 0.0

	  timer_radius = 18

	  draw_circle_timer(frame_surface, (timer_center_x, timer_center_y), timer_radius, time_fraction, remaining_time, hunger_active)

	  draw_scoreboard(frame_surface)

	  if hunger_popup_timer > 0.0:
	    hunger_popup_timer -= dt
	    if hunger_popup_timer < 0:
	      hunger_popup_timer = 0

	    t = 1.0 - (hunger_popup_timer / HUNGER_POPUP_DURATION)
	    t = max(0.0, min(1.0, t))

	    scale = 1.0 + 0.25 * math.sin(t * math.pi)

	    alpha = int(220 * (1.0 - t))

	    base_text_surf = hunger_font.render(HUNGER_TEXT, True, (255, 255, 255))
	    base_text_surf = base_text_surf.convert_alpha()

	    w, h = base_text_surf.get_size()
	    scaled_surf = pygame.transform.rotozoom(base_text_surf, 0, scale)
	    scaled_surf.set_alpha(alpha)

	    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
	    overlay.fill((0, 0, 0, int(alpha * 0.3)))
	    frame_surface.blit(overlay, (0, 0))

	    text_rect = scaled_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
	    frame_surface.blit(scaled_surf, text_rect)

	  if hunger_active:
	    small_surf = hud_small_font.render("The Hunger Grows", True, (255, 255, 255))
	    small_rect = small_surf.get_rect(center=(int(SCREEN_WIDTH * 0.8), int(HUD_HEIGHT * 0.3)))

	    frame_surface.blit(small_surf, small_rect)

	  if powerup_rect:
	    base_radius = powerup_rect.width // 2

	    if powerup_type == POWERUP_TYPE_SPEED:
	      outer_color = (255, 220, 80)
	      inner_color = (255, 255, 120)

	    else:
	      outer_color = (120, 200, 255)
	      inner_color = (190, 200, 255)

	    t = time.time() * 6.0
	    pulse = (math.sin(t) + 1.0) / 2.0

	    glow_radius = int(base_radius + 8 * pulse)
	    inner_radius = int(base_radius * (0.8 + 0.2 * pulse))
	    pygame.draw.circle(frame_surface, outer_color, powerup_rect.center, glow_radius)
	    pygame.draw.circle(frame_surface, inner_color, powerup_rect.center, inner_radius)

	  if p1_speed_timer > 0:
	    p1_speed_timer -= dt
	    if p1_speed_timer < 0:
	      p1_speed_timer = 0

	  if p2_speed_timer > 0:
	    p2_speed_timer -= dt
	    if p2_speed_timer < 0:
	      p2_speed_timer = 0

	  if p1_slow_timer > 0:
	    p1_slow_timer -= dt
	    if p1_slow_timer < 0:
	      p1_slow_timer = 0

	  if p2_slow_timer > 0:
	    p2_slow_timer -= dt
	    if p2_slow_timer < 0:
	      p2_slow_timer = 0

	  p1_mult = 1.0 
	  if p1_speed_timer > 0:
	    p1_mult *= POWERUP_MULTIPLIER
	  if p1_slow_timer > 0:
	    p1_mult *= SLOW_MULTIPLIER

	  p2_mult = 1.0 
	  if p2_speed_timer > 0:
	    p2_mult *= POWERUP_MULTIPLIER
	  if p2_slow_timer > 0:
	    p2_mult *= SLOW_MULTIPLIER

	  for o in obstacles:
	    r = o["rect"]
	    if p1_rect.colliderect(r) and not p1_dashing:
	      p1_mult *= SLOW_MULTIPLIER
	    if p2_rect.colliderect(r) and not p2_dashing:
	      p2_mult *= SLOW_MULTIPLIER

	  if powerup_rect:
	    powerup_timer -= dt
	    if powerup_timer <= 0:
	      powerup_rect = None
	      powerup_type = None
	      powerup_timer = 0.0
	      powerup_dx = 0.0
	      powerup_dy = 0.0
	      powerup_spawn_cooldown = random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)

	  else:
	    powerup_spawn_cooldown -= dt
	    if powerup_spawn_cooldown <= 0:
	      spawn_powerup()


	  if p1_dashing:
	    p1_speed_now = p1_base_speed * DASH_SPEED_MULTIPLIER * p1_mult
	  else:
	    p1_speed_now = (p1_sprint_speed if p1_sprinting else p1_base_speed) * p1_mult
	  dx1 = dy1 = 0
	  if keys[pygame.K_a]:
		  dx1 = -p1_speed_now * dt * 60
	  if keys[pygame.K_d]:
		  dx1 = p1_speed_now * dt * 60
	  if keys[pygame.K_w]:
		  dy1 = -p1_speed_now * dt * 60
	  if keys[pygame.K_s]:
		  dy1 = p1_speed_now * dt * 60
	  p1_rect.move_ip(dx1, dy1)
	  if p1_dashing and (dx1 != 0 or dy1 != 0):
	    p1_dash_trail.append({"rect": p1_rect.copy(),"life": DASH_TRAIL_LIFETIME})

	  if p2_dashing:
	    p2_speed_now = p2_base_speed * DASH_SPEED_MULTIPLIER * p2_mult
	  else:
	    p2_speed_now = (p2_sprint_speed if p2_sprinting else p2_base_speed) * p2_mult
	  dx2 = dy2 = 0
	  if keys[pygame.K_LEFT]:
		  dx2 = -p2_speed_now * dt * 60
	  if keys[pygame.K_RIGHT]:
		  dx2 = p2_speed_now * dt * 60
	  if keys[pygame.K_UP]:
		  dy2 = -p2_speed_now * dt * 60
	  if keys[pygame.K_DOWN]:
		  dy2 = p2_speed_now * dt * 60
	  p2_rect.move_ip(dx2, dy2)
	  if p2_dashing and (dx2 != 0 or dy2 != 0):
	    p2_dash_trail.append({"rect": p2_rect.copy(),"life": DASH_TRAIL_LIFETIME})

	  arena_rect = get_arena_rect()
	  p1_rect.clamp_ip(arena_rect)
	  p2_rect.clamp_ip(arena_rect)

	  hunter_hitbox = hunter_rect.inflate(20, 20)
	  hunted_hitbox = hunted_rect.inflate(20, 20)

	  if powerup_rect and p1_rect.colliderect(powerup_rect):
	    
	    if powerup_type == POWERUP_TYPE_SPEED:
	      play_sfx(sfx_powerup)
	    elif powerup_type == POWERUP_TYPE_SLOW:
	      play_sfx(sfx_slow)

	    if powerup_type == POWERUP_TYPE_SPEED:
	      p1_speed_timer = POWERUP_DURATION
	    else:
	      p2_slow_timer = POWERUP_DURATION

	    spawn_particles(powerup_rect.centerx, powerup_rect.centery)
	    powerup_rect = None
	    powerup_type = None
	    powerup_timer = 0.0
	    powerup_dx = 0.0
	    powerup_dy = 0.0
	    powerup_spawn_cooldown = random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)

	  elif powerup_rect and p2_rect.colliderect(powerup_rect):
	    

	    if powerup_type == POWERUP_TYPE_SPEED:
	      play_sfx(sfx_powerup)
	    elif powerup_type == POWERUP_TYPE_SLOW:
	      play_sfx(sfx_slow)

	    if powerup_type == POWERUP_TYPE_SPEED:
	      p2_speed_timer = POWERUP_DURATION
	    else:
	      p1_slow_timer = POWERUP_DURATION

	    spawn_particles(powerup_rect.centerx, powerup_rect.centery)
	    powerup_rect = None
	    powerup_type = None
	    powerup_timer = 0.0
	    powerup_dx = 0.0
	    powerup_dy = 0.0
	    powerup_spawn_cooldown = random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)

	  if remaining_time == 0 and not pending_hit:
	  	end_round(hunter_won=False, time_left=0)
	  
	  else:
		  if not pending_hit and hunter_hitbox.colliderect(hunted_hitbox):
		    pending_hit = True
		    slowmo_timer = SLOWMO_DURATION

		    play_sfx(sfx_hit)

		    hit_x = (hunter_hitbox.centerx + hunted_hitbox.centerx) // 2
		    hit_y = (hunter_hitbox.centery + hunted_hitbox.centery) // 2
		    spawn_particles(hit_x, hit_y)

		  if pending_hit and slowmo_timer <= 0:
		    pending_hit = False
		    end_round(hunter_won=True, time_left=remaining_time)


	elif state == "round_end":
	    frame_surface.fill((ARENA_COLOR))
	    draw_grid(frame_surface)
	    draw_hud(frame_surface)
	    draw_scoreboard(frame_surface)

	    round_text_surf = result_font.render(round_winner_text, True, (255, 255, 255))
	    round_text_rect = round_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
	    frame_surface.blit(round_text_surf, round_text_rect)

	    if round_end_was_catch:
	      time_msg = f"Time left when caught: {round_end_time_left}s"
	      time_surf = menu_font.render(time_msg, True, (200, 200, 200))
	      time_rect = time_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
	      frame_surface.blit(time_surf, time_rect)

	    prompt_surf = menu_font.render("Press ENTER for next round", True, (200, 200, 200))
	    prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
	    frame_surface.blit(prompt_surf, prompt_rect)

	elif state == "match_over":
	  frame_surface.fill((ARENA_COLOR))
	  draw_grid(frame_surface)
	  draw_hud(frame_surface)
	  match_text_surf = result_font.render(match_winner_text, True, (255, 255, 255))
	  match_text_rect = match_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
	  frame_surface.blit(match_text_surf, match_text_rect)

	  draw_scoreboard(frame_surface)

	  prompt_surf = menu_font.render("Press ENTER to play Again", True, (200, 200, 200))
	  prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
	  frame_surface.blit(prompt_surf, prompt_rect)

	  prompt_menu_surf = menu_font.render("Press M to return to Menu", True, (200, 200, 200))
	  prompt_menu_rect = prompt_menu_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
	  frame_surface.blit(prompt_menu_surf, prompt_menu_rect)

	update_and_draw_particles(frame_surface)

	if shake_timer > 0:
	  shake_timer -= 1 / 60
	  offset_x = random.randint(-shake_intensity, shake_intensity)
	  offset_y = random.randint(-shake_intensity, shake_intensity)
	else:
	  offset_x = 0
	  offset_y = 0

	if flash_timer > 0:
	  flash_timer -= 1 / 60
	  alpha = int(255 * (flash_timer / FLASH_DURATION))
	  if alpha < 0:
	    alpha = 0

	  flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
	  flash_surface.fill((255, 255, 255, alpha))
	  frame_surface.blit(flash_surface, (0, 0))

	if show_controls:
	  overlay_width = int(SCREEN_WIDTH * 0.6)
	  overlay_height = 200
	  overlay_x = (SCREEN_WIDTH - overlay_width) // 2
	  overlay_y = HUD_HEIGHT + 40

	  overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
	  overlay.fill((0, 0, 0, 200))

	  lines = [
	  "Controls",
	  "P1: WASD to move, LSHIFT to sprint, LEFT ALT to dash",
	  "P2: Arrow keys to move, SPACE to sprint, RIGHT ALT to dash",
	  "ESC: Toggle fullscreen",
	  "HUD: M=Music, S=SFX, F=Fullscreen",
	  "DASH: Ignores obstacles"
	  ]

	  y = 20
	  for line in lines:
	    txt = menu_font.render(line, True, (255, 255, 255))
	    rect = txt.get_rect(center=(overlay_width // 2, y))
	    overlay.blit(txt, rect)
	    y += 28

	  frame_surface.blit(overlay, (overlay_x, overlay_y))

	screen.fill((0, 0, 0))
	screen.blit(frame_surface, (offset_x, offset_y))

	pygame.display.update()

	clock.tick(60)

pygame.quit()