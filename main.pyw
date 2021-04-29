import os, pygame, math
from classes import *
from setup import *
from setup import selected

while 1:
    if pygame.get_init():
        break


def console_log(message, date=logic_frame):
    global game_console
    message = str(message)
    if date == -1:
        game_console[0] == ConsoleMessage(message, date)
    else:
        game_console += ConsoleMessage(message, date)


def between(x, a, b, inc=True):
    if a > b:
        a, b = b, a
    if inc:
        return a <= x <= b
    if not inc:
        return a < x < b


def in_rect(x, y, xa, ya, xb, yb, tolerance=0.0):
    if xa > xb:
        xa, xb = xb, xa
    if ya > yb:
        ya, yb = yb, ya
    return xa - tolerance < x < xb + tolerance and ya - tolerance < y < yb + tolerance


def m2w(x, y):  # mouse pos to world pos
    nx = ((x * camera_size_x / window_width) + camera_pos_x - 0.5 * camera_size_x) / 16
    ny = ((y * camera_size_y / window_height) + camera_pos_y - 0.5 * camera_size_y) / 16
    return nx, ny


def w2m(x, y):  # mouse pos to world pos
    nx = (window_width / camera_size_x) * (16 * x - camera_pos_x + 0.5 * camera_size_x)
    ny = (window_height / camera_size_y) * (16 * y - camera_pos_y + 0.5 * camera_size_y)
    return nx, ny


def select_from_mouse(x, y):
    global selected
    nx, ny = m2w(x, y)
    print(nx, ny)
    found = False
    for e in entities:
        if in_rect(e.x, e.y, nx - 1, ny - 1, nx, ny, 10):
            selected = e
            found = True
    if not found:
        selected = []


def get_y(e):
    return e.y


def select_area(xa, ya, xb, yb, tolerance=0.3):
    global selected
    global selected_team
    global selected_types
    selected = []
    selected_types = {}
    selected_team = False
    for e in entities:
        if in_rect(e.x, e.y, xa, ya, xb, yb, tolerance):
            if e.unit_team == player_team and not selected_team:
                selected_team = True
            selected.append(e)
            if e.unit_class in selected_types:
                selected_types[e.unit_class] += 1
            else:
                selected_types[e.unit_class] = 1
    for num, s in enumerate(selected):
        if selected_team and s.unit_team != player_team:
            selected.pop(num)
            selected_types[s.unit_class] -= 1
            if selected_types[s.unit_class] == 0:
                selected_types.pop(s.unit_class)


def draw_text(text, x, y):
    text = str(text)
    try:
        text_set.get(text)
    except:
        text_sur = font_hud.render(text, False, (0, 0, 0))
        text_sur = pygame.transform.flip(text_sur, False, True)
        text_set.load(text, text_sur)
    finally:
        text_sur = oglf.GL_Image(text_set, text)
        text_sur.draw(abspos=(int(x * hud_dec_sc), int(window_height - y * hud_dec_sc)))


def draw_icon(icon, x, y):
    sur = oglf.GL_Image(hud_set, "icon_" + str(icon))
    sur.draw(abspos=(int((x + 0.1) * hud_dec_sc), int(window_height - (y + 0.1) * hud_dec_sc)),
             width=int(1.8 * hud_dec_sc), height=int(-1.8 * hud_dec_sc))


def DEBUG_spawn_villager(x, y):
    global last_entity_id, entities
    villager = UnitVillager(last_entity_id, x, y, "blue")
    last_entity_id += 1
    entities.append(villager)
    return villager


def attack(attacker, defender):
    aa = unit_stats[attacker.unit_team][attacker.unit_class]["attack"]  # attackers attack
    dd = unit_stats[defender.unit_team][defender.unit_class]["defence"]  # defender defence
    dmg = int(math.ceil(aa / (0.7 + dd)))
    defender.unit_health -= dmg
    if defender.unit_health <= 0:
        entities.remove(defender)
        return True
    return False


def handle_input():
    global game_running
    global camera_pos_y, camera_pos_x
    global camera_size_x, camera_size_y

    global up_holding, down_holding, left_holding, right_holding
    global lmb_holding, rmb_holding, cmb_holding
    global ctrl_holding, alt_holding, shift_holding
    global lmb_hold_ax, lmb_hold_ay
    global lmb_hold_bx, lmb_hold_by

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            game_running = False
            pygame.quit()
            return 0
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                pygame.display.quit()
                game_running = False
                pygame.quit()
                return 0

            if event.key == pygame.K_UP:
                up_holding = True
            if event.key == pygame.K_DOWN:
                down_holding = True
            if event.key == pygame.K_LEFT:
                left_holding = True
            if event.key == pygame.K_RIGHT:
                right_holding = True

            if event.key == pygame.K_KP_PLUS:
                new_x = camera_size_x * 8 / 7
                new_y = camera_size_y * 8 / 7
                if new_x < window_height and new_y < window_width:
                    camera_size_x, camera_size_y = new_x, new_y
            if event.key == pygame.K_KP_MINUS:
                new_x = camera_size_x * 7 / 8
                new_y = camera_size_y * 7 / 8
                if new_x > 100 and new_y > 100:
                    camera_size_x, camera_size_y = new_x, new_y

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                up_holding = False
            if event.key == pygame.K_DOWN:
                down_holding = False
            if event.key == pygame.K_LEFT:
                left_holding = False
            if event.key == pygame.K_RIGHT:
                right_holding = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if lmb_holding == False:
                    if not hud_active or not (
                            event.pos[0] < 40 * hud_dec_sc and event.pos[1] > window_height - 16 * hud_dec_sc):
                        lmb_holding = True
                        lmb_hold_ax, lmb_hold_ay = m2w(event.pos[0], event.pos[1])
                    else:
                        pass
                if lmb_holding == True:
                    lmb_hold_bx, lmb_hold_by = m2w(event.pos[0], event.pos[1])
            if event.button == 3:
                if not hud_active or not (
                        event.pos[0] < 40 * hud_dec_sc and event.pos[1] > window_height - 16 * hud_dec_sc):
                    if selected_team and len(selected):
                        ground = True
                        res = False
                        mx, my = m2w(event.pos[0], event.pos[1])
                        target = False
                        for ent in entities:
                            if between(ent.x, mx + 0.1, mx - 0.1) and between(ent.y, my + 0.1, my - 0.1):
                                if ent.entity_type == "unit":
                                    if ent.unit_team != player_team:
                                        target = ent
                                        ground = False
                                        res = False
                                if ent.entity_type == "resource":
                                    target = ent
                                    ground = False
                                    res = True
                        if ground:
                            for sel in selected:
                                sel.target = dict()
                                sel.target["pos"] = m2w(event.pos[0], event.pos[1])
                                sel.target["type"] = "go"
                        elif res:
                            for sel in selected:
                                if sel.unit_class == "villager":
                                    sel.target = dict()
                                    sel.target["ent"] = target
                                    sel.target["type"] = "gather"
                                else:
                                    sel.target = dict()
                                    sel.target["pos"] = m2w(event.pos[0], event.pos[1])
                                    sel.target["type"] = "go"
                        else:
                            for sel in selected:
                                sel.target = dict()
                                sel.target["ent"] = target
                                sel.target["type"] = "attack"

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                select_area(lmb_hold_ax, lmb_hold_ay, lmb_hold_bx, lmb_hold_by)
                lmb_holding = False
    if lmb_holding:
        lmb_hold_bx, lmb_hold_by = m2w(mouse_x, mouse_y)

    # SCREEN SCROLL KEYED
    if up_holding:
        camera_pos_y -= 0.005 * dt * camera_size_y
    if down_holding:
        camera_pos_y += 0.005 * dt * camera_size_y
    if left_holding:
        camera_pos_x -= 0.005 * dt * camera_size_x
    if right_holding:
        camera_pos_x += 0.005 * dt * camera_size_x

    # SCREEN SCROLL MOUSE
    if mouse_y < window_height * 0.05:
        camera_pos_y -= 0.0005 * dt * camera_size_y
    if mouse_y > window_height * 0.95:
        camera_pos_y += 0.0005 * dt * camera_size_y
    if mouse_x < window_width * 0.05:
        camera_pos_x -= 0.0005 * dt * camera_size_x
    if mouse_x > window_width * 0.95:
        camera_pos_x += 0.0005 * dt * camera_size_x

    if camera_pos_y - camera_size_y / 2 < -16:
        camera_pos_y = camera_size_y / 2 - 16
    if camera_pos_y + camera_size_y / 2 > 16 + map_size_y * 16:
        camera_pos_y = map_size_y * 16 - camera_size_y / 2 + 16
    if camera_pos_x - camera_size_x / 2 < -16:
        camera_pos_x = camera_size_x / 2 - 16
    if camera_pos_x + camera_size_x / 2 > 16 + map_size_x * 16:
        camera_pos_x = map_size_x * 16 - camera_size_x / 2 + 16


def draw_ground():
    camera_area = pygame.Rect((4 + camera_pos_x - camera_size_x / 2, 4 + camera_pos_y - camera_size_y / 2),
                              (4 + camera_size_x, 4 + camera_size_y))
    camera_ground = pygame.Surface((camera_size_x, camera_size_y), flags=pygame.SRCALPHA)

    camera_ground.blit(ground_surface, (0, 0), camera_area)

    ground_set.load("k", camera_ground)
    img = oglf.GL_Image(ground_set, "k")
    img.draw(abspos=(0, window_height), width=window_width, height=-window_height)


def draw_entities():
    global target_frame
    entities_by_y = sorted(entities, key=get_y)
    scale_x = int(16 * window_width // camera_size_x)
    scale_y = int(16 * window_height // camera_size_y)
    for ent in entities_by_y:
        mx, my = w2m(ent.x, ent.y)
        if in_rect(mx, my, -scale_x * 2, -scale_y * 2, window_width + scale_x * 2, window_height + scale_y * 2):
            if ent.entity_type == "unit":
                img = oglf.GL_Image(shadow_set, "shadow")
                img.draw(abspos=w2m(ent.x - 0.25, ent.y + 0.2), width=scale_x / 16 * 8, height=-scale_y / 16 * 5)

    for ent in entities_by_y:
        mx, my = w2m(ent.x, ent.y)
        ent.animation_frame %= len(ani_standard[ent.animation])
        if in_rect(mx, my, -scale_x * 2, -scale_y * 2, window_width + scale_x * 2, window_height + scale_y * 2):
            if ent.entity_type == "unit":
                img = oglf.GL_Image(sprites[ent.unit_team + ent.unit_class], ent.animation + str(ent.animation_frame))
                img.draw(abspos=w2m(ent.x - 0.5, ent.y + 0.2), width=scale_x, height=-scale_y)
        if not logic_frame % 10:
            if ent.animation in ("idle_s", "idle_w", "idle_n", "idle_e") and ent.animation_frame == 0:
                if not logic_frame % 200:
                    ent.animation_frame = (ent.animation_frame + 1) % len(ani_standard[ent.animation])
            elif ent.animation in (
            "build_s", "build_w", "build_n", "build_e", "attack_s", "attack_w", "attack_n", "attack_e"):
                if not logic_frame % 50:
                    ent.animation_frame = (ent.animation_frame + 1) % len(ani_standard[ent.animation])
            else:
                ent.animation_frame = (ent.animation_frame + 1) % len(ani_standard[ent.animation])

    for ent in entities_by_y:
        mx, my = w2m(ent.x, ent.y)
        if in_rect(mx, my, -scale_x * 2, -scale_y * 2, window_width + scale_x * 2, window_height + scale_y * 2):
            if ent.entity_type == "unit":
                if ent in selected or ent.unit_health != unit_stats[ent.unit_team][ent.unit_class]["max_hp"]:
                    img1 = oglf.GL_Image(hud_set, "health_green")
                    img2 = oglf.GL_Image(hud_set, "health_red")
                    health = ent.unit_health / unit_stats[ent.unit_team][ent.unit_class]["max_hp"]
                    img2.draw(abspos=w2m(ent.x - 0.25, ent.y - 0.75), width=scale_x / 16 * 8,
                              height=-1 - scale_y / 16 * 1)
                    img1.draw(abspos=w2m(ent.x - 0.25, ent.y - 0.75), width=scale_x / 16 * 8 * health,
                              height=-1 - scale_y / 16 * 1)
        if ent.target is not None and ent.unit_team == player_team and ent in selected:
            if ent.target["type"] == "go":
                img_t = oglf.GL_Image(hud_set, "target" + str(target_frame))
                img_t.draw(abspos=w2m(ent.target["pos"][0] - 0.25, ent.target["pos"][1] + 0.2), width=scale_x / 16 * 8,
                           height=-scale_y / 16 * 8)
            if ent.target["type"] in ("attack", "gather"):
                img_t = oglf.GL_Image(hud_set, "target" + str(target_frame))
                tar = ent.target["ent"]
                img_t.draw(abspos=w2m(tar.x - 0.25, tar.y + 0.2), width=scale_x / 16 * 8, height=-scale_y / 16 * 8)
    if not logic_frame % 30:
        target_frame = (target_frame + 1) % 4


def draw_hud():
    global hud_scalar, hud_dec_sc
    global game_console, hud_active

    # console
    for num, mes in enumerate(game_console):
        if mes.date + 200 >= logic_frame and mes.date != -1:
            game_console.pop(num)
        else:
            draw_text(mes.message, 0, 50 - num)
    # selecting rectangle
    if lmb_holding:
        sel = oglf.GL_Image(hud_set, "selecting_rectangle")
        ax, ay = w2m(lmb_hold_ax, lmb_hold_ay)
        bx, by = w2m(lmb_hold_bx, lmb_hold_by)
        sel.draw(abspos=(ax, ay), width=bx - ax, height=by - ay)

    # bottom hud
    hud_active = True if (selected and selected_team) else False
    if hud_active:
        bottom_container = oglf.GL_Image(hud_set, "bottom_container")
        bottom_container.draw(abspos=(0, window_height), height=-16 * hud_dec_sc)
        if len(selected_types) == 1:
            sel = selected[0]
            if sel.entity_type == "unit":
                portrait = oglf.GL_Image(hud_set, "portrait_" + sel.unit_team + "_" + sel.unit_class)
                portrait.draw(abspos=(2 * hud_dec_sc, window_height - 6 * hud_dec_sc), height=-6 * hud_dec_sc,
                              width=6 * hud_dec_sc)
                draw_text(sel.unit_class.capitalize(), 2, 14)

                draw_icon("attack", 8, 10)
                draw_text(unit_stats[sel.unit_team][sel.unit_class]["attack"], 10, 12)
                draw_icon("defence", 8, 8)
                draw_text(unit_stats[sel.unit_team][sel.unit_class]["defence"], 10, 10)
                if sel.unit_class == "villager":
                    if sel.carry_type != "none":
                        draw_icon(sel.carry_type, 8, 6)
                        draw_text(
                            str(sel.carry_amount) + "/" + str(unit_stats[sel.unit_team][sel.unit_class]["max_carry"]),
                            10, 8)
                if len(selected) > 1:
                    draw_text(len(selected), 2, 12)
                if DEBUG:
                    draw_text(str(sel.entity_id), 20, 2)
                    draw_text(str(sel.x), 20, 4)
                    draw_text(str(sel.y), 20, 6)

        if len(selected_types) > 1:
            type_nr = 0
            for sel_type, sel_amount in selected_types.items():
                portrait = oglf.GL_Image(hud_set, "portrait_" + player_team + "_" + sel_type)
                portrait.draw(abspos=((2 + type_nr * 8) * hud_dec_sc, window_height - 6 * hud_dec_sc),
                              height=-6 * hud_dec_sc, width=6 * hud_dec_sc)
                draw_text(sel_amount, (2 + type_nr * 8), 12)
                type_nr += 1
                if type_nr == 5: break


def draw_screen():
    global graphic_frame
    img = oglf.GL_Image(black_set, "black")
    img.draw(abspos=(0, window_height), width=100000, height=-100000)

    draw_ground()
    draw_entities()
    draw_hud()
    if DEBUG:
        fps_surface = font_console.render(str(1000 / dt)[:2], True, (255, 0, 0))
        fps_set.load("fps", fps_surface)
        fps = oglf.GL_Image(fps_set, "fps")
        fps.draw(abspos=(20, 40), height=-fps_surface.get_height())
    graphic_frame += 1
    pygame.display.flip()


def logic_tick():
    global logic_frame
    for ent in entities:
        speed = unit_stats[ent.unit_team][ent.unit_class]["speed"] * 0.01
        if ent.target is not None:
            colliding = False
            target_type = ent.target["type"]
            if target_type == "go":
                target_x, target_y = ent.target["pos"]

                travel_x, travel_y = min(speed, max(-speed, target_x - ent.x)), min(speed, max(-speed, target_y - ent.y))
                for col in entities:
                    if between(col.x, ent.x + travel_x + 0.2, ent.x + travel_x - 0.2) and between(col.y, ent.y + travel_y - 0.2, ent.y + travel_y + 0.2) and col != ent:
                        colliding = True
                if not colliding:
                    ent.animate_walk(travel_x, travel_y)
                    ent.x += travel_x
                    ent.y += travel_y
                    if (ent.x, ent.y) == ent.target["pos"]:
                        ent.animate_walk(0, 0)
                        ent.target = None
                if colliding:
                    ent.animate_walk(0, 0)
            if target_type == "attack":
                tar = ent.target["ent"]
                if abs(tar.x - ent.x) > speed * 16 or abs(tar.y - ent.y) > speed * 16:
                    travel_x, travel_y = min(speed, max(-speed, tar.x - ent.x)), min(speed, max(-speed, tar.y - ent.y))
                    for col in entities:
                        if between(col.x, ent.x + travel_x + 0.2, ent.x + travel_x - 0.2) and between(col.y,ent.y + travel_y - 0.2, ent.y + travel_y + 0.2) and col != ent and col !=ent.target["ent"]:
                            colliding = True
                    if not colliding:
                        ent.animate_walk(travel_x, travel_y)
                        ent.x += travel_x
                        ent.y += travel_y
                else:
                    ent.animate_attack(tar.x - ent.x, tar.y - ent.y)
                    if not logic_frame % 100:
                        dead = attack(ent, tar)
                        if dead:
                            ent.animate_walk(tar.x - ent.x, tar.y - ent.y)
                            ent.animate_walk(0, 0)
                            ent.target = None

    logic_frame += 1


game_running = True

for num, ani in enumerate(ani_standard):
    vil = DEBUG_spawn_villager(20 + num * 3, 20)
    vil.animation = ani
    vil.carry_type = "wood"
    vil.carry_amount = 4
    if num % 2 == 0:
        vil.unit_team = "red"
    if num == 4:
        vil.unit_class = "knight"

selected = [entities[0]]

while game_running:
    dt = clock.tick(120)

    handle_input()
    draw_screen()
    logic_tick()
