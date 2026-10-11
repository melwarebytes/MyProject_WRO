import pygame
import random
import math
import time

WIDTH, HEIGHT = 800, 560
FPS = 60
BG = (30, 35, 25)
HUD_H = 40

# Player tuning
SPEED = 4
PLAYER_MAX_HP = 3
INVINCIBLE_MS = 1500        # invincibility window after taking a hit
CLIP_SIZE = 12
RELOAD_MS = 2000            # reload duration

# Barrel tuning
BARREL_COUNT = 4
BARREL_SIZE = 26
EXPLOSION_RADIUS = 120
EXPLOSION_MS = 400          # how long the blast effect stays on screen


# --------------------------------------------------------------------------
# Zombies
# --------------------------------------------------------------------------
class Zombie:
    """Standard zombie. Subclasses override the class-level stats."""
    SPEED = 1.5
    HP = 3
    SIZE = 30
    COLOR = (60, 140, 60)
    EYE = (200, 40, 40)

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        # Float position so slow speeds / shallow angles aren't truncated to 0
        self.fx, self.fy = float(x), float(y)
        self.hp = self.HP
        self.frame = random.randint(0, 100)
        self.flash = 0

    def update(self, player_pos):
        px, py = player_pos
        cx, cy = self.fx + self.SIZE / 2, self.fy + self.SIZE / 2
        dx, dy = px - cx, py - cy
        dist = math.hypot(dx, dy)
        if dist:
            self.fx += dx / dist * self.SPEED
            self.fy += dy / dist * self.SPEED
            self.rect.x, self.rect.y = round(self.fx), round(self.fy)
        self.frame += 1
        if self.flash > 0:
            self.flash -= 1

    def hit(self):
        self.hp -= 1
        self.flash = 5
        return self.hp <= 0

    def draw(self, screen):
        wobble_y = int(math.sin(self.frame * 0.2) * 3)
        r = self.rect.move(0, wobble_y)
        color = (255, 255, 255) if self.flash else self.COLOR
        pygame.draw.rect(screen, color, r, border_radius=5)
        eye_r = max(3, self.SIZE // 8)
        for ex in (r.x + self.SIZE // 4, r.x + self.SIZE * 3 // 4):
            pygame.draw.circle(screen, self.EYE, (ex, r.y + self.SIZE // 3), eye_r)
        if self.HP > 1 and self.hp < self.HP:      # health bar once damaged
            w = int(self.SIZE * self.hp / self.HP)
            pygame.draw.rect(screen, (60, 0, 0), (r.x, r.y - 7, self.SIZE, 4))
            pygame.draw.rect(screen, (220, 60, 60), (r.x, r.y - 7, w, 4))


class FastZombie(Zombie):
    SPEED = 3.0
    HP = 1
    SIZE = 20
    COLOR = (170, 190, 60)
    EYE = (255, 240, 80)


class TankZombie(Zombie):
    SPEED = 0.8
    HP = 6
    SIZE = 46
    COLOR = (40, 90, 50)
    EYE = (255, 90, 30)


def pick_zombie_type(wave):
    """Mix of types; specials become more common in later waves."""
    fast_w = min(10 + wave * 5, 35)
    tank_w = min(5 + wave * 4, 25)
    normal_w = 100 - fast_w - tank_w
    return random.choices([Zombie, FastZombie, TankZombie],
                          weights=[normal_w, fast_w, tank_w])[0]


def spawn_zombie(width, height, player_rect, wave=1, kind=None, margin=160):
    kind = kind or pick_zombie_type(wave)
    s = kind.SIZE
    while True:
        x = random.randint(0, width - s)
        y = random.randint(HUD_H, height - s)
        rect = pygame.Rect(x, y, s, s)
        if not rect.colliderect(player_rect.inflate(margin, margin)):
            return kind(x, y)


# --------------------------------------------------------------------------
# Barrels
# --------------------------------------------------------------------------
class Barrel:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BARREL_SIZE, BARREL_SIZE + 6)

    def draw(self, screen):
        r = self.rect
        pygame.draw.rect(screen, (170, 50, 30), r, border_radius=4)
        pygame.draw.line(screen, (90, 25, 15), (r.x, r.y + 8), (r.right - 1, r.y + 8), 2)
        pygame.draw.line(screen, (90, 25, 15), (r.x, r.bottom - 9), (r.right - 1, r.bottom - 9), 2)
        pygame.draw.circle(screen, (240, 200, 40), r.center, 5)


class Explosion:
    def __init__(self, center):
        self.center = center
        self.start = pygame.time.get_ticks()

    def alive(self, now):
        return now - self.start < EXPLOSION_MS

    def draw(self, screen, now):
        t = (now - self.start) / EXPLOSION_MS
        radius = int(EXPLOSION_RADIUS * (0.3 + 0.7 * t))
        alpha = int(200 * (1 - t))
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 140, 30, alpha), (radius, radius), radius)
        pygame.draw.circle(surf, (255, 240, 120, alpha), (radius, radius), radius // 2)
        screen.blit(surf, (self.center[0] - radius, self.center[1] - radius))


def place_barrels(player_rect, count=BARREL_COUNT):
    barrels = []
    while len(barrels) < count:
        x = random.randint(40, WIDTH - 40 - BARREL_SIZE)
        y = random.randint(HUD_H + 30, HEIGHT - 40 - BARREL_SIZE)
        b = Barrel(x, y)
        if b.rect.colliderect(player_rect.inflate(200, 200)):
            continue
        if any(b.rect.inflate(120, 120).colliderect(o.rect) for o in barrels):
            continue
        barrels.append(b)
    return barrels


# --------------------------------------------------------------------------
# Player
# --------------------------------------------------------------------------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = (60, 160, 220)
        self.bullets = []          # each bullet: [x, y, vx, vy]
        self.shoot_cooldown = 0
        # Health
        self.hp = PLAYER_MAX_HP
        self.invincible_until = 0
        # Ammo
        self.ammo = CLIP_SIZE
        self.reload_until = 0      # 0 = not reloading

    # --- state helpers ---
    def is_invincible(self, now):
        return now < self.invincible_until

    def is_reloading(self):
        return self.reload_until != 0

    def reload_left_ms(self, now):
        return max(0, self.reload_until - now) if self.is_reloading() else 0

    def take_hit(self, now):
        """Returns True if the hit actually landed."""
        if self.is_invincible(now) or self.hp <= 0:
            return False
        self.hp -= 1
        self.invincible_until = now + INVINCIBLE_MS
        return True

    def start_reload(self, now):
        if not self.is_reloading() and self.ammo < CLIP_SIZE:
            self.reload_until = now + RELOAD_MS

    def update_reload(self, now):
        if self.is_reloading() and now >= self.reload_until:
            self.ammo = CLIP_SIZE
            self.reload_until = 0

    # --- movement / shooting ---
    def move(self, keys, width, height):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = SPEED
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x + dx))
        self.rect.y = max(HUD_H, min(height - self.rect.height, self.rect.y + dy))
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self, target_pos, now):
        if self.shoot_cooldown > 0 or self.is_reloading():
            return
        if self.ammo <= 0:
            self.start_reload(now)
            return
        cx, cy = self.rect.center
        tx, ty = target_pos
        dx, dy = tx - cx, ty - cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        self.bullets.append([cx, cy, dx / dist * 10, dy / dist * 10])
        self.ammo -= 1
        self.shoot_cooldown = 15
        if self.ammo == 0:          # auto-reload when the clip runs dry
            self.start_reload(now)

    def update_bullets(self, width, height):
        live = []
        for b in self.bullets:
            b[0] += b[2]; b[1] += b[3]
            if 0 <= b[0] <= width and 0 <= b[1] <= height:
                live.append(b)
        self.bullets = live

    def draw(self, screen, now):
        # Blink while invincible
        if not (self.is_invincible(now) and (now // 100) % 2 == 0):
            pygame.draw.rect(screen, self.color, self.rect, border_radius=6)
            if self.is_invincible(now):
                pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=6)
        for b in self.bullets:
            pygame.draw.circle(screen, (255, 220, 60), (int(b[0]), int(b[1])), 5)


# --------------------------------------------------------------------------
# Game
# --------------------------------------------------------------------------
class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zombie Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 20, bold=True)
        self.small_font = pygame.font.SysFont("monospace", 14)
        self.big_font = pygame.font.SysFont("monospace", 44, bold=True)
        self.reset()

    def reset(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.wave = 1
        self.kills = 0                 # kills this wave
        self.total_kills = 0
        self.kill_points = 0
        self.kills_to_next = 8
        self.zombies = [spawn_zombie(WIDTH, HEIGHT, self.player.rect, self.wave, Zombie)
                        for _ in range(4)]
        self.barrels = place_barrels(self.player.rect)
        self.explosions = []
        self.score = 0
        self.spawn_timer = 0
        self.game_over = False
        self.start_time = time.time()

    def handle_events(self):
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.game_over:
                self.player.shoot(event.pos, now)
        return True

    def register_kill(self, z):
        if z in self.zombies:
            self.zombies.remove(z)
            self.kills += 1
            self.total_kills += 1
            self.kill_points += 10

    def explode(self, barrel):
        center = barrel.rect.center
        self.explosions.append(Explosion(center))
        for z in self.zombies[:]:
            if math.dist(center, z.rect.center) <= EXPLOSION_RADIUS:
                self.register_kill(z)

    def update_spawning(self):
        """Keep enough zombies coming so the wave's kill target is reachable."""
        max_alive = 4 + self.wave * 2
        self.spawn_timer -= 1
        if (self.spawn_timer <= 0 and len(self.zombies) < max_alive
                and self.kills + len(self.zombies) < self.kills_to_next):
            self.zombies.append(spawn_zombie(WIDTH, HEIGHT, self.player.rect, self.wave))
            self.spawn_timer = max(20, 70 - self.wave * 5)

    def update(self):
        if self.game_over: return
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        self.player.move(keys, WIDTH, HEIGHT)
        self.player.update_reload(now)
        self.player.update_bullets(WIDTH, HEIGHT)

        # Zombies move and hurt the player
        for z in self.zombies:
            z.update(self.player.rect.center)
            if z.rect.colliderect(self.player.rect):
                self.player.take_hit(now)
        if self.player.hp <= 0:
            self.game_over = True

        # Bullet collisions (barrels first, then zombies). Each bullet hits once.
        for b in self.player.bullets[:]:
            bx, by = int(b[0]), int(b[1])
            hit = False
            for barrel in self.barrels[:]:
                if barrel.rect.collidepoint(bx, by):
                    self.barrels.remove(barrel)
                    self.explode(barrel)
                    hit = True
                    break
            if not hit:
                for z in self.zombies:
                    if z.rect.collidepoint(bx, by):
                        if z.hit():
                            self.register_kill(z)
                        hit = True
                        break
            if hit and b in self.player.bullets:
                self.player.bullets.remove(b)

        self.explosions = [e for e in self.explosions if e.alive(now)]

        # Score = seconds survived + kill bonus (bonus no longer overwritten)
        self.score = int(time.time() - self.start_time) + self.kill_points

        # Wave progression
        if self.kills >= self.kills_to_next:
            self.kills = 0
            self.wave += 1
            self.kills_to_next = 8 + self.wave * 2
            for _ in range(self.wave + 3):
                self.zombies.append(spawn_zombie(WIDTH, HEIGHT, self.player.rect, self.wave))
        self.update_spawning()

    def draw_hud(self, now):
        pygame.draw.rect(self.screen, (15, 20, 15), (0, 0, WIDTH, HUD_H))
        x = 10
        # Hearts
        for i in range(PLAYER_MAX_HP):
            col = (220, 50, 60) if i < self.player.hp else (70, 40, 40)
            cx = x + i * 26 + 10
            pygame.draw.circle(self.screen, col, (cx - 4, 16), 6)
            pygame.draw.circle(self.screen, col, (cx + 4, 16), 6)
            pygame.draw.polygon(self.screen, col, [(cx - 10, 18), (cx + 10, 18), (cx, 30)])
        x += PLAYER_MAX_HP * 26 + 14

        # Ammo
        if self.player.is_reloading():
            secs = self.player.reload_left_ms(now) / 1000
            ammo_txt, ammo_col = f"RELOADING {secs:.1f}s", (255, 170, 60)
        else:
            ammo_txt = f"AMMO {self.player.ammo:2d}/{CLIP_SIZE}"
            ammo_col = (230, 210, 90) if self.player.ammo > 3 else (255, 100, 80)
        t = self.font.render(ammo_txt, True, ammo_col)
        self.screen.blit(t, (x, 10))
        x += 200

        info = self.font.render(
            f"Wave {self.wave}  Score {self.score}  Kills {self.kills}/{self.kills_to_next}",
            True, (160, 220, 120))
        self.screen.blit(info, (x, 10))

        hint = self.small_font.render("WASD move  |  Click shoot  |  R restart", True, (120, 140, 110))
        self.screen.blit(hint, (WIDTH - hint.get_width() - 8, HEIGHT - 20))

    def draw(self):
        now = pygame.time.get_ticks()
        self.screen.fill(BG)
        for x in range(0, WIDTH, 60):
            pygame.draw.line(self.screen, (40, 45, 35), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 60):
            pygame.draw.line(self.screen, (40, 45, 35), (0, y), (WIDTH, y), 1)
        for b in self.barrels: b.draw(self.screen)
        for z in self.zombies: z.draw(self.screen)
        self.player.draw(self.screen, now)
        for e in self.explosions: e.draw(self.screen, now)
        self.draw_hud(now)

        if self.game_over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            self.screen.blit(ov, (0, 0))
            m = self.big_font.render("DEVOURED!", True, (180, 40, 40))
            s = self.font.render(
                f"Wave {self.wave} | Score {self.score} | Kills {self.total_kills} | Press R",
                True, (200, 200, 200))
            self.screen.blit(m, (WIDTH // 2 - m.get_width() // 2, HEIGHT // 2 - 40))
            self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    engine = GameEngine()
    engine.run()
