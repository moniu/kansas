class Entity:
    def __init__(self, entity_id, entity_type, x, y):
        self.entity_type = entity_type if entity_type else "error"
        self.pos = (x, y)
        self.x = x
        self.y = y
        self.entity_id = entity_id


class Unit(Entity):
    def __init__(self, entity_id, x, y, unit_class, unit_team, target=None, unit_health=20):
        Entity.__init__(self, entity_id, "unit", x, y)
        self.unit_class = unit_class
        self.unit_team = unit_team
        self.target = target
        self.unit_health = unit_health
        self.prev_pos = self.prev_x, self.prev_y = x, y
        self.animation = "idle_s"
        self.animation_frame = 0
        self.dead = False

    def animate_walk(self, x, y):
        if x == 0 and y == 0:
            if self.animation == "walk_n": self.animation = "idle_n"
            elif self.animation == "walk_e": self.animation = "idle_e"
            elif self.animation == "walk_w": self.animation = "idle_w"
            elif self.animation == "walk_s": self.animation = "idle_s"
            elif self.animation in ("idle_s", "idle_n", "idle_w", "idle_e"):
                pass
            else:
                self.animation = "idle_s"
            self.animation_frame = 0
            return self.animation
        if abs(y) >= abs(x):
            if y > 0:
                self.animation = "walk_s"
            else:
                self.animation = "walk_n"
        else:
            if x > 0:
                self.animation = "walk_e"
            else:
                self.animation = "walk_w"
        return self.animation

    def animate_attack(self, x, y):
        if x == 0 and y == 0:
            if self.animation == "walk_n":
                self.animation = "attack_n"
            elif self.animation == "walk_e":
                self.animation = "attack_e"
            elif self.animation == "walk_w":
                self.animation = "attack_w"
            elif self.animation == "walk_s":
                self.animation = "attack_s"
            elif self.animation in ("attack_s", "attack_n", "attack_w", "attack_e"):
                pass
            else:
                self.animation = "attack_s"
            self.animation_frame = 0
            return self.animation
        if abs(y) >= abs(x):
            if y > 0:
                self.animation = "attack_s"
            else:
                self.animation = "attack_n"
        else:
            if x > 0:
                self.animation = "attack_e"
            else:
                self.animation = "attack_w"
        return self.animation


class UnitVillager(Unit):
    def __init__(self, entity_id, x, y, unit_team, target=None, unit_health=20):
        Unit.__init__(self, entity_id, x, y, "villager", unit_team, target, unit_health)
        self.carry_type = "none"
        self.carry_amount = 0


