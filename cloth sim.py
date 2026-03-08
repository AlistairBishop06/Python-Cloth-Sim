"""
Cloth Simulation
----------------
Click and drag to grab and move the cloth in any direction.
Right-click to pin/unpin points.
Press R to reset.
Press G to toggle gravity.
"""

import pygame
import math

# ── Config ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT   = 900, 700
FPS             = 60
CLOTH_COLS      = 30
CLOTH_ROWS      = 22
SPACING         = 22
CLOTH_ORIGIN_X  = (WIDTH  - CLOTH_COLS * SPACING) // 2
CLOTH_ORIGIN_Y  = 60
GRAVITY         = 0.5
DAMPING         = 0.98
CONSTRAINT_ITER = 8           # more iterations = stiffer cloth / better drag propagation
TEAR_DISTANCE   = SPACING * 2.8
GRAB_RADIUS     = 36          # how close you need to click to grab

# Colours
BG_COLOR        = (15,  15,  20)
CLOTH_COLOR     = (220, 200, 170)
PINNED_COLOR    = (255, 120,  60)
GRAB_COLOR      = (100, 200, 255)
HIGHLIGHT_COLOR = (255, 230, 100)
LINK_WIDTH      = 1


# ── Point ────────────────────────────────────────────────────────────────────
class Point:
    __slots__ = ("x", "y", "px", "py", "pinned")

    def __init__(self, x, y, pinned=False):
        self.x  = float(x)
        self.y  = float(y)
        self.px = float(x)
        self.py = float(y)
        self.pinned = pinned

    def update(self, gravity):
        if self.pinned:
            return
        vx = (self.x - self.px) * DAMPING
        vy = (self.y - self.py) * DAMPING
        self.px, self.py = self.x, self.y
        self.x += vx
        self.y += vy + gravity

    def constrain_bounds(self):
        if self.pinned:
            return
        if self.y > HEIGHT - 2:
            self.y  = HEIGHT - 2
            self.py = self.y + (self.y - self.py) * 0.5
        if self.x < 0:
            self.x  = 0
            self.px = self.x - (self.px - self.x) * 0.5
        if self.x > WIDTH:
            self.x  = WIDTH
            self.px = self.x - (self.px - self.x) * 0.5


# ── Link ─────────────────────────────────────────────────────────────────────
class Link:
    __slots__ = ("p1", "p2", "rest_len", "active")

    def __init__(self, p1, p2):
        self.p1       = p1
        self.p2       = p2
        self.rest_len = math.hypot(p2.x - p1.x, p2.y - p1.y)
        self.active   = True

    def resolve(self):
        if not self.active:
            return
        dx   = self.p2.x - self.p1.x
        dy   = self.p2.y - self.p1.y
        dist = math.hypot(dx, dy) or 1e-6

        if dist > TEAR_DISTANCE:
            self.active = False
            return

        diff   = (dist - self.rest_len) / dist * 0.5
        ox, oy = dx * diff, dy * diff

        if not self.p1.pinned:
            self.p1.x += ox
            self.p1.y += oy
        if not self.p2.pinned:
            self.p2.x -= ox
            self.p2.y -= oy


# ── Cloth builder ─────────────────────────────────────────────────────────────
def build_cloth():
    points, links = [], []

    for row in range(CLOTH_ROWS):
        for col in range(CLOTH_COLS):
            x      = CLOTH_ORIGIN_X + col * SPACING
            y      = CLOTH_ORIGIN_Y + row * SPACING
            pinned = (row == 0) and (col % 3 == 0)
            points.append(Point(x, y, pinned=pinned))

    for row in range(CLOTH_ROWS):
        for col in range(CLOTH_COLS):
            idx = row * CLOTH_COLS + col
            if col < CLOTH_COLS - 1:
                links.append(Link(points[idx], points[idx + 1]))
            if row < CLOTH_ROWS - 1:
                links.append(Link(points[idx], points[idx + CLOTH_COLS]))

    return points, links


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cloth Simulation  •  drag to grab  •  R=reset  G=gravity  RMB=pin")
    font   = pygame.font.SysFont("consolas", 17)
    tick   = pygame.time.Clock()

    points, links = build_cloth()

    grabbed    = None   # the Point currently being dragged
    gravity_on = True

    def find_closest(mx, my):
        best, best_d = None, GRAB_RADIUS * GRAB_RADIUS
        for p in points:
            d = (p.x - mx) ** 2 + (p.y - my) ** 2
            if d < best_d:
                best, best_d = p, d
        return best

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    points, links = build_cloth()
                    grabbed = None
                elif event.key == pygame.K_g:
                    gravity_on = not gravity_on

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    grabbed = find_closest(mx, my)
                elif event.button == 3:
                    p = find_closest(mx, my)
                    if p:
                        p.pinned = not p.pinned

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    grabbed = None

        grav = GRAVITY if gravity_on else 0.0

        # KEY FIX: teleport the grabbed point directly to the mouse each frame,
        # then zero its stored previous-position so it has no residual velocity.
        # The constraint solver then pulls the surrounding cloth naturally.
        if grabbed is not None and not grabbed.pinned:
            grabbed.x  = float(mx)
            grabbed.y  = float(my)
            grabbed.px = float(mx)
            grabbed.py = float(my)

        # Physics
        for p in points:
            p.update(grav)

        # Re-anchor grab after physics so gravity can't fight it
        if grabbed is not None and not grabbed.pinned:
            grabbed.x  = float(mx)
            grabbed.y  = float(my)
            grabbed.px = float(mx)
            grabbed.py = float(my)

        for _ in range(CONSTRAINT_ITER):
            for lk in links:
                lk.resolve()
            # Keep the grab locked during constraint iterations too
            if grabbed is not None and not grabbed.pinned:
                grabbed.x = float(mx)
                grabbed.y = float(my)

        for p in points:
            p.constrain_bounds()

        # ── Render ──────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)

        for lk in links:
            if not lk.active:
                continue
            dx   = lk.p2.x - lk.p1.x
            dy   = lk.p2.y - lk.p1.y
            dist = math.hypot(dx, dy)
            t    = max(0.0, min(1.0, dist / lk.rest_len - 1.0))
            r = int(CLOTH_COLOR[0] + (255 - CLOTH_COLOR[0]) * t * 0.6)
            g = int(CLOTH_COLOR[1] - CLOTH_COLOR[1] * t * 0.5)
            b = int(CLOTH_COLOR[2] - CLOTH_COLOR[2] * t * 0.5)
            pygame.draw.line(screen,
                             (max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b))),
                             (int(lk.p1.x), int(lk.p1.y)),
                             (int(lk.p2.x), int(lk.p2.y)), LINK_WIDTH)

        for p in points:
            if p.pinned:
                pygame.draw.circle(screen, PINNED_COLOR, (int(p.x), int(p.y)), 4)

        if grabbed is None:
            for p in points:
                d2 = (p.x - mx) ** 2 + (p.y - my) ** 2
                if d2 < GRAB_RADIUS ** 2:
                    pygame.draw.circle(screen, HIGHLIGHT_COLOR, (int(p.x), int(p.y)), 3)

        if grabbed is not None:
            pygame.draw.circle(screen, GRAB_COLOR, (int(grabbed.x), int(grabbed.y)), 6)

        grav_txt = "ON " if gravity_on else "OFF"
        hud = [
            "LMB drag  — grab & move cloth",
            "RMB click — pin / unpin point",
            f"G — gravity {grav_txt}",
            "R — reset",
        ]
        for i, line in enumerate(hud):
            surf = font.render(line, True, (130, 130, 160))
            screen.blit(surf, (12, HEIGHT - 18 - i * 20))

        pygame.display.flip()
        tick.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()