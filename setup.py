import pygame,os
from random import randint
import openglfunctions as oglf
pygame.init()
game_version = "1.00"
window_size =  window_width, window_height = 1920, 1080
window_ratio = window_width/window_height

oglf.initializeDisplay(window_width, window_height)

pygame.display.set_caption("Kansas v."+game_version)


clock = pygame.time.Clock()
graphic_frame, logic_frame, target_frame = 0, 0, 0
map_size_x, map_size_y = 800, 800
camera_pos_x, camera_pos_y = map_size_x//2, map_size_y//2
camera_default_size_x, camera_default_size_y = window_width/5, window_height/5
camera_size_x, camera_size_y = camera_default_size_x, camera_default_size_y
last_entity_id = 0
player_team = "blue"
hud_active = True
selected = []
selected_team = True
selected_types = dict()
entities = []
game_console = []
DEBUG = True



team_colors={"red":(200,10,10),"blue":(20,100,200),"green":(21,237,21),"yellow":(217,188,24)}

units = ("villager","knight")

unit_stats = {
    "red": {
        "villager": {
            "defence": 2,
            "attack": 1,
            "speed": 3,
            "cost_food": 20,
            "cost_gold": 0,
            "cost_wood": 0,
            "cost_room": 1,
            "max_hp": 20,
            "speed_food": 10,
            "speed_gold": 10,
            "speed_wood": 10,
            "speed_build": 5,
            "max_carry": 20,
            "spawn_time": 3
        },
        "knight": {
            "defence": 5,
            "attack": 5,
            "speed": 3,
            "max_hp": 50,
            "cost_food": 40,
            "cost_gold": 40,
            "cost_wood": 0,
            "cost_room": 1,
            "spawn_time": 8
        }
    }
}
for team,color in team_colors.items():
    unit_stats[team] = unit_stats["red"].copy()



ground_set = oglf.Textureset()
fps_set = oglf.Textureset()
shadow_set = oglf.Textureset()
hud_set = oglf.Textureset()
black_set = oglf.Textureset()
text_set = oglf.Textureset()

sprites = {}

ani_standard = {
    "idle_s": ((0, 0), (0, 3)),
    "idle_w": ((1, 0), (1, 3)),
    "idle_n": ((2, 0), (2, 3)),
    "idle_e": ((3, 0), (3, 3)),
    "walk_s": ((0, 0), (0, 1), (0, 0), (0, 2)),
    "walk_w": ((1, 0), (1, 1), (1, 0), (1, 2)),
    "walk_n": ((2, 0), (2, 1), (2, 0), (2, 2)),
    "walk_e": ((3, 0), (3, 1), (3, 0), (3, 2)),
    "build_s": ((0, 4), (0, 5)),
    "build_w": ((1, 4), (1, 5)),
    "build_n": ((2, 4), (2, 5)),
    "build_e": ((3, 4), (3, 5)),
    "attack_s": ((0, 4), (0, 5)),
    "attack_w": ((1, 4), (1, 5)),
    "attack_n": ((2, 4), (2, 5)),
    "attack_e": ((3, 4), (3, 5))
    }


for team, color in team_colors.items():
    for unit in units:
        img = pygame.image.load(os.path.join("img", "units", unit+".png"))
        for x in range(img.get_width()):
            for y in range(img.get_height()):
                if img.get_at((x, y)) == (0, 255, 0):
                    img.set_at((x, y), color[::-1])
        ts = oglf.Textureset()
        for anim_n, anim_d in ani_standard.items():
            for frame_num, frame_d in enumerate(anim_d):
                cut = pygame.Surface((16,16))
                rect = pygame.Rect((frame_d[0]*16, frame_d[1]*16), (16, 16))
                cut.blit(img, (0, 0), area=rect)

                cut.set_colorkey((255, 0, 255))
                
                ts.load(anim_n+str(frame_num), cut)
        
        sprites[team+unit]=ts

img = pygame.image.load(os.path.join("img", "hud", "target.png"))
for x in range(4):
    cut = pygame.Surface((8, 8))
    rect = pygame.Rect((0, x*8), (8, 8))
    cut.blit(img, (0, 0), area=rect)
    cut.set_colorkey((255, 0, 255))
    hud_set.load("target"+str(x), cut)

up_holding, down_holding, left_holding, right_holding = False, False, False, False
lmb_holding, rmb_holding, cmb_holding = False, False, False
ctrl_holding, alt_holding, shift_holding = False, False, False
lmb_hold_ax, lmb_hold_ay = 0.0, 0.0
lmb_hold_bx, lmb_hold_by = 0.0, 0.0

font_console = pygame.font.SysFont("Consolas", 24, bold=True)

map_img = pygame.image.load("map.png")
ground_grass_img = pygame.image.load(os.path.join("img", "terrain", "grass.png"))
ground_sand_img = pygame.image.load(os.path.join("img", "terrain", "sand.png"))

ground_grass_img.set_colorkey((255, 0, 255))
ground_sand_img.set_colorkey((255, 0, 255))

unit_villager_img = pygame.image.load(os.path.join("img", "units", "villager.png"))

ground_surface = pygame.Surface((map_size_x*16+8, map_size_y*16+8))
ground_surface.fill((255, 0, 255))
ground_surface.set_colorkey((255, 0, 255))
for x in range(map_size_x):
    for y in range(map_size_y):
        if map_img.get_at((x, y))==(0, 0, 0, 255):
            ground_surface.blit(ground_grass_img, (x*16, y*16))
        else:
            ground_surface.blit(ground_sand_img, (x*16, y*16))

shadow = pygame.Surface((10, 5), flags=pygame.SRCALPHA)
pygame.draw.ellipse(shadow, (0, 0, 0, 63), (0, 0, 10, 5))

black = pygame.Surface((16, 16))
pygame.draw.rect(black, (140, 140, 140), (0, 0, 16, 16))

selecting_rectangle = pygame.Surface((1, 1), flags=pygame.SRCALPHA)
selecting_rectangle.set_at((0, 0), (255, 255, 255, 50))
hud_set.load("selecting_rectangle", selecting_rectangle)

health_bar = pygame.Surface((1, 1))
health_bar.set_at((0, 0), (255, 0, 0))
hud_set.load("health_red", health_bar)
health_bar.set_at((0, 0), (0, 255, 0))
hud_set.load("health_green", health_bar)

hud_scalar = 1+(window_height-600)/480
hud_dec_sc = int(hud_scalar*10)

hud_bottom_container = pygame.Surface((40*hud_dec_sc, 16*hud_dec_sc))
pygame.draw.rect(hud_bottom_container, (178, 176, 151), (0, 0, 40*hud_dec_sc, 16*hud_dec_sc))
hud_set.load("bottom_container", hud_bottom_container)

hud_top_container = pygame.Surface((window_width, 3*hud_dec_sc))
pygame.draw.rect(hud_top_container, (178, 176, 151), (0, 0, window_width, 3*hud_dec_sc))
hud_set.load("top_container", hud_top_container)

for icon in ("food", "gold", "room", "wood", "hp", "attack", "defence"):
    img = pygame.image.load(os.path.join("img", "hud", "icons", icon+".png"))
    img = pygame.transform.scale(img, (hud_dec_sc*2, hud_dec_sc*2))
    img.set_colorkey((255, 0, 255))
    hud_set.load("icon_"+icon, img)
    
for team, color in team_colors.items():
    for unit in units:
        img = pygame.image.load(os.path.join("img", "hud", "portraits", unit+".png"))

        for x in range(img.get_width()):
            for y in range(img.get_height()):
                if img.get_at((x, y)) == (0, 255, 0):
                    img.set_at((x, y), color[::-1])
        
        img.set_colorkey((255, 0, 255))
        hud_set.load("portrait_"+team+"_"+unit, img)

font_hud = pygame.font.SysFont("Consolas", int(hud_dec_sc*2))

black_set.load("black", black)
shadow_set.load("shadow", shadow)


class ConsoleMessage():
    def __init__(self, message, date):
        self.message = message
        self.date = date
